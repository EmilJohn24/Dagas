from django.db.models import Sum
from slick_reporting.decorators import report_field_register
from slick_reporting.fields import SlickReportField
from slick_reporting.views import SlickReportView

from relief.models import Supply


@report_field_register
class AvailablePaxField(SlickReportField):
    name = 'pax'
    calculation_field = 'pax'
    type = 'number'
    method = Sum
    verbose_name = 'Total Pax'


class SupplySummary(SlickReportView):
    report_model = Supply
    date_field = 'datetime_added'
    group_by = 'type'
    report_title = "Supply Summary"
    time_series_pattern = 'daily'
    time_series_columns = [
        SlickReportField.create(name='pax__sum', field='quantity', method=Sum, verbose_name='Pax per day')
    ]
    columns = ['name',
               SlickReportField.create(method=Sum, field='pax', name='pax__sum', verbose_name='Pax'),
               '__time_series__', ]

    chart_settings = [
        {
            'type': 'pie',
            'data_source': ['pax__sum'],
            'title': 'Supply Distribution',
            'plot_total': False,
        },
        {
            'type': 'column',
            'data_source': ['pax__sum'],
            'title_source': 'title',
            'title': 'Supplies',
        }, ]
