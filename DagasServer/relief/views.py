from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
# For REST API-based views, use the list at: https://www.django-rest-framework.org/api-guide/generic-views/
from django.utils.decorators import method_decorator
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from relief.decorators import role_required
from relief.models import User, ResidentProfile, GovAdminProfile, DonorProfile, Donation
from relief.permissions import IsProfileUserOrReadOnly
from relief.serializers import UserSerializer, ResidentSerializer, GovAdminSerializer, DonorSerializer, \
    DonationSerializer

gov_admin_required = role_required(role_id=User.GOVERNMENT_ADMIN)


# @method_decorator(gov_admin_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UserListView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(detail=True, methods=['get'], name='Get Current User',
            permission_classes=[IsProfileUserOrReadOnly])
    def current_user(self, request):
        user_serializer = UserSerializer(request.user)
        return Response(user_serializer.data)


# @method_decorator(gov_admin_required, name='dispatch')
# @method_decorator(gov_admin_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UserDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()


@method_decorator(login_required, name='dispatch')
class ResidentListView(generics.ListCreateAPIView):
    serializer_class = ResidentSerializer
    queryset = ResidentProfile.objects.all()


@method_decorator(login_required, name='dispatch')
class GovAdminListView(generics.ListCreateAPIView):
    serializer_class = GovAdminSerializer
    queryset = GovAdminProfile.objects.all()


@method_decorator(login_required, name='dispatch')
class DonorListView(generics.ListCreateAPIView):
    serializer_class = DonorSerializer
    queryset = DonorProfile.objects.all()


@method_decorator(login_required, name='dispatch')
class DonorDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = DonorSerializer
    queryset = DonorProfile.objects.all()


# TODO: Add donor_required decorator
@method_decorator(login_required, name='dispatch')
class DonationListView(generics.ListCreateAPIView):
    serializer_class = DonationSerializer
    queryset = Donation.objects.all()

    # def perform_create(self, serializer):
    #     serializer.save(owner=self.request.user)


# TODO: Add donor_required decorator
@method_decorator(login_required, name='dispatch')
class DonationDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = DonationSerializer
    queryset = Donation.objects.all()

    # def perform_create(self, serializer):
    #     serializer.save(owner=self.request.user)
