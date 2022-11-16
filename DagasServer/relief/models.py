from time import time
import uuid
from datetime import datetime, timedelta
from io import StringIO

import django.contrib.auth
import qrcode
from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
# See management/commands/create_groups.py for list of groups
# TODO: Finish models
from django.db.models import Sum
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django_google_maps import fields as map_fields
from notifications.signals import notify
from queryable_properties.properties import queryable_property

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
    current_disaster = models.ForeignKey(to="Disaster", on_delete=models.CASCADE, related_name='donors',
                                         null=True, blank=True)

    def __str__(self):
        return self.user.username


class BarangayProfile(models.Model):
    """
        User information exclusive to barangays
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, related_name="barangay_profile")
    current_disaster = models.ForeignKey(to='Disaster', on_delete=models.CASCADE, related_name='barangays',
                                         null=True, blank=True)

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


@receiver(post_save, sender=BarangayProfile)
def notify_residents_disaster(sender, instance, created, **kwargs):
    barangay = instance
    if barangay.current_disaster is None or not barangay.current_disaster.ongoing:
        return
    resident_users = User.objects.filter(resident_profile__barangay=barangay)
    notif_verb = "Disaster Declaration"
    notif_message = 'Your barangay has been declared under ' + str(barangay.current_disaster)
    notify.send(sender=barangay.user, recipient=resident_users, target=barangay.current_disaster,
                verb=notif_verb, description=notif_message)


# END User Management
class Disaster(models.Model):
    name = models.CharField(max_length=200)
    ongoing = models.BooleanField(default=True)
    date_started = models.DateTimeField(default=timezone.now)
    date_ended = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


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


def supply_image_path(instance, filename):
    return 'supply/id_{0}/{1}'.format(instance.id, filename)


# TODO: Add some kind of type to Supply (e.g. Food, Water)
class Supply(models.Model):
    name = models.CharField(max_length=250)
    type = models.ForeignKey(ItemType, on_delete=models.CASCADE, related_name='supplies')
    quantity = models.IntegerField()
    pax = models.IntegerField()
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='supplies', null=True, blank=True, )
    transaction = models.ForeignKey(to="Transaction", on_delete=models.CASCADE, related_name='transaction_supply',
                                    null=True)
    picture = models.ImageField(null=True, blank=True, upload_to=supply_image_path)
    donor = models.ForeignKey(to="DonorProfile", on_delete=models.CASCADE,
                              related_name='donor_supplies', null=True, blank=True, )
    datetime_added = models.DateTimeField('Date added', null=True, default=datetime.now, )

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

    class Meta:
        verbose_name_plural = 'supplies'


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
    # TODO: Use auto_add_now and remove at serializer level
    # Link: https://stackoverflow.com/questions/3429878/automatic-creation-date-for-django-model-form-objects
    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    barangay_request = models.ForeignKey(to="BarangayRequest", on_delete=models.CASCADE)
    received = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, null=True,
                                                blank=True)  # 1 = received, 0 = not received
    received_date = models.DateTimeField(null=True)

    # Constants
    EXPIRATION_TIME_HRS = 24

    def status_string(self):
        if self.is_expired():
            return "Expired"
        if self.received == Transaction.PACKAGING:
            return "Packaging"
        if self.received == Transaction.INCOMING:
            return "Incoming"
        if self.received == Transaction.RECEIVED:
            return "Received"

    def is_expired(self):
        timespan = datetime.now(timezone.utc) - self.created_on
        timespan_hrs = timespan.seconds / 60 / 60
        # If the transaction has already been received, it clearly cannot be expired
        if self.received == Transaction.RECEIVED:
            return False
        else:
            return timespan_hrs >= self.EXPIRATION_TIME_HRS

    def __str__(self):
        return str(self.barangay_request) + " " + str(self.id)

    def save(self, *args, **kwargs):
        if self._state.adding:
            filename = 'qr_%s.png' % self.id
            qr_code_file = ContentFile(b'', name=filename)
            img = qrcode.make(str(self.id))
            img.save(qr_code_file)
            self.qr_code = qr_code_file
        if self.received == Transaction.RECEIVED and self.received is None:
            self.received_date = datetime.now(timezone.utc)
        super(Transaction, self).save(*args, **kwargs)


def transaction_img_path(instance, filename):
    return 'transactions/id_{0}/{1}'.format(instance.transaction.id, filename)


# @receiver(post_save, sender=Transaction)
# def update_received_date(sender, instance, created, **kwargs):
#     # post_save.disconnect(update_received_date, )
#     if instance.received == Transaction.RECEIVED and instance.received is None:
#         instance.received_date = timezone.now(timezone.utc)
#     instance.save()


class TransactionImage(models.Model):
    image = models.ImageField(null=True, upload_to=transaction_img_path)
    transaction = models.ForeignKey(to=Transaction, on_delete=models.CASCADE, related_name='transaction_image')


class BarangayRequest(models.Model):
    barangay = models.ForeignKey(null=True, to=BarangayProfile, on_delete=models.CASCADE)
    evacuation_center = models.ForeignKey(null=True, to=EvacuationCenter, on_delete=models.CASCADE)
    details = models.ForeignKey(null=True, to=EvacuationDetails,
                                on_delete=models.CASCADE)  # contains both the barangay and the evac center
    # TODO: Add own disaster field (since BarangayProfile's disaster can change)
    # TODO: Add check
    expected_date = models.DateTimeField(null=True, default=datetime.now)

    # TODO: Add field for date created
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

    def is_finished(self):
        for item_type in ItemType.objects.all():
            if self.calculate_untransacted_pax(item_type) > 0:
                return False
        return True

    def is_handled(self):
        for item_type in ItemType.objects.all():
            if self.calculate_untransacted_pax(item_type) - \
                    self.calculate_suggested_pax(item_type) > 0:
                return False
        return True

    def calculate_suggested_pax(self, item_type: ItemType):
        """Returns the number of pax for item_type that has been suggested to others"""
        # Unaccepted route nodes: Filters out accepted suggestions to
        # prevent calculation conflict with calculate_untransacted_pax
        # This also filters out expired requests
        request_nodes = RouteNode.objects.filter(request=self).filter(suggestion__accepted=False) \
            .filter(suggestion__expiration_time__gte=datetime.now(timezone.utc))
        item_fulfillments = Fulfillment.objects.filter(node__in=request_nodes).filter(type=item_type)
        if len(item_fulfillments) > 0:
            return item_fulfillments.aggregate(Sum('pax')).get('pax__sum')
        else:
            return 0

    def calculate_untransacted_pax(self, item_type: ItemType):
        type_requests = ItemRequest.objects.filter(barangay_request=self)
        type_requests = type_requests.filter(type=item_type)
        transaction_orders = TransactionOrder.objects.filter(transaction__barangay_request=self)
        transaction_orders = transaction_orders.filter(supply__type=item_type)
        pax_from_requests = 0
        if not len(type_requests) == 0:
            pax_from_requests = type_requests.aggregate(Sum('pax')).get('pax__sum')
        else:
            return 0

        if not len(transaction_orders) == 0:
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
        return datetime.now(timezone.utc) <= self.expected_date
        # now = timezone.now()
        # return now - datetime.timedelta(days=1) <= self.pub_date <= now
        # return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class ItemRequest(models.Model):
    """
    Request made by or for a victim Note: Notice the use of 'for'. This is because this can be posted and tied to a
    barangay directly since victim_request is nullable
    """
    barangay_request = models.ForeignKey(to=BarangayRequest, on_delete=models.CASCADE, related_name='item_request')
    # TODO: Change to auto_now_add and remove automation in serialization
    # Link: https://stackoverflow.com/questions/3429878/automatic-creation-date-for-django-model-form-objects
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

    @property
    def untransacted_pax(self):
        transaction_orders = TransactionOrder.objects.filter(transaction__barangay_request=self)
        transaction_orders = transaction_orders.filter(supply__type=self.type)
        if not len(transaction_orders) == 0:
            pax_in_transaction = transaction_orders.aggregate(Sum('pax')).get('pax__sum')
            if pax_in_transaction is None:
                return self.pax
            return self.pax - pax_in_transaction
        else:
            return self.pax


class VictimRequest(models.Model):
    # Nullable because this can be requested through the barangay
    resident = models.ForeignKey(to=ResidentProfile, on_delete=models.CASCADE,
                                 related_name='resident_requests', null=True, blank=True)


class TransactionStub(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code = models.ImageField(upload_to='resident_stub_QRs', blank=True, null=True)
    request = models.ForeignKey(to=BarangayRequest, on_delete=models.CASCADE, blank=True, null=True)
    resident = models.ForeignKey(to=ResidentProfile, on_delete=models.CASCADE)
    received = models.BooleanField(default=False)
    # TODO: Change to auto_now_add and remove automation in serialization
    # Link: https://stackoverflow.com/questions/3429878/automatic-creation-date-for-django-model-form-objects
    created_on = models.DateTimeField(default=datetime.now, blank=True, null=True)

    # Constants
    EXPIRATION_TIME_HRS = 48

    def is_expired(self):
        # Fix based on: https://stackoverflow.com/questions/796008/cant-subtract-offset-naive-and-offset-aware-datetimes/25662061#25662061
        timespan = datetime.now(timezone.utc) - self.created_on
        timespan_hrs = timespan.seconds / 60 / 60
        return timespan_hrs >= self.EXPIRATION_TIME_HRS

    def save(self, *args, **kwargs):
        if self._state.adding:
            filename = 'qr_%s.png' % self.id
            qr_code_file = ContentFile(b'', name=filename)
            img = qrcode.make('*' + str(self.id))  # Add an asterisk (*) to differentiate it from Transaction QRs
            img.save(qr_code_file)
            self.qr_code = qr_code_file

        super(TransactionStub, self).save(*args, **kwargs)


@receiver(post_save, sender=BarangayRequest)
def generate_transaction_stubs(sender, instance, created, **kwargs):
    # TODO: Consider doing this in a Celery task
    if created:
        barangay = instance.barangay
        resident_profiles = ResidentProfile.objects.filter(barangay=barangay)

        for resident_profile in resident_profiles:
            TransactionStub.objects.create(request=instance, resident=resident_profile)
            notif_verb = "New Request Created"
            notif_message = "Your barangay has filed a new request"
            notify.send(sender=barangay.user, recipient=resident_profile.user, target=instance,
                        verb=notif_verb, description=notif_message)


@receiver(pre_save, sender=ResidentProfile)
def resident_brgy_change_transaction_stub_handler(sender, instance, **kwargs):
    if instance.id is not None:
        previous_resident_state = ResidentProfile.objects.get(id=instance.id)
        if previous_resident_state.barangay != instance.barangay and instance.barangay is not None:
            for request in BarangayRequest.objects.filter(barangay=instance.barangay):
                TransactionStub.objects.create(request=request, resident=instance)
                notif_verb = "New Request Created"
                notif_message = "Your barangay has filed a new request"
                notify.send(sender=instance.barangay.user, recipient=instance.user, target=request,
                            verb=notif_verb, description=notif_message)


class Rating(models.Model):
    resident = models.ForeignKey(to=ResidentProfile, on_delete=models.CASCADE,
                                 related_name='ratings')
    barangay = models.ForeignKey(to=BarangayProfile, on_delete=models.CASCADE,
                                 related_name='ratings')
    disaster = models.ForeignKey(to=Disaster, on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])


# Algorithm-related models
class AlgorithmExecution(models.Model):
    donor = models.ForeignKey(to=DonorProfile, on_delete=models.CASCADE, related_name='requesting_donor')
    time_started = models.DateTimeField(auto_now_add=True)
    time_modified = models.DateTimeField(auto_now=True)
    result = models.ForeignKey(to='RouteSuggestion', on_delete=models.CASCADE, related_name='suggestion', null=True)

    def has_result(self):
        return self.result is not None


class RouteSuggestion(models.Model):
    # TODO: Add date/time?
    donor = models.ForeignKey(to=DonorProfile, on_delete=models.CASCADE,
                              related_name='route_donor', )
    accepted = models.BooleanField(default=False)
    # Reserve for 15 minutes only
    expiration_time = models.DateTimeField(editable=False, null=True, blank=True, )

    def is_expired(self):
        return datetime.now(timezone.utc) > self.expiration_time and not self.accepted

    def save(self, *args, **kwargs):
        if not self.id:
            self.expiration_time = datetime.now(timezone.utc) + timedelta(minutes=15)
        return super(RouteSuggestion, self).save(*args, **kwargs)


class RouteNode(models.Model):
    request = models.ForeignKey(to=BarangayRequest, on_delete=models.CASCADE,
                                related_name='request', )
    suggestion = models.ForeignKey(to=RouteSuggestion, on_delete=models.CASCADE, related_name='nodes')
    distance_from_prev = models.FloatField(null=True, )


class Fulfillment(models.Model):
    """Single item fulfillment connected to routenode"""
    node = models.ForeignKey(to=RouteNode, on_delete=models.CASCADE, )
    type = models.ForeignKey(to=ItemType, on_delete=models.CASCADE, )
    pax = models.IntegerField()
