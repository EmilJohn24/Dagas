from django.conf.global_settings import LOGIN_URL
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from .models import Role


def role_required(role_id, function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=LOGIN_URL):
    test_decorator = user_passes_test(
        lambda user: user.is_active and user.role.id == role_id,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:  # Not None
        return test_decorator(function)
    else:
        return test_decorator
