from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import viewsets
from rest_framework.routers import SimpleRouter

from DagasServer import settings
from . import views
from .forms import User
from .models import ResidentProfile
from .serializers import UserSerializer, ResidentSerializer

# Settings
from .viewsets import UserViewSet, ResidentViewSet, SupplyViewSet, ItemTypeViewSet, ItemRequestViewSet, \
    TransactionViewSet, BarangayRequestViewSet, BarangayViewSet, DonationViewSet, EvacuationCenterViewSet, \
    TransactionOrderViewSet, UserLocationViewSet, RouteSuggestionViewSet, NotificationViewSet, DisasterViewSet, \
    DonorViewSet

USE_ROUTER = True

app_name = 'relief'
# TODO: Add URLs (Format: path('dir/', view, name="name")
urlpatterns = [
    # path('api/users/', view=views.UserListView.as_view(), name='users'),
    # path('api/users/<int:pk>/', views.UserDetailView.as_view(), name='user_details'),
    path('api/users/residents/', views.ResidentListView.as_view(), name='residents'),
    path('api/users/admins/', views.GovAdminListView.as_view(), name='admins'),
    path('api/users/donors/', views.DonorListView.as_view(), name='donors'),
    path('api/users/donors/<int:pk>', views.DonorDetailView.as_view(), name='donor_details'),
    # path('api/donations/', views.DonationListView.as_view(), name='donations'),
    path('api/donations/<int:pk>', views.DonationDetailView.as_view(), name='donations_details'),
]


# view sets and router

router = SimpleRouter()
router.register('api/supplies', SupplyViewSet)
router.register('api/item-type', ItemTypeViewSet, basename='itemtype')
router.register('api/item-request', ItemRequestViewSet, basename='item_request')
router.register('api/requests', BarangayRequestViewSet, basename='barangay_request')
router.register('api/transactions', TransactionViewSet, basename='transactions')
router.register('api/users/residents/r', ResidentViewSet, basename='residents_others')
router.register('api/users/barangays', BarangayViewSet, basename='barangays')
router.register('api/users/donors/r', DonorViewSet, basename='donor_alt')
router.register('api/users', viewset=UserViewSet, basename='users')
router.register('api/user-location', viewset=UserLocationViewSet, basename='user-locations')
router.register('api/donations', DonationViewSet, basename='donations')
router.register('api/evacuation-center', EvacuationCenterViewSet, basename='evac_center')
router.register('api/transaction-order', TransactionOrderViewSet, basename='transaction_orders')
router.register('api/suggestions', RouteSuggestionViewSet, basename='suggestions')
router.register('api/notifications', NotificationViewSet, basename='notifications')
router.register('api/disasters', DisasterViewSet, basename='disasters')
urlpatterns += router.urls
