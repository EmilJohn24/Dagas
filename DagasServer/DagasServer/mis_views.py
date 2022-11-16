from django.db.models import Sum, Count
from slick_reporting.decorators import report_field_register
from slick_reporting.fields import SlickReportField
from slick_reporting.form_factory import report_form_factory
from slick_reporting.views import SlickReportView

import relief.models
from relief.models import Supply, ItemRequest, Transaction, TransactionOrder


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
    report_title = "Supply Summary"
    columns = ['name',
               SlickReportField.create(method=Sum, field='pax', name='pax__sum', verbose_name='Pax'),
               '__time_series__', ]

    chart_settings = [
        {
            'type': 'pie',
            'data_source': ['pax__sum'],
            'title_source': 'name',
            'title': 'Supply Distribution',
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


class RequestSummary(SlickReportView):
    def get_form_class(self):
        def f_filter_func(fkey_maps):
            disaster_model = relief.models.BarangayProfile._meta.get_field('current_disaster')
            fkey_maps['barangay_request__barangay__current_disaster_id'] = disaster_model
            return fkey_maps
        return self.form_class or report_form_factory(self.get_report_model(), crosstab_model=self.crosstab_model,
                                                      display_compute_reminder=self.crosstab_compute_reminder,
                                                      excluded_fields=self.excluded_fields,
                                                      fkeys_filter_func=f_filter_func)
    report_model = ItemRequest
    date_field = 'date_added'
    group_by = 'type'
    report_title = "Requests Summary"
    columns = ['name',
               SlickReportField.create(method=Sum, field='pax', name='pax__sum', verbose_name='Pax'),
               '__time_series__', ]

    chart_settings = [
        {
            'type': 'pie',
            'data_source': ['pax__sum'],
            'title_source': 'name',
            'title': 'Request Distribution',
            'plot_total': False,
        }, ]


class RequestSeries(SlickReportView):
    def get_form_class(self):
        def f_filter_func(fkey_maps):
            disaster_model = relief.models.BarangayProfile._meta.get_field('current_disaster')
            fkey_maps['barangay_request__barangay__current_disaster_id'] = disaster_model
            return fkey_maps
        return self.form_class or report_form_factory(self.get_report_model(), crosstab_model=self.crosstab_model,
                                                      display_compute_reminder=self.crosstab_compute_reminder,
                                                      excluded_fields=self.excluded_fields,
                                                      fkeys_filter_func=f_filter_func)
    report_model = ItemRequest
    date_field = 'date_added'
    group_by = 'type'
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


class TransactionOrderSummary(SlickReportView):
    def get_form_class(self):
        def f_filter_func(fkey_maps):
            disaster_model = relief.models.BarangayProfile._meta.get_field('current_disaster')
            fkey_maps['transaction__barangay_request__barangay__current_disaster_id'] = disaster_model
            return fkey_maps
        return self.form_class or report_form_factory(self.get_report_model(), crosstab_model=self.crosstab_model,
                                                      display_compute_reminder=self.crosstab_compute_reminder,
                                                      excluded_fields=self.excluded_fields,
                                                      fkeys_filter_func=f_filter_func)
    report_model = TransactionOrder
    date_field = 'transaction__created_on'
    group_by = 'supply__type'
    report_title = "Transaction Order Summary"
    columns = [SlickReportField.create(method=Sum, field='pax', name='pax__sum', verbose_name='Pax'),
               '__time_series__', ]

    chart_settings = [
        {
            'type': 'pie',
            'data_source': ['pax__sum'],
            'title_source': 'name',
            'title': 'Transacted Order Distribution',
            'plot_total': False,
        }, ]


class TransactionOrderSeries(SlickReportView):
    def get_form_class(self):
        def f_filter_func(fkey_maps):
            disaster_model = relief.models.BarangayProfile._meta.get_field('current_disaster')
            fkey_maps['transaction__barangay_request__barangay__current_disaster_id'] = disaster_model
            return fkey_maps
        return self.form_class or report_form_factory(self.get_report_model(), crosstab_model=self.crosstab_model,
                                                      display_compute_reminder=self.crosstab_compute_reminder,
                                                      excluded_fields=self.excluded_fields,
                                                      fkeys_filter_func=f_filter_func)
    report_model = TransactionOrder
    date_field = 'transaction__created_on'
    group_by = 'supply__type'
    report_title = "Transaction Order Series"
    time_series_pattern = 'daily'
    time_series_columns = [
        SlickReportField.create(name='series_pax', field='pax', method=Sum, verbose_name='Pax per day')
    ]
    columns = [SlickReportField.create(method=Sum, field='pax', name='pax__sum', verbose_name='Pax'),
               '__time_series__', ]

    chart_settings = [
        {
            'type': 'area',
            'data_source': ['series_pax'],
            'title_source': 'name',
            'title': 'Transaction Orders Fulfilled',
        }
    ]


class TransactionSummary(SlickReportView):
    def get_form_class(self):
        def f_filter_func(fkey_maps):
            disaster_model = relief.models.BarangayProfile._meta.get_field('current_disaster')
            fkey_maps['barangay_request__barangay__current_disaster_id'] = disaster_model
            return fkey_maps
        return self.form_class or report_form_factory(self.get_report_model(), crosstab_model=self.crosstab_model,
                                                      display_compute_reminder=self.crosstab_compute_reminder,
                                                      excluded_fields=self.excluded_fields,
                                                      fkeys_filter_func=f_filter_func)
    report_model = Transaction
    date_field = 'created_on'
    group_by = 'received'
    report_title = "Transaction Status"
    columns = [SlickReportField.create(method=Count, field='received', name='count', verbose_name='Pax'),
               '__time_series__', ]

    chart_settings = [
        {
            'type': 'pie',
            'data_source': ['count'],
            'title_source': 'name',
            'title': 'Transaction Distribution',
            'plot_total': False,
        }, ]
