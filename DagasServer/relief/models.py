import uuid
from datetime import datetime
from io import StringIO

import django.contrib.auth
import qrcode
from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
# See management/commands/create_groups.py for list of groups
# TODO: Finish models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_google_maps import fields as map_fields
from DagasServer import settings


# START User Management
# User profile picture path
def user_profile_picture_path(instance, filename):
    return 'profilePicture/id_{0}/{1}'.format(instance.id, filename)


# Use default user model


class User(AbstractUser):
    RESIDENT = 1
    DONOR = 2
    BARANGAY = 3
    GOVERNMENT_ADMIN = 4

    ROLE_CHOICES = (
        (RESIDENT, 'Resident'),
        (DONOR, 'Donor'),
        (BARANGAY, 'Barangay'),
        (GOVERNMENT_ADMIN, 'Admin')
    )

    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)

    profile_picture = models.ImageField(null=True, blank=True, upload_to=user_profile_picture_path)

    def get_most_recent_location(self):
        user_locations = UserLocation.objects.filter(user=self)
        return user_locations.last()


# User Profiles
def resident_id_path(instance, filename):
    return 'resident/id_{0}/{1}'.format(instance.user.id, filename)


class UserLocation(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, related_name="user_location")
    geolocation = map_fields.GeoLocationField(max_length=100, null=True)
    time = models.DateTimeField('Date and time')


class ResidentProfile(models.Model):
    """
        User information exclusive to residents
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, related_name="resident_profile")
    # TODO: Add Pillow library to support ImageField
    gov_id = models.ImageField(null=True, upload_to=resident_id_path)
    barangay = models.ForeignKey(to="BarangayProfile", on_delete=models.CASCADE, related_name="barangay", null=True, )


class DonorProfile(models.Model):
    """
        User information exclusive to donors
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, related_name="donor_profile")

    def __str__(self):
        return self.user.__str__()


class BarangayProfile(models.Model):
    """
        User information exclusive to barangays
    """
    # TODO: Add geolocation and evacuation centers
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, related_name="barangay_profile")

    def __str__(self):
        return self.user.username


class GovAdminProfile(models.Model):
    """
        User information exclusive to government admins
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, related_name="gov_admin_profile")


# Called after a user is created (post-save receiver decorator)
@receiver(post_save, sender=User)
def generate_user_profile(sender, instance, created, **kwargs):
    if instance.role == User.RESIDENT:
        instance, created = ResidentProfile.objects.get_or_create(user=instance)
    elif instance.role == User.DONOR:
        instance, created = DonorProfile.objects.get_or_create(user=instance)
    elif instance.role == User.BARANGAY:
        instance, created = BarangayProfile.objects.get_or_create(user=instance)
    elif instance.role == User.GOVERNMENT_ADMIN:
        instance, created = GovAdminProfile.objects.get_or_create(user=instance)
    else:
        return
    instance.save()


# END User Management
class EvacuationDetails(models.Model):
    # TODO: Add datetime validation later
    barangay = models.ForeignKey(to=BarangayProfile, on_delete=models.CASCADE)
    # TODO: Remove null=True after test
    evacuation_center = models.ForeignKey(to='EvacuationCenter', on_delete=models.CASCADE, null=True)
    time_evacuated = models.DateTimeField()


class EvacuationCenter(models.Model):
    """
    Evacuation centers
    """
    # TODO: Add geolocation
    name = models.CharField(max_length=200)
    barangays = models.ForeignKey(null=True, to=BarangayProfile, on_delete=models.CASCADE, related_name='centers', )
    # barangays = models.ManyToManyField(to=BarangayProfile, related_name='centers',
    #                                    through=EvacuationDetails)
    # Geolocation
    address = map_fields.AddressField(max_length=200, null=True)
    geolocation = map_fields.GeoLocationField(max_length=100, null=True)

    def __str__(self):
        return self.name

    def get_geolocation(self):
        return self.geolocation


class Donation(models.Model):
    donor = models.ForeignKey(DonorProfile,
                              on_delete=models.CASCADE,
                              related_name='donations')  # Removed: limit_choices_to={'groups__name': 'donors'})
    datetime_added = models.DateTimeField('Date added')

    def __str__(self):
        return self.donor.__str__() + ':' + str(self.id)


class ItemType(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


# TODO: Add some kind of type to Supply (e.g. Food, Water)
class Supply(models.Model):
    name = models.CharField(max_length=250)
    type = models.ForeignKey(ItemType, on_delete=models.CASCADE, related_name='type')
    quantity = models.IntegerField()
    pax = models.IntegerField()
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='supplies')
    transaction = models.ForeignKey(to="Transaction", on_delete=models.CASCADE, related_name='transaction_supply',
                                    null=True)

    # Not in transaction
    def calculate_available_pax(self):
        supply_transactions = TransactionOrder.objects.filter(supply=self)
        if supply_transactions is not None:
            pax_in_transaction = supply_transactions.aggregate(Sum('pax')).get('pax__sum')
            if pax_in_transaction is None:
                return self.pax
            available_supply_pax = self.pax - pax_in_transaction
            return available_supply_pax
        else:
            return self.pax

    def is_ongoing(self) -> bool:
        """
        :return: True if the supply is included in a Transaction
        """
        return self.transaction is not None

    def __str__(self) -> str:
        return self.name


# TODO: Check if good models

class TransactionOrder(models.Model):
    # type = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    pax = models.IntegerField()
    supply = models.ForeignKey(Supply, null=True, on_delete=models.CASCADE)
    transaction = models.ForeignKey(to="Transaction", on_delete=models.CASCADE)


# TODO: Make views for Transaction
class Transaction(models.Model):
    # Status List
    PACKAGING = 1
    INCOMING = 2
    RECEIVED = 3

    STATUS_CHOICES = (
        (PACKAGING, 'Packaging'),
        (INCOMING, 'Incoming'),
        (RECEIVED, 'Received'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code = models.ImageField(upload_to='transaction_QRs', blank=True, null=True)
    donor = models.ForeignKey(to=DonorProfile, on_delete=models.CASCADE)
    barangay_request = models.ForeignKey(to="BarangayRequest", on_delete=models.CASCADE)
    received = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, null=True,
                                                blank=True)  # 1 = received, 0 = not received
    received_date = models.DateTimeField(null=True)

    def __str__(self):
        return str(self.barangay_request) + " " + str(self.id)

    def save(self, *args, **kwargs):
        if self._state.adding:
            filename = 'qr_%s.png' % self.id
            qr_code_file = ContentFile(b'', name=filename)
            img = qrcode.make(str(self.id))
            img.save(qr_code_file)
            self.qr_code = qr_code_file

        super(Transaction, self).save(*args, **kwargs)


def transaction_img_path(instance, filename):
    return 'transactions/id_{0}/{1}'.format(instance.transaction.id, filename)


class TransactionImage(models.Model):
    image = models.ImageField(null=True, upload_to=transaction_img_path)
    transaction = models.ForeignKey(to=Transaction, on_delete=models.CASCADE, related_name='transaction_image')


class BarangayRequest(models.Model):
    barangay = models.ForeignKey(null=True, to=BarangayProfile, on_delete=models.CASCADE)
    evacuation_center = models.ForeignKey(null=True, to=EvacuationCenter, on_delete=models.CASCADE)
    details = models.ForeignKey(null=True, to=EvacuationDetails,
                                on_delete=models.CASCADE)  # contains both the barangay and the evac center
    expected_date = models.DateTimeField(null=True, default=datetime.now)

    def __str__(self):
        return self.barangay.user.username + " (" + str(self.id) + ")"

    def total_pax_of_type(self, item_type: ItemType):
        type_requests = ItemRequest.objects.filter(barangay_request=self)
        type_requests = type_requests.filter(type=item_type)
        pax_from_requests = 0
        if type_requests is not None:
            return type_requests.aggregate(Sum('pax')).get('pax__sum')
        else:
            return 0

    def calculate_untransacted_pax(self, item_type: ItemType):
        type_requests = ItemRequest.objects.filter(barangay_request=self)
        type_requests = type_requests.filter(type=item_type)
        transaction_orders = TransactionOrder.objects.filter(transaction__barangay_request=self)
        transaction_orders = transaction_orders.filter(supply__type=item_type)
        pax_from_requests = 0
        if type_requests is not None:
            pax_from_requests = type_requests.aggregate(Sum('pax')).get('pax__sum')
        else:
            return 0

        if transaction_orders is not None:
            pax_in_transaction = transaction_orders.aggregate(Sum('pax')).get('pax__sum')
            if pax_in_transaction is None:
                return pax_from_requests
            return pax_from_requests - pax_in_transaction
        else:
            return pax_from_requests

    def within_expected_date(self):
        """
        :return: true if the current date precedes the expected date of the request,
                returns false otherwise
        """
        return timezone.now() <= self.expected_date
        # now = timezone.now()
        # return now - datetime.timedelta(days=1) <= self.pub_date <= now
        # return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class ItemRequest(models.Model):
    """
    Request made by or for a victim Note: Notice the use of 'for'. This is because this can be posted and tied to a
    barangay directly since victim_request is nullable
    """
    barangay_request = models.ForeignKey(to=BarangayRequest, on_delete=models.CASCADE, related_name='item_request')
    date_added = models.DateTimeField()
    type = models.ForeignKey(ItemType, on_delete=models.CASCADE, )
    pax = models.IntegerField()
    victim_request = models.OneToOneField(to='VictimRequest', on_delete=models.CASCADE,
                                          null=True, blank=True, )

    def is_by_barangay(self):
        """
        Check if the barangay made the request directly
        :return: True if it was made by a barangay, False if made by a victim
        """
        return self.victim_request is None


class VictimRequest(models.Model):
    # Nullable because this can be requested through the barangay
    resident = models.ForeignKey(to=ResidentProfile, on_delete=models.CASCADE,
                                 related_name='resident_requests', null=True, blank=True)


# Algorithm-related models
class RouteSuggestion(models.Model):
    # TODO: Add date/time?
    donor = models.ForeignKey(to=DonorProfile, on_delete=models.CASCADE,
                              related_name='route_donor', )


class RouteNode(models.Model):
    request = models.ForeignKey(to=BarangayRequest, on_delete=models.CASCADE,
                                related_name='request', )
    suggestion = models.ForeignKey(to=RouteSuggestion, on_delete=models.CASCADE, related_name='nodes')
    distance_from_prev = models.FloatField(null=True,)


class Fulfillment(models.Model):
    """Single item fulfillment connected to routenode"""
    node = models.ForeignKey(to=RouteNode, on_delete=models.CASCADE, )
    type = models.ForeignKey(to=ItemType, on_delete=models.CASCADE, )
    pax = models.IntegerField()
