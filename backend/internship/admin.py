from django.contrib import admin
from .models import Intern, Attendance, Task, Image

@admin.register(Intern)
class InternAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'start_date', 'time_to_render', 'time_rendered')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('intern', 'type', 'time_in', 'time_out', 'status')
    list_filter = ('type', 'status')
    search_fields = ('intern__full_name', 'intern__email')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('description', 'attendance', 'created_at')
    search_fields = ('description',)
    list_filter = ('created_at',)

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('task', 'file', 'uploaded_at')
    search_fields = ('task__description',)
    list_filter = ('uploaded_at',)
