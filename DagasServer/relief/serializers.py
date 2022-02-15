from django.db import transaction
from django.db.models import Sum
from rest_framework import serializers
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework.reverse import reverse

from relief.models import Donation, Supply, User, ResidentProfile, DonorProfile, GovAdminProfile, BarangayProfile, \
    ItemType, ItemRequest, BarangayRequest, EvacuationDetails, Transaction, TransactionImage, EvacuationCenter, \
    TransactionOrder


class ItemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemType
        fields = ('id', 'name')


class SupplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Supply
        fields = ('id', 'name', 'type', 'quantity', 'pax', 'donation',)


class DonationSerializer(serializers.ModelSerializer):
    donor = serializers.HyperlinkedRelatedField(
        required=False,
        view_name='relief:donor_details',
        read_only=False,
        queryset=DonorProfile.objects.all(),
    )
    supplies = serializers.HyperlinkedRelatedField(
        required=False,
        many=True,
        read_only=False,
        queryset=Supply.objects.all(),
        view_name='relief:supply-detail'
    )

    datetime_added = serializers.DateTimeField(
        required=False,
    )

    class Meta:
        model = Donation
        fields = ['id', 'donor', 'supplies', 'datetime_added']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role',)


# Profile serializers
class BarangaySerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = BarangayProfile
        fields = ('id', 'user')


class ResidentSerializer(serializers.ModelSerializer):
    barangay = serializers.PrimaryKeyRelatedField(many=False, required=False,
                                                  queryset=BarangayProfile.objects.all(), )
    barangay_info = BarangaySerializer(source='barangay', read_only=True,
                                       many=False, allow_null=True, )

    class Meta:
        model = ResidentProfile
        fields = ('id', 'user', 'gov_id', 'barangay', 'barangay_info',)
        read_only_fields = ('user', 'owner',)


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


class GovAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovAdminProfile
        fields = ('id', 'user')


class EvacuationCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvacuationCenter
        fields = ('id', 'name', 'barangays', 'address', 'geolocation')


class EvacuationDetailsSerializer(serializers.ModelSerializer):
    # TODO : Create HyperlinkedRelatedFields for barangay and evacuation_center
    class Meta:
        model = EvacuationDetails
        fields = ('barangay', 'evacuation_center', 'time_evacuated')


class ItemRequestSerializer(serializers.ModelSerializer):
    date_added = serializers.DateTimeField(required=False)

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
        required=False,
        read_only=False,
        queryset=BarangayProfile.objects.all(),
        view_name='relief:barangays-detail',
    )

    expected_date = serializers.DateTimeField(required=False)

    # def create(self, validated_data):
    #     barangay_request: BarangayRequest = BarangayRequest.objects.create()
    #     barangay_request.expected_date = validated_data["expected_date"]
    #

    class Meta:
        model = BarangayRequest
        fields = ('id', 'item_request', 'evacuation_center', 'expected_date', 'barangay')


# TODO: Consider using serializers.ImageField
class TransactionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionImage
        fields = ('id', 'image', 'transaction')


class TransactionOrderSerializer(serializers.ModelSerializer):
    def validate(self, data):
        request = self.context.get('request')
        current_donor = DonorProfile.objects.get(user=request.user)
        # transaction: BarangayRequest = serializer.data['transaction']
        supplies = Supply.objects.filter(donation__donor=current_donor)
        donor_transactions = Transaction.objects.filter(donor=current_donor)
        item_pax = data['pax']
        item_supply: Supply = data['supply']
        item_type = item_supply.type

        # Get all transactions with that supply
        supply_transactions = TransactionOrder.objects.filter(supply=item_supply)
        if supply_transactions is not None:
            if item_pax > item_supply.calculate_available_pax():
                raise serializers.ValidationError({
                    "pax": item_supply.name + " has insufficient pax."}, )

        type_supplies = supplies.filter(type=item_type)
        all_orders = TransactionOrder.objects.filter(transaction__in=donor_transactions)
        all_order_type_pax = all_orders.filter(supply__type=item_type).aggregate(Sum('pax'))
        transaction_pax = all_order_type_pax.get('pax__sum')
        if transaction_pax is None:
            transaction_pax = 0

        if type_supplies:
            type_supply_pax_sum = type_supplies.aggregate(Sum('pax'))
            type_supply_pax = type_supply_pax_sum.get('pax__sum')

            # Note: Use https://stackoverflow.com/questions/51665260/django-rest-framework-custom-error-message
            if type_supply_pax - transaction_pax < item_pax:
                raise serializers.ValidationError({
                    "pax": item_type.name + " not enough."}, )
        return data

    supply_info = SupplySerializer(source='supply', many=False, read_only=True, )

    class Meta:
        model = TransactionOrder
        fields = ('id', 'pax', 'supply', 'supply_info', 'transaction',)


class TransactionSerializer(serializers.ModelSerializer):
    # TODO: Validate for oversupply (check if all transactions > requested amount)
    donor = serializers.HyperlinkedRelatedField(
        required=False,
        view_name='relief:donor_details',
        read_only=False,
        queryset=DonorProfile.objects.all(),
    )
    donor_name = serializers.StringRelatedField(source='donor', many=False, read_only=True, )
    # barangay_request = serializers.HyperlinkedRelatedField(
    #     view_name='relief:barangay_request-detail',
    #     read_only=False,
    #     queryset=BarangayRequest.objects.all(),
    # )
    transaction_image = TransactionImageSerializer(many=True, read_only=True)
    received_date = serializers.StringRelatedField(many=False)
    transaction_orders = TransactionOrderSerializer(source='transactionorder_set',
                                                    read_only=True, many=True, )
    barangay_name = serializers.StringRelatedField(source='barangay_request.barangay', many=False, read_only=True, )
    evac_center_name = serializers.StringRelatedField(source='barangay_request.evacuation_center',
                                                      many=False, read_only=True, )

    class Meta:
        model = Transaction
        fields = ('id', 'donor', 'donor_name', 'barangay_name', 'evac_center_name',
                  'transaction_image', 'qr_code', 'transaction_orders',
                  'barangay_request', 'received', 'received_date')
        read_only_fields = ('qr_code', 'received', 'donor',)


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
