from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from relief.models import AlgorithmExecution, TransactionOrder, User, Transaction, EvacuationCenter, BarangayProfile, DonorProfile, Donation, Supply, \
    BarangayRequest, ItemRequest, RouteNode, RouteSuggestion, Fulfillment, Disaster, ResidentProfile, TransactionStub, AlgorithmExecution

# Guide: https://docs.djangoproject.com/en/4.0/ref/contrib/admin/
# 3.2 Guide: https://docs.djangoproject.com/en/3.2/ref/contrib/admin/
# admin.site.register(User, UserAdmin)
admin.site.site_header = 'Dagas DSWD Administation System'


class EvacuationCenterAdmin(admin.ModelAdmin):
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},
    }
    list_display = ('name', 'barangays', 'address')

class BarangayRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'barangay', 'evacuation_center',)

class ProfileAdmin(UserAdmin):
    list_filter = ('role', 'is_staff',)


class DonorAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_disaster',)


class SupplyAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'quantity', 'pax', 'calculate_available_pax', 'donation',)
    list_filter = ('type',)

admin.site.register(AlgorithmExecution)
admin.site.register(TransactionStub)
admin.site.register(Transaction)
admin.site.register(TransactionOrder)
admin.site.register(BarangayProfile)
admin.site.register(DonorProfile, DonorAdmin)
admin.site.register(ResidentProfile)
admin.site.register(Donation)
admin.site.register(Supply, SupplyAdmin)
admin.site.register(BarangayRequest, BarangayRequestAdmin)
admin.site.register(ItemRequest)
admin.site.register(RouteNode)
admin.site.register(RouteSuggestion)
admin.site.register(Fulfillment)
admin.site.register(Disaster)
admin.site.register(User, ProfileAdmin)
admin.site.register(EvacuationCenter, EvacuationCenterAdmin)
