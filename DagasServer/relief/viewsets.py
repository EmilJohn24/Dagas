from django.utils.datetime_safe import datetime
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError

from relief.models import User, ResidentProfile, DonorProfile, Supply, ItemType, ItemRequest, Transaction, \
    BarangayRequest, TransactionImage, BarangayProfile, Donation
from relief.permissions import IsOwnerOrReadOnly, IsProfileUserOrReadOnly
from relief.serializers import UserSerializer, ResidentSerializer, DonorSerializer, SupplySerializer, \
    ItemTypeSerializer, ItemRequestSerializer, TransactionSerializer, BarangayRequestSerializer, BarangaySerializer, \
    DonationSerializer


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


class BarangayRequestViewSet(viewsets.ModelViewSet):
    queryset = BarangayRequest.objects.all()
    serializer_class = BarangayRequestSerializer

    def perform_create(self, serializer):
        serializer.save(barangay=BarangayProfile.objects.get(user=self.request.user))


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer

    def perform_create(self, serializer):
        serializer.save(datetime_added=datetime.now(),
                        donor=DonorProfile.objects.get(user=self.request.user),
                        )


class SupplyViewSet(viewsets.ModelViewSet):
    queryset = Supply.objects.all()
    serializer_class = SupplySerializer


class ItemTypeViewSet(viewsets.ModelViewSet):
    queryset = ItemType.objects.all()
    serializer_class = ItemTypeSerializer


class ItemRequestViewSet(viewsets.ModelViewSet):
    queryset = ItemRequest.objects.all()
    serializer_class = ItemRequestSerializer

    def perform_create(self, serializer):
        serializer.save(date_added=datetime.now())
