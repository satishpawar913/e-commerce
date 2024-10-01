from django.contrib import admin

from .models import *


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    ist_display = ('user', 'role')
    list_filter = ('role',)
