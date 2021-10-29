from django.urls import path, include

from . import views
app_name = 'relief'
# TODO: Add URLs (Format: path('dir/', view, name="name")
urlpatterns = [
    path('api/users/', view=views.UserListView.as_view(), name='users'),
]
