from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from relief.models import User, Transaction

admin.site.register(User, UserAdmin)
admin.site.register(Transaction)