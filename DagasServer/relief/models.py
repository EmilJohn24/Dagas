import django.contrib.auth
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
# See management/commands/create_groups.py for list of groups
# TODO: Create models
from django.db.models.signals import post_save
from django.dispatch import receiver

from DagasServer import settings


# START User Management
# Use default user model

# User roles
# class Role(models.Model):
#     """
#         Defined user roles
#     """
#     RESIDENT = 1
#     DONOR = 2
#     BARANGAY = 3
#     GOVERNMENT_ADMIN = 4
#
#     ROLE_CHOICES = (
#         (RESIDENT, 'Resident'),
#         (DONOR, 'Donor'),
#         (BARANGAY, 'Barangay'),
#         (GOVERNMENT_ADMIN, 'Admin')
#     )
#
#     role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)


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

    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=RESIDENT)


# User Profiles
class ResidentProfile(models.Model):
    """
        User information exclusive to residents
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, related_name="resident_profile")


class DonorProfile(models.Model):
    """
        User information exclusive to donors
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, related_name="donor_profile")


class BarangayProfile(models.Model):
    """
        User information exclusive to donors
    """
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, related_name="barangay_profile")


class GovAdminProfile(models.Model):
    """
        User information exclusive to donors
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
    instance.save()


# END User Management
class Donation(models.Model):
    donor = models.ForeignKey(DonorProfile,
                              on_delete=models.CASCADE, )  # Removed: limit_choices_to={'groups__name': 'donors'})
    datetime_added = models.DateTimeField('Date added')


class ItemType(models.Model):
    name = models.CharField(max_length=250)


# TODO: Add some kind of type to Supply (e.g. Food, Water)
class Supply(models.Model):
    name = models.CharField(max_length=250)
    type = models.ForeignKey(ItemType, on_delete=models.CASCADE)
    quantity = models.IntegerField
    pax = models.IntegerField
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)


# TODO: Check if good models
class VictimRequest(models.Model):
    pass


class BarangayRequest(models.Model):
    pass
