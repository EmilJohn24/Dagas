from django.db.models import Sum
from django.utils.datetime_safe import datetime
from rest_framework.response import Response
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError, ValidationError

from relief.models import User, ResidentProfile, DonorProfile, Supply, ItemType, ItemRequest, Transaction, \
    BarangayRequest, TransactionImage, BarangayProfile, Donation, EvacuationCenter, TransactionOrder
from relief.permissions import IsOwnerOrReadOnly, IsProfileUserOrReadOnly
from relief.serializers import UserSerializer, ResidentSerializer, DonorSerializer, SupplySerializer, \
    ItemTypeSerializer, ItemRequestSerializer, TransactionSerializer, BarangayRequestSerializer, BarangaySerializer, \
    DonationSerializer, EvacuationCenterSerializer, TransactionOrderSerializer


# Guide: https://www.django-rest-framework.org/api-guide/viewsets/
# TODO: Add permission classes
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'], name='Get Current User',
            permission_classes=[IsProfileUserOrReadOnly])
    def current_user(self, request, pk=None):
        user_serializer = UserSerializer(request.user)
        return Response(user_serializer.data)


class ResidentViewSet(viewsets.ModelViewSet):
    queryset = ResidentProfile.objects.all()
    serializer_class = ResidentSerializer

    # Can also be applied to views
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # def post(self, request, *args, **kwargs):
    #     file = request.data['file']
    #     profile = self.get_object()
    #     profile.gov_id = file
    #     profile.save()

    @action(detail=True, methods=['patch', 'put'], name='Upload ID', permission_classes=[IsProfileUserOrReadOnly])
    def upload_id(self, request, pk=None):
        profile: ResidentProfile = self.get_object()
        profile.gov_id = list(request.FILES.values())[0]  # Get first file
        profile.save()
        return Response({'status': 'File uploaded'})


class BarangayViewSet(viewsets.ModelViewSet):
    queryset = BarangayProfile.objects.all()
    serializer_class = BarangaySerializer

    # Can also be applied to views
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class TransactionOrderViewSet(viewsets.ModelViewSet):
    queryset = TransactionOrder.objects.all()
    serializer_class = TransactionOrderSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    @action(detail=True, methods=['patch', 'put'], name='Upload Transaction Picture',
            permission_classes=[IsProfileUserOrReadOnly])
    def upload_image(self, request, pk=None):
        transaction: Transaction = self.get_object()
        new_image: TransactionImage = TransactionImage.objects.create()
        new_image.image = list(request.FILES.values())[0]  # Get first image uploaded
        new_image.transaction = transaction
        new_image.save()

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


class BarangayRequestViewSet(viewsets.ModelViewSet):
    queryset = BarangayRequest.objects.all()
    serializer_class = BarangayRequestSerializer

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

    def perform_create(self, serializer):
        serializer.save(datetime_added=datetime.now(),
                        donor=DonorProfile.objects.get(user=self.request.user),
                        )


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
        user_barangay = BarangayProfile.objects.get(user=request.user)
        evac_centers = EvacuationCenter.objects.filter(barangays=user_barangay)
        serializer = EvacuationCenterSerializer(evac_centers, many=True)
        return Response(serializer.data)


class SupplyViewSet(viewsets.ModelViewSet):
    queryset = Supply.objects.all()
    serializer_class = SupplySerializer

    @action(detail=False, methods=['get'], name='Get Current Supplies',
            permission_classes=[IsProfileUserOrReadOnly])
    def current_supplies(self, request, pk=None):
        user_donor = DonorProfile.objects.get(user=request.user)
        supplies = Supply.objects.filter(donation__donor=user_donor)
        serializer = SupplySerializer(supplies, many=True)
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
        serializer.save(date_added=datetime.now())
