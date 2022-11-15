from django.db.models import Sum
from slick_reporting.decorators import report_field_register
from slick_reporting.fields import SlickReportField
from slick_reporting.views import SlickReportView

from relief.models import Supply


@report_field_register
class AvailablePaxField(SlickReportField):
    name = 'available_pax'
    calculation_field = 'calculate_available_pax'
    type = 'number'
    method = Sum
    verbose_name = 'Available Pax'


class SupplySummary(SlickReportView):
    report_model = Supply
    date_field = 'datetime_added'
    group_by = 'type'
    report_title = "Supply Summary"
    columns = ['name',
               'available_pax', ]
    chart_settings = [{
        'type': 'column',
        'data_source': ['available_pax'],
        'plot_total': False,
        'title_source': 'title',
        'title': 'Supplies',

    }, ]
