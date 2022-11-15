"""DagasServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
import notifications.urls
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from DagasServer import settings
from DagasServer.mis_views import SupplySummary, SupplySeries, RequestSummary, RequestSeries, TransactionOrderSeries, \
    TransactionOrderSummary

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin_tools_stats/', include('admin_tools_stats.urls')),
    # Graphs
    path('supply-series', SupplySeries.as_view()),
    path('supply-summary', SupplySummary.as_view()),
    path('request-series', RequestSeries.as_view()),
    path('request-summary', RequestSummary.as_view()),
    path('order-series', TransactionOrderSeries.as_view()),
    path('order-summary', TransactionOrderSummary.as_view()),
    # End Graphs
    path('relief/', include('relief.urls')),
    path('api-auth/', include('rest_framework.urls')),
    # path('api/rest-auth', include('rest_auth.urls')),
    path('api/rest-auth/registration', include('rest_auth.registration.urls')),
    path('api/rest-auth', include('dj_rest_auth.urls')),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),

    # API tokens
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
