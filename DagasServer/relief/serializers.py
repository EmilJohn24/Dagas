from django.db import transaction
from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from relief.models import Donation, Supply, User, ResidentProfile, DonorProfile, GovAdminProfile


class SupplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Supply
        fields = ('name', 'quantity', 'pax', 'donation',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role',)


# Profile serializers
class ResidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentProfile
        fields = ('id', 'user')


class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentProfile
        fields = ('id', 'user')


class BarangaySerializer(serializers.ModelSerializer):
    class Meta:
        model = DonorProfile
        fields = ('id', 'user')


class GovAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovAdminProfile
        fields = ('id', 'user')


# Based on: https://stackoverflow.com/questions/62291394/django-rest-auth-dj-rest-auth-custom-user-registration
class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, allow_null=True, allow_blank=True)

    def get_cleaned_data(self):
        super(CustomRegisterSerializer, self).get_cleaned_data()
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'role': self.validated_data.get('role'),
        }

    @transaction.atomic
    def save(self, request):
        user = super().save(request)
        user.role = self.validated_data.get('role')
        user.save()
        return user
