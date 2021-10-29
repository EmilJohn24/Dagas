from rest_framework import serializers

from relief.models import Donation, Supply, User


class SupplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Supply
        fields = ('name', 'quantity', 'pax', 'donation',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',)
