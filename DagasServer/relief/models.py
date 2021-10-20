from django.contrib.auth.models import User
from django.db import models


# Create your models here.
# See management/commands/create_groups.py for list of groups
# TODO: Create models

class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'groups__name': 'donors'})
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
