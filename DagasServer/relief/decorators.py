from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test

from DagasServer.settings import LOGIN_URL
from .models import User


def role_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=LOGIN_URL, role_id=User.RESIDENT):
    test_decorator = user_passes_test(
        lambda user: user.is_active and user.role == role_id,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:  # Not None
        return test_decorator(function)
    else:
        return test_decorator
