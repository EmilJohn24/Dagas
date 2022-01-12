from django.urls import path, include
from rest_framework import viewsets
from rest_framework.routers import SimpleRouter

from . import views
from .forms import User
from .models import ResidentProfile
from .serializers import UserSerializer, ResidentSerializer

# Settings
from .viewsets import UserViewSet, ResidentViewSet, SupplyViewSet, ItemTypeViewSet, ItemRequestViewSet, \
    TransactionViewSet, BarangayRequestViewSet, BarangayViewSet

USE_ROUTER = True

app_name = 'relief'
# TODO: Add URLs (Format: path('dir/', view, name="name")
urlpatterns = [
    path('api/users/', view=views.UserListView.as_view(), name='users'),
    path('api/users/<int:pk>/', views.UserDetailView.as_view(), name='user_details'),
    path('api/users/residents/', views.ResidentListView.as_view(), name='residents'),
    path('api/users/admins/', views.GovAdminListView.as_view(), name='admins'),
    path('api/users/donors/', views.DonorListView.as_view(), name='donors'),
    path('api/users/donors/<int:pk>', views.DonorDetailView.as_view(), name='donor_details'),
    path('api/donations/', views.DonationListView.as_view(), name='donations'),
    path('api/donations/<int:pk>', views.DonationDetailView.as_view(), name='donations_details'),
]


# view sets and router

router = SimpleRouter()
# router.register('users', viewset=UserViewSet, basename='users')
router.register('api/users/residents/r', ResidentViewSet, basename='residents_others')
router.register('api/supplies', SupplyViewSet)
router.register('api/item-type', ItemTypeViewSet, basename='itemtype')
router.register('api/item-request', ItemRequestViewSet, basename='item_request')
router.register('api/requests', BarangayRequestViewSet, basename='barangay_request')
router.register('api/transactions', TransactionViewSet, basename='transactions')
router.register('api/users/barangays', BarangayViewSet, basename='barangays')

urlpatterns += router.urls
