from django.contrib import admin
from .models import Intern

@admin.register(Intern)
class InternAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'start_date', 'time_to_render', 'time_rendered')
