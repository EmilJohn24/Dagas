from datetime import datetime

import django.contrib.auth
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
# See management/commands/create_groups.py for list of groups
# TODO: Finish models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from DagasServer import settings


# START User Management
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


# User Profiles
def resident_id_path(instance, filename):
    return 'resident/id_{0}/{1}'.format(instance.user.id, filename)


class ResidentProfile(models.Model):
    """
        User information exclusive to residents
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, related_name="resident_profile")
    # TODO: Add Pillow library to support ImageField
    gov_id = models.ImageField(null=True, upload_to=resident_id_path)


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
    barangays = models.ManyToManyField(to=BarangayProfile, related_name='centers',
                                       through=EvacuationDetails)


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

    def is_ongoing(self) -> bool:
        """
        :return: True if the supply is included in a Transaction
        """
        return self.transaction is not None

    def __str__(self) -> str:
        return self.name


# TODO: Check if good models

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

    donor = models.ForeignKey(to=DonorProfile, on_delete=models.CASCADE)
    barangay_request = models.ForeignKey(to="BarangayRequest", on_delete=models.CASCADE)
    received = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, null=True,
                                                blank=True)  # 1 = received, 0 = not received
    received_date = models.DateTimeField(null=True)


def transaction_img_path(instance, filename):
    return 'transactions/id_{0}/{1}'.format(instance.transaction.id, filename)


class TransactionImage(models.Model):
    image = models.ImageField(null=True, upload_to=transaction_img_path)
    transaction = models.ForeignKey(to=Transaction, on_delete=models.CASCADE, related_name='transaction_image')


class BarangayRequest(models.Model):
    barangay = models.ForeignKey(null=True, to=BarangayProfile, on_delete=models.CASCADE)
    details = models.ForeignKey(null=True, to=EvacuationDetails,
                                on_delete=models.CASCADE)  # contains both the barangay and the evac center
    expected_date = models.DateTimeField(null=True, default=datetime.now)

    def __str__(self):
        return self.barangay.user.username + " (" + str(self.id) + ")"

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
