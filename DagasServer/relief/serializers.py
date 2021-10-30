from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from relief.models import Donation, Supply, User


class SupplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Supply
        fields = ('name', 'quantity', 'pax', 'donation',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',)


# Based on: https://stackoverflow.com/questions/62291394/django-rest-auth-dj-rest-auth-custom-user-registration
class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)

    def get_cleaned_data(self):
        super(CustomRegisterSerializer, self).get_cleaned_data()
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'role': self.validated_data.get('role', ''),
        }
