from django.db.models import Sum, Count
from slick_reporting.decorators import report_field_register
from slick_reporting.fields import SlickReportField
from slick_reporting.views import SlickReportView

from relief.models import Supply, ItemRequest, Transaction, TransactionOrder


class SupplySummary(SlickReportView):
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
