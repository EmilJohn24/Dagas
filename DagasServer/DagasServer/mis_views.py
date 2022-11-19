from django.db.models import Sum, Count, Aggregate
from slick_reporting.decorators import report_field_register
from slick_reporting.fields import SlickReportField
from slick_reporting.form_factory import report_form_factory
from slick_reporting.views import SlickReportView

import relief.models
from relief.models import Supply, ItemRequest, Transaction, TransactionOrder, ItemType, BarangayRequest


@report_field_register
class AvailableAmountField(SlickReportField):
    name = 'available_pax'
    calculation_field = 'pax'
    verbose_name = 'Available Pax'

    def resolve(self, current_obj, current_row=None):
        current_obj = int(current_obj)
        supplies = Supply.objects.filter(type_id=current_obj)
        total = 0
        for supply in supplies:
            total += supply.calculate_available_pax()
        return total


class SupplySummary(SlickReportView):
    def get_form_class(self):
        def f_filter_func(fkey_maps):
            disaster_model = relief.models.DonorProfile._meta.get_field('current_disaster')
            fkey_maps['donor__current_disaster_id'] = disaster_model
            return fkey_maps

        return self.form_class or report_form_factory(self.get_report_model(), crosstab_model=self.crosstab_model,
                                                      display_compute_reminder=self.crosstab_compute_reminder,
                                                      excluded_fields=self.excluded_fields,
                                                      fkeys_filter_func=f_filter_func)

    report_model = Supply
    date_field = 'datetime_added'
    group_by = 'type'
    excluded_fields = ['donation_id', 'transaction_id', ]
    report_title = "Supply Summary"
    columns = ['name',
               SlickReportField.create(method=Sum, field='pax', name='pax__sum', verbose_name='Pax'),
               'available_pax',
               ]

    chart_settings = [
        {
            'type': 'pie',
            'data_source': ['pax__sum'],
            'title_source': 'name',
            'title': 'Supply Distribution',
            'plot_total': False,
        },
        {
            'type': 'pie',
            'data_source': ['available_pax'],
            'title_source': 'name',
            'title': 'Undelivered Supply Distribution',
            'plot_total': False,
        }, ]


class SupplySeries(SlickReportView):
    def get_form_class(self):
        def f_filter_func(fkey_maps):
            disaster_model = relief.models.DonorProfile._meta.get_field('current_disaster')
            fkey_maps['donor__current_disaster_id'] = disaster_model
            return fkey_maps

        return self.form_class or report_form_factory(self.get_report_model(), crosstab_model=self.crosstab_model,
                                                      display_compute_reminder=self.crosstab_compute_reminder,
                                                      excluded_fields=self.excluded_fields,
                                                      fkeys_filter_func=f_filter_func)

    report_model = Supply
    date_field = 'datetime_added'
    group_by = 'type'
    excluded_fields = ['donation_id', 'transaction_id', ]
    report_title = "Supply Summary"
    time_series_pattern = 'daily'
    time_series_columns = [
        SlickReportField.create(name='series_pax', field='pax', method=Sum, verbose_name='Pax per day')
    ]
    columns = ['name',
               SlickReportField.create(method=Sum, field='pax', name='pax__sum', verbose_name='Pax'),
               '__time_series__', ]

    chart_settings = [
        {
            'type': 'area',
            'data_source': ['series_pax'],
            'title_source': 'name',
            'title': 'Supplies',
        }, ]


@report_field_register
class UntransactedAmountField(SlickReportField):
    name = 'untransacted_pax'
    calculation_field = 'pax'
    verbose_name = 'Untransacted Pax'

    def resolve(self, current_obj, current_row=None):
        current_obj = int(current_obj)
        barangay_requests = BarangayRequest.objects.all()
        total = 0
        for barangay_request in barangay_requests:
            total += barangay_request.calculate_untransacted_pax(current_obj)
        return total


class RequestSummary(SlickReportView):
    def get_form_class(self):
        def f_filter_func(fkey_maps):
            disaster_model = relief.models.BarangayProfile._meta.get_field('current_disaster')
            fkey_maps['barangay_request__barangay__current_disaster_id'] = disaster_model
            barangay_model = relief.models.BarangayRequest._meta.get_field('barangay')
            fkey_maps['barangay_request__barangay_id'] = barangay_model
            return fkey_maps

        return self.form_class or report_form_factory(self.get_report_model(), crosstab_model=self.crosstab_model,
                                                      display_compute_reminder=self.crosstab_compute_reminder,
                                                      excluded_fields=self.excluded_fields,
                                                      fkeys_filter_func=f_filter_func)

    report_model = ItemRequest
    date_field = 'date_added'
    group_by = 'type'
    report_title = "Requests Summary"
    excluded_fields = ['barangay_request_id', 'victim_request_id', ]
    columns = ['name',
               SlickReportField.create(method=Sum, field='pax', name='pax__sum', verbose_name='Pax'),
               'untransacted_pax', ]

    chart_settings = [
        {
            'type': 'pie',
            'data_source': ['pax__sum'],
            'title_source': 'name',
            'title': 'Request Distribution',
            'plot_total': False,
        },
        {
            'type': 'pie',
            'data_source': ['untransacted_pax'],
            'title_source': 'name',
            'title': 'Unfulfilled Demand Distribution',
            'plot_total': False,
        },
    ]


class RequestSeries(SlickReportView):
    def get_form_class(self):
        def f_filter_func(fkey_maps):
            disaster_model = relief.models.BarangayProfile._meta.get_field('current_disaster')
            fkey_maps['barangay_request__barangay__current_disaster_id'] = disaster_model
            barangay_model = relief.models.BarangayRequest._meta.get_field('barangay')
            fkey_maps['barangay_request__barangay_id'] = barangay_model
            return fkey_maps

        return self.form_class or report_form_factory(self.get_report_model(), crosstab_model=self.crosstab_model,
                                                      display_compute_reminder=self.crosstab_compute_reminder,
                                                      excluded_fields=self.excluded_fields,
                                                      fkeys_filter_func=f_filter_func)

    report_model = ItemRequest
    date_field = 'date_added'
    group_by = 'type'
    excluded_fields = ['barangay_request_id', 'victim_request_id', ]
    report_title = "Requests Series"
    time_series_pattern = 'daily'
    time_series_columns = [
        SlickReportField.create(name='series_pax', field='pax', method=Sum, verbose_name='Pax per day')
    ]
    columns = ['name',
               SlickReportField.create(method=Sum, field='pax', name='pax__sum', verbose_name='Pax'),
               '__time_series__', ]

    chart_settings = [
        {
            'type': 'area',
            'data_source': ['series_pax'],
            'title_source': 'name',
            'title': 'Requests',
        }, ]


@report_field_register
class ItemTypeName(SlickReportField):
    name = 'item_type_name'
    calculation_field = 'supply__type'
    verbose_name = 'Item Type'

    def resolve(self, current_obj, current_row=None):
        current_obj = int(current_obj)
        return ItemType.objects.get(id=current_obj).name


class TransactionOrderSummary(SlickReportView):
    def get_form_class(self):
        def f_filter_func(fkey_maps):
            disaster_model = relief.models.BarangayProfile._meta.get_field('current_disaster')
            fkey_maps['transaction__barangay_request__barangay__current_disaster_id'] = disaster_model
            barangay_model = relief.models.BarangayRequest._meta.get_field('barangay')
            fkey_maps['transaction__barangay_request__barangay_id'] = barangay_model
            donor_model = relief.models.Transaction._meta.get_field('donor')
            fkey_maps['transaction__donor_id'] = donor_model
            type_model = relief.models.Supply._meta.get_field('type')
            fkey_maps['supply__type_id'] = type_model
            return fkey_maps

        return self.form_class or report_form_factory(self.get_report_model(), crosstab_model=self.crosstab_model,
                                                      display_compute_reminder=self.crosstab_compute_reminder,
                                                      excluded_fields=self.excluded_fields,
                                                      fkeys_filter_func=f_filter_func)

    report_model = TransactionOrder
    date_field = 'transaction__created_on'
    group_by = 'supply__type'
    excluded_fields = ['supply_id', 'transaction_id']
    report_title = "Transaction Order Summary"
    columns = ['item_type_name',
               SlickReportField.create(method=Sum, field='pax', name='pax__sum', verbose_name='Pax')]

    chart_settings = [
        {
            'type': 'pie',
            'data_source': ['pax__sum'],
            'title_source': 'item_type_name',
            'title': 'Transacted Order Distribution',
            'plot_total': False,
        }, ]


class TransactionOrderSeries(SlickReportView):
    def get_form_class(self):
        def f_filter_func(fkey_maps):
            disaster_model = relief.models.BarangayProfile._meta.get_field('current_disaster')
            fkey_maps['transaction__barangay_request__barangay__current_disaster_id'] = disaster_model
            barangay_model = relief.models.BarangayRequest._meta.get_field('barangay')
            fkey_maps['transaction__barangay_request__barangay_id'] = barangay_model
            donor_model = relief.models.Transaction._meta.get_field('donor')
            fkey_maps['transaction__donor_id'] = donor_model
            type_model = relief.models.Supply._meta.get_field('type')
            fkey_maps['supply__type_id'] = type_model
            return fkey_maps

        return self.form_class or report_form_factory(self.get_report_model(), crosstab_model=self.crosstab_model,
                                                      display_compute_reminder=self.crosstab_compute_reminder,
                                                      excluded_fields=self.excluded_fields,
                                                      fkeys_filter_func=f_filter_func)

    report_model = TransactionOrder
    date_field = 'transaction__created_on'
    group_by = 'supply__type'
    excluded_fields = ['supply_id', 'transaction_id']
    report_title = "Transaction Order Series"
    time_series_pattern = 'daily'
    time_series_columns = [
        SlickReportField.create(name='series_pax', field='pax', method=Sum, verbose_name='Pax per day')
    ]
    columns = ['item_type_name',
               SlickReportField.create(method=Sum, field='pax', name='pax__sum', verbose_name='Pax'), ]

    chart_settings = [
        {
            'type': 'area',
            'data_source': ['series_pax'],
            'title_source': 'item_type_name',
            'title': 'Transaction Orders Fulfilled',
        }
    ]


@report_field_register
class StatusNameField(SlickReportField):
    name = 'status'
    calculation_field = 'received'
    verbose_name = 'Status'

    def resolve(self, current_obj, current_row=None):
        current_obj = int(current_obj)
        if current_obj == Transaction.PACKAGING:
            return "Packaging"
        elif current_obj == Transaction.INCOMING:
            return "Incoming"
        elif current_obj == Transaction.RECEIVED:
            return "Received"
        else:
            return "None"


class TransactionSummary(SlickReportView):
    def get_form_class(self):
        def f_filter_func(fkey_maps):
            disaster_model = relief.models.BarangayProfile._meta.get_field('current_disaster')
            fkey_maps['barangay_request__barangay__current_disaster_id'] = disaster_model
            barangay_model = relief.models.BarangayRequest._meta.get_field('barangay')
            fkey_maps['barangay_request__barangay_id'] = barangay_model
            return fkey_maps

        return self.form_class or report_form_factory(self.get_report_model(), crosstab_model=self.crosstab_model,
                                                      display_compute_reminder=self.crosstab_compute_reminder,
                                                      excluded_fields=self.excluded_fields,
                                                      fkeys_filter_func=f_filter_func)

    report_model = Transaction
    date_field = 'created_on'
    group_by = 'received'
    report_title = "Transaction Status"
    columns = ['status',
               SlickReportField.create(method=Count, field='received', name='count', verbose_name='Pax'), ]
    excluded_fields = ['barangay_request_id']
    chart_settings = [
        {
            'type': 'pie',
            'data_source': ['count'],
            'title_source': 'status',
            'title': 'Transaction Distribution',
            'plot_total': False,
        }, ]
