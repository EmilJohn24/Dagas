import django.contrib.auth
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
# See management/commands/create_groups.py for list of groups
# TODO: Finish models
from django.db.models.signals import post_save
from django.dispatch import receiver

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


class BarangayProfile(models.Model):
    """
        User information exclusive to barangays
    """
    # TODO: Add geolocation and evacuation centers
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, related_name="barangay_profile")


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
    barangay = models.ForeignKey(to=BarangayProfile, on_delete=models.CASCADE, related_name="evacuating_barangay")
    evacuation_center = models.ForeignKey(to='EvacuationCenter', on_delete=models.CASCADE,
                                          related_name='evacuation_center')
    time_evacuated = models.DateTimeField()


class EvacuationCenter(models.Model):
    """
    Evacuation centers
    """
    # TODO: Add geolocation
    name = models.CharField(max_length=200)
    barangays = models.ManyToManyField(to=BarangayProfile, related_name='barangays_evacuation',
                                       through=EvacuationDetails)


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
