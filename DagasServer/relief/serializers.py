from django.db import transaction
from django.db.models import Sum
from rest_framework import serializers
# from rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework.reverse import reverse

from relief.models import Donation, Supply, User, ResidentProfile, DonorProfile, GovAdminProfile, BarangayProfile, \
    ItemType, ItemRequest, BarangayRequest, EvacuationDetails, Transaction, TransactionImage, EvacuationCenter, \
    TransactionOrder, UserLocation, Fulfillment, RouteNode, RouteSuggestion


class ItemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemType
        fields = ('id', 'name')


class SupplySerializer(serializers.ModelSerializer):
    available_pax = serializers.IntegerField(source='calculate_available_pax')

    class Meta:
        model = Supply
        fields = ('id', 'name', 'type', 'quantity', 'pax', 'donation', 'available_pax',)


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
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role', 'profile_picture')
        read_only_fields = ('profile_picture',)


class UserLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = ('id', 'user', 'geolocation', 'time')
        read_only_fields = ('user', 'time',)


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

    user_link = serializers.HyperlinkedRelatedField(
        source='user',
        many=False,
        read_only=True,
        view_name='relief:users-detail',
    )

    class Meta:
        model = DonorProfile
        fields = ('id', 'user', 'donations', 'user_link')
        read_only_fields = ('user_link',)


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

    item_requests_serialized = ItemRequestSerializer(source='item_request', many=True, read_only=True, )

    barangay = serializers.HyperlinkedRelatedField(
        required=False,
        read_only=False,
        queryset=BarangayProfile.objects.all(),
        view_name='relief:barangays-detail',
    )

    barangay_serialized = BarangaySerializer(source='barangay', read_only=True, many=False, )
    evacuation_center_serialized = EvacuationCenterSerializer(source='evacuation_center',
                                                              read_only=True, many=False, )
    expected_date = serializers.DateTimeField(required=False)

    # def create(self, validated_data):
    #     barangay_request: BarangayRequest = BarangayRequest.objects.create()
    #     barangay_request.expected_date = validated_data["expected_date"]
    #

    class Meta:
        model = BarangayRequest
        fields = ('id', 'item_request', 'item_requests_serialized',
                  'evacuation_center', 'expected_date', 'barangay',
                  'barangay_serialized', 'evacuation_center_serialized')
        read_only_fields = ('item_requests_serialized', 'barangay_serialized', 'evacuation_center_serialized')


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
    donor_info = DonorSerializer(source='donor', many=False, read_only=True)
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
        fields = ('id', 'donor', 'donor_name', 'donor_info', 'barangay_name', 'evac_center_name',
                  'transaction_image', 'qr_code', 'transaction_orders',
                  'barangay_request', 'received', 'received_date')
        read_only_fields = ('qr_code', 'received', 'donor', 'donor_info')


class FulfillmentSerializer(serializers.ModelSerializer):
    type_name = serializers.StringRelatedField(
        read_only=True,
        source='type',
    )

    class Meta:
        model = Fulfillment
        fields = ('id', 'node', 'type', 'type_name', 'pax',)
        read_only_fields = ('node', 'type', 'type_name', 'pax',)


class RouteNodeSerializer(serializers.ModelSerializer):
    request = serializers.HyperlinkedRelatedField(
        required=False,
        view_name='relief:barangay_request-detail',
        read_only=True,
    )
    barangay_name = serializers.StringRelatedField(
        required=False,
        read_only=True,
        source='request.barangay',
    )

    evacuation_center_name = serializers.StringRelatedField(
        read_only=True,
        source='request.evacuation_center',
    )

    evacuation_center_geolocation = serializers.StringRelatedField(
        read_only=True,
        source='request.evacuation_center.geolocation',
    )
    fulfillments = FulfillmentSerializer(source='fulfillment_set',
                                         read_only=True, many=True, )

    class Meta:
        model = RouteNode
        fields = ('id', 'request', 'suggestion', 'barangay_name', 'evacuation_center_name',
                  'evacuation_center_geolocation', 'fulfillments', 'distance_from_prev',)
        read_only_fields = ('id', 'request', 'suggestion', 'barangay_name', 'evacuation_center_name',
                            'evacuation_center_geolocation', 'fulfillments', 'distance_from_prev',)


class RouteSuggestionSerializer(serializers.ModelSerializer):
    donor = serializers.HyperlinkedRelatedField(
        required=False,
        view_name='relief:donor_details',
        read_only=False,
        queryset=DonorProfile.objects.all(),
    )
    donor_name = serializers.StringRelatedField(
        required=False,
        read_only=True,
        source='donor',
    )
    route_nodes = RouteNodeSerializer(source='nodes', read_only=True, many=True, )

    class Meta:
        model = RouteSuggestion
        fields = ('id', 'donor', 'donor_name', 'route_nodes')
        read_only_fields = ('id', 'donor', 'donor_name', 'route_nodes')


# Based on: https://stackoverflow.com/questions/62291394/django-rest-auth-dj-rest-auth-custom-user-registration
class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, allow_null=True, allow_blank=True)

    # profile_picture = serializers.ImageField()
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
            # 'profile picture': self.validated_data.get('profile_picture'),
        }

    @transaction.atomic
    def save(self, request):
        user = super().save(request)
        user.role = self.validated_data.get('role')
        user.save()
        return user
