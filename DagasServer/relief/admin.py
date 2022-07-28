from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from relief.models import User, Transaction, EvacuationCenter, BarangayProfile, DonorProfile, Donation, Supply, \
    BarangayRequest, ItemRequest, RouteNode, RouteSuggestion, Fulfillment, Disaster
# Guide: https://docs.djangoproject.com/en/4.0/ref/contrib/admin/
# 3.2 Guide: https://docs.djangoproject.com/en/3.2/ref/contrib/admin/
admin.site.register(User, UserAdmin)
admin.site.register(Transaction)
admin.site.register(BarangayProfile)
admin.site.register(DonorProfile)
admin.site.register(Donation)
admin.site.register(Supply)
admin.site.register(BarangayRequest)
admin.site.register(ItemRequest)
admin.site.register(RouteNode)
admin.site.register(RouteSuggestion)
admin.site.register(Fulfillment)
admin.site.register(Disaster)
admin.site.site_header = 'Dagas DSWD Administation System'


class EvacuationCenterAdmin(admin.ModelAdmin):
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},
    }


admin.site.register(EvacuationCenter, EvacuationCenterAdmin)
