from django.urls import path, include
from rest_framework import viewsets
from rest_framework.routers import SimpleRouter

from . import views
from .forms import User
from .models import ResidentProfile
from .serializers import UserSerializer, ResidentSerializer

# Settings
from .viewsets import UserViewSet, ResidentViewSet

USE_ROUTER = True

app_name = 'relief'
# TODO: Add URLs (Format: path('dir/', view, name="name")
urlpatterns = [
    path('api/users/', view=views.UserListView.as_view(), name='users'),
    path('api/users/<int:pk>/', views.UserDetailView.as_view(), name='user_details'),
    path('api/users/residents/', views.ResidentListView.as_view(), name='residents'),
    path('api/users/admins/', views.GovAdminListView.as_view(), name='admins'),
]


# view sets and router

router = SimpleRouter()
# router.register('users', viewset=UserViewSet, basename='users')
router.register('api/users/residents/r', ResidentViewSet, basename='residents_others')
urlpatterns += router.urls
