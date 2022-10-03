from django.db.models import Sum, QuerySet
from django.db import transaction
from django.utils.datetime_safe import datetime
from django.utils import timezone
from django_auto_prefetching import AutoPrefetchViewSetMixin
from django_filters.rest_framework import DjangoFilterBackend
from notifications.signals import notify
from notifications.models import Notification
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status, serializers, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, ValidationError
from silk.profiling.profiler import silk_profile

from relief.models import User, ResidentProfile, DonorProfile, Supply, ItemType, ItemRequest, Transaction, \
    BarangayRequest, TransactionImage, BarangayProfile, Donation, EvacuationCenter, TransactionOrder, UserLocation, \
    RouteSuggestion, RouteNode, Fulfillment, Disaster, TransactionStub, Rating, AlgorithmExecution
from relief.pagination import SmallResultsSetPagination
from relief.permissions import IsOwnerOrReadOnly, IsProfileUserOrReadOnly
from relief.serializers import UserSerializer, ResidentSerializer, DonorSerializer, SupplySerializer, \
    ItemTypeSerializer, ItemRequestSerializer, TransactionSerializer, BarangayRequestSerializer, BarangaySerializer, \
    DonationSerializer, EvacuationCenterSerializer, TransactionOrderSerializer, UserLocationSerializer, \
    RouteSuggestionSerializer, NotificationSerializer, DisasterSerializer, TransactionStubSerializer, RatingSerializer, \
    RatingOnlySerializer, AlgorithmExecutionSerializer

# Guide: https://www.django-rest-framework.org/api-guide/viewsets/
# Filtering Guide: https://www.django-rest-framework.org/api-guide/filtering/
# TODO: Add permission classes
from relief.tasks import solo_algo_tests, algo_error_handler


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], name='Get Current User',
            permission_classes=[IsProfileUserOrReadOnly])
    def current_user(self, request, pk=None):
        if request.user.is_anonymous:
            return Response({"error": "Not logged in"}, 403)
        user_serializer = UserSerializer(request.user)
        return Response(user_serializer.data)

    @action(detail=False, methods=['get'], name='Get Current User Profile')
    def current_user_profile(self, request, pk=None):
        user = request.user
        if user.role == user.BARANGAY:
            profile_serializer = BarangaySerializer(BarangayProfile.objects.get(user=user))
            return Response(profile_serializer.data)
        if user.role == user.RESIDENT:
            profile_serializer = ResidentSerializer(ResidentProfile.objects.get(user=user))
            return Response(profile_serializer.data)
        if user.role == user.DONOR:
            profile_serializer = DonorSerializer(DonorProfile.objects.get(user=user),
                                                 context={'request': request}, )
            return Response(profile_serializer.data)
        else:
            raise ValidationError(detail="Invalid request")
        # TODO: Add admin

    # permission_classes=[IsProfileUserOrReadOnly]
    @action(detail=False, methods=['put', 'patch'], name='Upload Profile Picture')
    def upload_profile_picture(self, request, pk=None):
        user = request.user
        user.profile_picture = list(request.FILES.values())[0]  # Get first file
        user.save()
        return Response({'status': 'File uploaded'})

    @action(detail=True, methods=['get'], name='Get Most Recent Location')
    def get_most_recent_location(self, request, pk=None):
        requested_user = self.get_object()
        user_locations = UserLocation.objects.filter(user=requested_user)
        most_recent_location = user_locations.last()
        most_recent_location_serialized = UserLocationSerializer(most_recent_location)
        return Response(most_recent_location_serialized.data)

    @action(detail=False, methods=['get'], name='Get Own Most Recent Location')
    def get_own_most_recent_location(self, request, pk=None):
        if request.user.is_anonymous:
            return Response({"error": "Not logged in"}, 403)
        requested_user = request.user
        user_locations = UserLocation.objects.filter(user=requested_user)
        most_recent_location = user_locations.last()
        most_recent_location_serialized = UserLocationSerializer(most_recent_location)
        return Response(most_recent_location_serialized.data)


class UserLocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer

    def perform_create(self, serializer):
        serializer.save(time=datetime.now(), user=self.request.user)


class ResidentViewSet(viewsets.ModelViewSet):
    queryset = ResidentProfile.objects.all()
    serializer_class = ResidentSerializer

    # Can also be applied to views
    # def perform_create(self, serializer):
    #     serializer.save(owner=self.request.user)

    # def post(self, request, *args, **kwargs):
    #     file = request.data['file']
    #     profile = self.get_object()
    #     profile.gov_id = file
    #     profile.save()

    # permission_classes=[IsProfileUserOrReadOnly]
    @action(detail=False, methods=['put', 'patch'], name='Upload ID')
    def upload_id(self, request, pk=None):
        profile: ResidentProfile = ResidentProfile.objects.get(user=request.user)
        profile.gov_id = list(request.FILES.values())[0]  # Get first file
        profile.save()
        return Response({'status': 'File uploaded'})


class BarangayViewSet(viewsets.ModelViewSet):
    queryset = BarangayProfile.objects.all()
    serializer_class = BarangaySerializer

    # Can also be applied to views
    # def perform_create(self, serializer):
    #     serializer.save(owner=self.request.user)


class DonorViewSet(viewsets.ModelViewSet):
    queryset = DonorProfile.objects.all()
    serializer_class = DonorSerializer


class TransactionOrderViewSet(viewsets.ModelViewSet):
    queryset = TransactionOrder.objects.all()
    serializer_class = TransactionOrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if not is_many:
            return super(TransactionViewSet, self).create(request, *args, **kwargs)
        else:
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer=serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers, )


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, ]
    filterset_fields = ['donor', 'barangay_request', 'received', ]
    search_fields = ['donor__user__username', 'barangay_request__barangay__user__username',
                     'barangay_request__evacuation_center__name', ]
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['patch', 'put'], name='Quick Update status',
            permission_classes=[IsProfileUserOrReadOnly])
    def quick_update_status(self, request, pk=None):
        user = request.user
        transaction: Transaction = self.get_object()
        if user.role == User.BARANGAY:
            if transaction.received == Transaction.INCOMING:
                transaction.received = Transaction.RECEIVED
                # Create notification for Residents
                # TODO: Consider moving to a Transaction signal instead
                resident_profiles = ResidentProfile.objects.filter(barangay__user=user)
                resident_users = User.objects.filter(resident_profile__barangay__user=user)
                notif_verb = "Package Arrival"
                notif_message = 'The packages for evacuation center ' + \
                                transaction.barangay_request.evacuation_center.name + 'has arrived'
                notify.send(sender=user, recipient=resident_users, target=transaction,
                            verb=notif_verb, description=notif_message)

            elif transaction.received == Transaction.PACKAGING:
                raise ValidationError(detail="Order still being packaged")
            elif transaction.received == Transaction.RECEIVED:
                raise ValidationError(detail="Already received.")
        elif user.role == User.DONOR:
            if transaction.received == Transaction.INCOMING:
                raise ValidationError(detail="Already declared incoming")
            elif transaction.received == Transaction.PACKAGING:
                transaction.received = Transaction.INCOMING
            elif transaction.received == Transaction.RECEIVED:
                raise ValidationError(detail="Already received.")
        transaction.save()
        # return Response({"status": "Successful update"}, status=status.HTTP_200_OK)
        return Response(TransactionSerializer(transaction, context={'request': request}).data,
                        status=status.HTTP_200_OK, )

    @action(detail=True, methods=['patch', 'put'], name='Upload Transaction Picture',
            permission_classes=[IsProfileUserOrReadOnly, IsAuthenticated])
    def upload_image(self, request, pk=None):
        transaction: Transaction = self.get_object()
        new_image: TransactionImage = TransactionImage.objects.create()
        new_image.image = list(request.FILES.values())[0]  # Get first image uploaded
        new_image.transaction = transaction
        new_image.save()

    @action(detail=True, methods=['get'], name='Get Evacuation',
            permission_classes=[IsProfileUserOrReadOnly, IsAuthenticated])
    def evacuation_center(self, request, pk=None):
        current_transaction: Transaction = self.get_object()
        barangay_request: BarangayRequest = current_transaction.barangay_request
        serializer = EvacuationCenterSerializer(barangay_request.evacuation_center)
        return Response(serializer.data)

    def perform_create(self, serializer):
        current_donor = DonorProfile.objects.get(user=self.request.user)
        # TODO: Possible re-run algorithm here
        serializer.save(donor=current_donor, received=Transaction.PACKAGING, )
    # Note: Based on total pool of donations
    # TODO: Consider checking for oversupply
    # def perform_create(self, serializer):
    #     current_donor = DonorProfile.objects.get(user=self.request.user)
    #     req : BarangayRequest = serializer.data['barangay_request']
    #
    #     supplies = Supply.objects.filter(donation__donor=current_donor)
    #     for item_type in ItemType.objects.all():
    #         type_supplies = supplies.filter(type=item_type)
    #         if type_supplies:
    #             type_total_pax = type_supplies.aggregate(Sum('pax'))
    #             item_req = ItemRequest.objects.get(barangay_request=req,
    #                                                type=item_type)
    #             # Note: Use https://stackoverflow.com/questions/51665260/django-rest-framework-custom-error-message
    #             if type_total_pax.get('pax__sum') < item_req.pax:
    #                 return Response({
    #                     "error": item_type.name + " not enough."},
    #                     status=status.HTTP_400_BAD_REQUEST,)
    #
    #
    #     serializer.save(donor=current_donor,)


class BarangayRequestViewSet(AutoPrefetchViewSetMixin, viewsets.ModelViewSet):
    # queryset = BarangayRequest.objects.all()
    serializer_class = BarangayRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, ]
    pagination_class = SmallResultsSetPagination
    filterset_fields = ['barangay', 'evacuation_center', ]
    search_fields = ['barangay__user__username', 'evacuation_center__name', ]
    permission_classes = [IsAuthenticated]

    @silk_profile(name="Retrieve barangay requests")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @silk_profile(name="Retrieve specific barangay request")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @silk_profile(name="Create barangay request")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        current_user = self.request.user
        queryset = BarangayRequest.objects.all()
        if current_user.role == User.DONOR:
            donor_profile = DonorProfile.objects.get(user=current_user)
            if donor_profile.current_disaster is not None:
                queryset = queryset.filter(barangay__current_disaster=donor_profile.current_disaster)
        return queryset

    def perform_create(self, serializer):
        serializer.save(barangay=BarangayProfile.objects.get(user=self.request.user))

    @action(methods=['get'], detail=True, name='Available pax')
    def not_in_transaction(self, request, pk=None):
        # if not request.query_params.get["type"]:
        #     raise ValidationError(detail="Type parameter required")
        item_type_id = int(request.query_params['type'])
        item_type = ItemType.objects.get(id=item_type_id)
        current_request: BarangayRequest = self.get_object()
        untrans_pax = current_request.calculate_untransacted_pax(item_type)
        total_pax = current_request.total_pax_of_type(item_type)
        return Response(
            {'not_in_transaction': untrans_pax,
             'total': total_pax, }, status=200, )


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(datetime_added=datetime.now(),
                        donor=DonorProfile.objects.get(user=self.request.user),
                        )


class DisasterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Disaster.objects.all()
    serializer_class = DisasterSerializer

    @action(detail=True, methods=['get'], name='Change to Disaster',
            permission_classes=[IsProfileUserOrReadOnly])
    def change_to_disaster(self, request, pk=None):
        current_donor = DonorProfile.objects.get(user=self.request.user)
        if current_donor is not None:
            current_donor.current_disaster = self.get_object()
            current_donor.save()
            return Response(DonorSerializer(current_donor, context={'request': request}, many=False).data)
        else:
            return Response({'error': 'Only donors can change their disaster assignment'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], name='Remove Disaster',
            permission_classes=[IsProfileUserOrReadOnly])
    def remove_disaster(self, request, pk=None):
        if self.request.user.is_anonymous:
            return Response({'error': 'Please log in'})
        current_donor = DonorProfile.objects.get(user=self.request.user)
        if current_donor is not None:
            current_donor.current_disaster = None
            current_donor.save()
            return Response(DonorSerializer(current_donor, context={'request': request}, many=False).data)
        else:
            return Response({'error': 'Only donors can change their disaster assignment'},
                            status=status.HTTP_400_BAD_REQUEST)


class EvacuationCenterViewSet(viewsets.ModelViewSet):
    queryset = EvacuationCenter.objects.all()
    serializer_class = EvacuationCenterSerializer

    def perform_create(self, serializer):
        serializer.save(barangays=BarangayProfile.objects.get(
            user=self.request.user)
        )

    @action(detail=False, methods=['get'], name='Get Current Evac',
            permission_classes=[IsProfileUserOrReadOnly])
    def current_evac(self, request, pk=None):
        user = request.user
        user_barangay = None
        if user.role == user.BARANGAY:
            user_barangay = BarangayProfile.objects.get(user=request.user)
        elif user.role == user.RESIDENT:
            user_resident = ResidentProfile.objects.get(user=request.user)
            user_barangay = user_resident.barangay
        else:
            raise ValidationError(detail="Barangay or Resident profiles only")
        evac_centers = EvacuationCenter.objects.filter(barangays=user_barangay)
        serializer = EvacuationCenterSerializer(evac_centers, many=True)
        return Response(serializer.data)


class SupplyViewSet(AutoPrefetchViewSetMixin, viewsets.ModelViewSet):
    queryset = Supply.objects.all()
    serializer_class = SupplySerializer

    def perform_create(self, serializer):
        serializer.save(datetime_added=datetime.now(timezone.utc),
                        donor=DonorProfile.objects.get(user=self.request.user),
                        )

    @action(detail=True, methods=['put', 'patch'], name='Upload Picture')
    def upload_picture(self, request, pk=None):
        supply = self.get_object()
        if len(list(request.FILES.values())) > 0:
            supply.picture = list(request.FILES.values())[0]  # Get first file
        else:
            return Response({'status': 'Please upload a picture'})
        supply.save()
        return Response({'status': 'File uploaded'})

    @action(detail=False, methods=['get'], name='Get Current Supplies',
            permission_classes=[IsProfileUserOrReadOnly])
    def current_supplies(self, request, pk=None):
        user_donor = DonorProfile.objects.get(user=request.user)
        # Preparation for Donation deprecation
        supplies = Supply.objects.filter(donation__donor=user_donor) | Supply.objects.filter(donor=user_donor)
        serializer = SupplySerializer(supplies, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['get'], detail=True, name='Available pax')
    def available_pax(self, request, pk=None):
        current_supply: Supply = self.get_object()
        available_pax = current_supply.calculate_available_pax()
        total_pax = current_supply.pax
        return Response(
            {'available': available_pax,
             'total': total_pax, }, status=200, )


class ItemTypeViewSet(viewsets.ModelViewSet):
    queryset = ItemType.objects.all()
    serializer_class = ItemTypeSerializer


class ItemRequestViewSet(viewsets.ModelViewSet):
    queryset = ItemRequest.objects.all()
    serializer_class = ItemRequestSerializer

    def perform_create(self, serializer):
        serializer.save(date_added=datetime.now(timezone.utc))


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    @action(methods=['patch', 'put'], detail=False, name='Rate Barangay in Current Disaster')
    def rate(self, request, pk=None):
        serializer = RatingOnlySerializer(data=request.data)
        user = request.user
        if user.role != User.RESIDENT:
            return Response({'error': 'Only residents can rate'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            value = serializer.validated_data['value']
            user_barangay: BarangayProfile = user.resident_profile.barangay
            current_disaster = user_barangay.current_disaster
            rating = Rating.objects \
                .filter(resident__user=user) \
                .filter(disaster=current_disaster) \
                .filter(barangay=user_barangay)
            if rating:
                rating = rating[0]
                rating.value = value
                rating.save()
                return Response(data=RatingSerializer(rating).data, status=status.HTTP_200_OK)
            else:
                rating = Rating.objects.create(
                    resident=user.resident_profile,
                    disaster=current_disaster,
                    barangay=user.resident_profile.barangay,
                )
                return Response(data=RatingSerializer(rating).data, status=status.HTTP_201_CREATED)


class TransactionStubViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionStubSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, ]
    filterset_fields = ['request__evacuation_center__name', ]
    search_fields = ['request__evacuation_center__name']

    def get_queryset(self):
        if self.request.user.role == User.BARANGAY:
            return TransactionStub.objects.filter(resident__barangay__user=self.request.user)
        else:
            return TransactionStub.objects.filter(resident__user=self.request.user)

    @action(methods=['patch', 'put'], detail=True, name='Mark as received')
    def mark_as_received(self, request, pk=None):
        transaction_stub = TransactionStub.objects.get(pk=pk)
        transaction_stub.received = True
        transaction_stub.save()
        return Response(
            {'message': 'Marked as received', }, status=status.HTTP_200_OK, )


class AlgorithmExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AlgorithmExecutionSerializer

    @action(detail=True, methods=['post'], name='Accept Suggestion',
            permission_classes=[IsProfileUserOrReadOnly])
    @transaction.atomic
    def accept(self, request, pk=None):
        # TODO: Consider moving to DonorViewSet
        algo_exec = self.get_object()
        donor = algo_exec.donor
        suggestion = algo_exec.result
        route_nodes = RouteNode.objects.filter(suggestion=suggestion)
        created_transactions = []
        supplies = Supply.objects.filter(donation__donor=donor)
        for route_node in route_nodes:
            fulfillments = Fulfillment.objects.filter(node=route_node)
            created_transaction = Transaction.objects.create(donor=donor, received=Transaction.PACKAGING,
                                                             barangay_request=route_node.request, )
            created_transactions.append(created_transaction)
            for fulfillment in fulfillments:
                remaining_fulfillment_pax = fulfillment.pax
                item_type = fulfillment.type
                for supply in supplies.filter(type=item_type):
                    if remaining_fulfillment_pax == 0:
                        break
                    available_pax = supply.calculate_available_pax()
                    if available_pax >= remaining_fulfillment_pax:
                        TransactionOrder.objects.create(pax=remaining_fulfillment_pax, supply=supply,
                                                        transaction=created_transaction, )
                        remaining_fulfillment_pax = 0
                    else:
                        TransactionOrder.objects.create(pax=available_pax, supply=supply,
                                                        transaction=created_transaction, )
                        remaining_fulfillment_pax = remaining_fulfillment_pax - available_pax

        # serializer = EvacuationCenterSerializer(barangay_request.evacuation_center)
        suggestion.accepted = True
        suggestion.save()
        return Response(TransactionSerializer(created_transactions,
                                              many=True,
                                              context={'request': request}).data, status=201)

    @action(methods=['post'], detail=False, name='Execute Algorithm')
    @transaction.atomic
    def execute(self, request, pk=None):
        # if request.data['geolocation']:
        if 'geolocation' in request.data:
            UserLocation.objects.create(geolocation=request.data['geolocation'],
                                        user=request.user,
                                        time=datetime.now())
        user = request.user
        if not user.is_anonymous and user.role == User.DONOR:
            user_donor = DonorProfile.objects.get(user=user)
            algo_exec = AlgorithmExecution.objects.filter(
                donor=user_donor)
            algo_exec = algo_exec.filter(result__isnull=True) | algo_exec.filter(result__accepted=False,
                                                                                 result__expiration_time__gt=
                                                                                 datetime.now(timezone.utc))

            if not algo_exec:
                new_algo_exec = AlgorithmExecution.objects.create(donor=user_donor)
                solo_algo_tests.apply_async(args=['tabu', user_donor.id, new_algo_exec.id])
                return Response(AlgorithmExecutionSerializer(new_algo_exec).data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    AlgorithmExecutionSerializer(algo_exec[0], context={'request': request}, many=False).data,
                    status=status.HTTP_200_OK)
        else:
            raise ValidationError(detail="Not a donor account",
                                  code=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        user = self.request.user
        if not user.is_anonymous:
            return AlgorithmExecution.objects.filter(donor__user=user)
        else:
            return AlgorithmExecution.objects.all()


class RouteSuggestionViewSet(viewsets.ReadOnlyModelViewSet):
    # TODO: Filter query set according to current user?
    # queryset = RouteSuggestion.objects.all()
    serializer_class = RouteSuggestionSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_anonymous:
            return RouteSuggestion.objects.filter(donor__user=user)
        else:
            return RouteSuggestion.objects.all()


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, ]
    filterset_fields = ['unread', ]

    @action(detail=False, methods=['get'], name='Mark All Notifications of current user',
            permission_classes=[IsProfileUserOrReadOnly])
    def mark_all_as_read(self, request, pk=None):
        recipient = self.request.user
        Notification.objects.mark_all_as_read(recipient)
        return Response({"success": "All notifications marked as read"})

    def get_queryset(self):
        recipient = self.request.user
        if recipient.is_anonymous:
            return Notification.objects.all()
        notifications = Notification.objects.filter(recipient=recipient)
        return notifications
