import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule

# Remove all existing periodic tasks and schedules
PeriodicTask.objects.all().delete()
IntervalSchedule.objects.all().delete()
CrontabSchedule.objects.all().delete()

# Example: Add a new crontab schedule (every day at 5:00 PM)
crontab, _ = CrontabSchedule.objects.get_or_create(
    minute='0',
    hour='17',
    day_of_week='*',
    day_of_month='*',
    month_of_year='*',
)

PeriodicTask.objects.create(
    crontab=crontab,
    name='Auto Timeout F2F Logs',
    task='internship.tasks.auto_timeout_f2f_logs',
    enabled=True,
)

# Example: Add another schedule (every day at 7:00 PM)
crontab2, _ = CrontabSchedule.objects.get_or_create(
    minute='0',
    hour='19',
    day_of_week='*',
    day_of_month='*',
    month_of_year='*',
)

PeriodicTask.objects.create(
    crontab=crontab2,
    name='Auto Timeout Async Logs',
    task='internship.tasks.auto_timeout_async_logs',
    enabled=True,
)