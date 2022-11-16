from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields

from DagasServer.mis_views import SupplySeries, SupplySummary, RequestSeries, RequestSummary, TransactionOrderSeries, \
    TransactionOrderSummary, TransactionSummary
from relief.models import AlgorithmExecution, TransactionOrder, User, Transaction, EvacuationCenter, BarangayProfile, \
    DonorProfile, Donation, Supply, \
    BarangayRequest, ItemRequest, RouteNode, RouteSuggestion, Fulfillment, Disaster, ResidentProfile, TransactionStub, \
    AlgorithmExecution

# Guide: https://docs.djangoproject.com/en/4.0/ref/contrib/admin/
# 3.2 Guide: https://docs.djangoproject.com/en/3.2/ref/contrib/admin/
# admin.site.register(User, UserAdmin)
admin.site.site_header = 'Dagas DSWD Administation System'


class BarangayInline(admin.TabularInline):
    model = BarangayProfile
    fields = ('user',)


class DisasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_barangays_affected_count')
    inlines = [
        BarangayInline,
    ]

    @admin.display(description='Barangay Count')
    def get_barangays_affected_count(self, obj):
        return len(BarangayProfile.objects.filter(current_disaster=obj))


class EvacuationCenterAdmin(admin.ModelAdmin):
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},
    }
    list_display = ('name', 'barangays', 'address')


class ItemRequestInline(admin.TabularInline):
    model = ItemRequest
    fields = ('type', 'pax',)


class BarangayRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'barangay', 'evacuation_center',)
    inlines = [
        ItemRequestInline,
    ]


class ProfileAdmin(UserAdmin):
    list_filter = ('role', 'is_staff',)


class DonorInline(admin.TabularInline):
    model = Supply
    fields = ('id', 'name', 'type',
              'pax',)
    readonly_fields = ('calculate_available_pax',)


class DonorAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_disaster',)
    inlines = [
        DonorInline,
    ]


class BarangayAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_disaster',)


class TransactionStubInline(admin.TabularInline):
    model = TransactionStub


class ResidentAdmin(admin.ModelAdmin):
    list_display = ('user', 'barangay', 'get_current_disaster')
    inlines = [
        TransactionStubInline,
    ]

    @admin.display(ordering='barangay__current_disaster__name', description='Disaster')
    def get_current_disaster(self, obj):
        if obj.barangay and obj.barangay.current_disaster:
            return obj.barangay.current_disaster.name


class SupplyAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'quantity', 'pax', 'calculate_available_pax', 'donation',)
    list_filter = ('type',)


class TransactionOrderInline(admin.TabularInline):
    model = TransactionOrder
    fields = ('id', 'supply', 'pax',)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_donor', 'get_barangay', 'get_disaster', 'created_on', 'status_string', 'received_date')

    @admin.display(ordering='barangay_request__barangay__current_disaster', description='Disaster')
    def get_disaster(self, obj):
        return obj.barangay_request.barangay.current_disaster

    @admin.display(ordering='barangay_request__barangay', description='Barangay')
    def get_barangay(self, obj):
        return obj.barangay_request.barangay

    @admin.display(ordering='donor__user', description='Donor')
    def get_donor(self, obj):
        return obj.donor.user

    inlines = [
        TransactionOrderInline,
    ]


admin.site.register_view('supply-series', 'Supply Trend', visible=True, view=SupplySeries.as_view())
admin.site.register_view('supply-summary', 'Supply Summary', visible=True, view=SupplySummary.as_view())
admin.site.register_view('request-series', 'Request Trend', visible=True, view=RequestSeries.as_view())
admin.site.register_view('request-summary', 'Request Summary', visible=True, view=RequestSummary.as_view())
admin.site.register_view('order-summary', 'Order Trend', visible=True, view=TransactionOrderSeries.as_view())
admin.site.register_view('order-series', 'Order Summary', visible=True, view=TransactionOrderSummary.as_view())
admin.site.register_view('transaction-summary', 'Transactions', visible=True, view=TransactionSummary.as_view())
admin.site.register(AlgorithmExecution)
admin.site.register(TransactionStub)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionOrder)
admin.site.register(BarangayProfile, BarangayAdmin)
admin.site.register(DonorProfile, DonorAdmin)
admin.site.register(ResidentProfile, ResidentAdmin)
admin.site.register(Donation)
admin.site.register(Supply, SupplyAdmin)
admin.site.register(BarangayRequest, BarangayRequestAdmin)
admin.site.register(ItemRequest)
admin.site.register(RouteNode)
admin.site.register(RouteSuggestion)
admin.site.register(Fulfillment)
admin.site.register(Disaster, DisasterAdmin)
admin.site.register(User, ProfileAdmin)
admin.site.register(EvacuationCenter, EvacuationCenterAdmin)
