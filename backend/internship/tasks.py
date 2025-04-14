from backend.backend.celery import shared_task
from django.utils.timezone import localtime
from internship.models import Attendance

@shared_task
def auto_timeout_attendance_logs():
    current_time = localtime()
    today = current_time.date()

    # Query all ongoing attendance logs for today
    ongoing_logs = Attendance.objects.filter(
        time_in__date=today,
        status='ongoing'
    )

    # Update each log
    for log in ongoing_logs:
        log.time_out = current_time  # Set the time_out to the current time
        log.admin_remarks = "Did not time out."
        log.status = 'flagged'
        log.work_duration = log.time_out - log.time_in  # Calculate work duration
        log.save()

    return f"Timed out {ongoing_logs.count()} ongoing attendance logs."