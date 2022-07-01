from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm

# Based on:
#       https://blog.crunchydata.com/blog/building-a-user-registration-form-with-djangos-built-in-authentication
#       https://stackoverflow.com/questions/55614022/merging-add-form-in-django-admin-from-2-or-more-models-connected-with-one-to
User = get_user_model()


class RegisterForm(UserCreationForm):
    """
        Form for registering users
    """
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'role','profile_picture']


