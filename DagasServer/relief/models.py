import django.contrib.auth
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
# See management/commands/create_groups.py for list of groups
# TODO: Create models
from DagasServer import settings


# Use default user model
class User(AbstractUser):
    pass


class Donation(models.Model):
    donor = models.ForeignKey(get_user_model(),
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
