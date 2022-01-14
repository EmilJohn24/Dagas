from django.db import transaction
from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from relief.models import Donation, Supply, User, ResidentProfile, DonorProfile, GovAdminProfile, BarangayProfile, \
    ItemType, ItemRequest, BarangayRequest, EvacuationDetails, Transaction, TransactionImage


class ItemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemType
        fields = ('id', 'name')


class SupplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Supply
        fields = ('name', 'type', 'quantity', 'pax', 'donation',)


class DonationSerializer(serializers.ModelSerializer):
    donor = serializers.HyperlinkedRelatedField(
        view_name='relief:donor_details',
        read_only=False,
        queryset=DonorProfile.objects.all(),
    )
    supplies = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=False,
        queryset=Supply.objects.all(),
        view_name='relief:supply-detail'
    )

    class Meta:
        model = Donation
        fields = ['donor', 'supplies', 'datetime_added']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role',)


# Profile serializers
class ResidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentProfile
        fields = ('id', 'user', 'gov_id')


class DonorSerializer(serializers.ModelSerializer):
    # donations = DonationSerializer(source='donation_set',)
    donations = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='relief:donations_details',
    )

    class Meta:
        model = DonorProfile
        fields = ('id', 'user', 'donations')


class BarangaySerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = BarangayProfile
        fields = ('id', 'user')


class GovAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovAdminProfile
        fields = ('id', 'user')


class EvacuationDetailsSerializer(serializers.ModelSerializer):
    # TODO : Create HyperlinkedRelatedFields for barangay and evacuation_center
    class Meta:
        model = EvacuationDetails
        fields = ('barangay', 'evacuation_center', 'time_evacuated')


class ItemRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemRequest
        fields = ('id', 'type', 'pax', 'date_added', 'barangay_request')


# TODO: Include EvacuationDetails
class BarangayRequestSerializer(serializers.ModelSerializer):
    item_request = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        # queryset=ItemRequest.objects.all(),
        view_name='relief:item_request-detail'
    )

    barangay = serializers.HyperlinkedRelatedField(
        read_only=False,
        queryset=BarangayProfile.objects.all(),
        view_name='relief:barangays-detail',
    )

    # def create(self, validated_data):
    #     barangay_request: BarangayRequest = BarangayRequest.objects.create()
    #     barangay_request.expected_date = validated_data["expected_date"]
    #

    class Meta:
        model = BarangayRequest
        fields = ('id', 'item_request', 'expected_date', 'barangay')


# TODO: Consider using serializers.ImageField
class TransactionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionImage
        fields = ('id', 'image', 'transaction')


# TODO: Make transaction image work
class TransactionSerializer(serializers.ModelSerializer):
    donor = serializers.HyperlinkedRelatedField(
        view_name='relief:donor_details',
        read_only=False,
        queryset=DonorProfile.objects.all(),
    )
    barangay_request = serializers.HyperlinkedRelatedField(
        view_name='relief:barangay_request-detail',
        read_only=False,
        queryset=BarangayRequest.objects.all(),
    )
    transaction_image = TransactionImageSerializer(many=True, read_only=True)

    received_date = serializers.StringRelatedField(many=False)

    class Meta:
        model = Transaction
        fields = ('id', 'donor', 'transaction_image', 'qr_code', 'barangay_request', 'received', 'received_date')
        read_only_fields = ('qr_code', 'received')

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
