from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from relief.models import User, Transaction, EvacuationCenter, BarangayProfile, DonorProfile, Donation, Supply, \
    BarangayRequest, ItemRequest

admin.site.register(User, UserAdmin)
admin.site.register(Transaction)
admin.site.register(BarangayProfile)
admin.site.register(DonorProfile)
admin.site.register(Donation)
admin.site.register(Supply)
admin.site.register(BarangayRequest)
admin.site.register(ItemRequest)


class EvacuationCenterAdmin(admin.ModelAdmin):
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},
    }


admin.site.register(EvacuationCenter, EvacuationCenterAdmin)
