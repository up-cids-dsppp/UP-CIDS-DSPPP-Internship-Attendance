from celery import shared_task
from django.utils.timezone import localtime
from internship.models import Attendance
import logging

@shared_task
def auto_timeout_f2f_logs():
    logger = logging.getLogger(__name__)
    logger.info("Running auto_timeout_attendance_logs task")

    current_time = localtime()
    today = current_time.date()

    ongoing_f2f_logs = Attendance.objects.filter(
        time_in__date=today,
        status='ongoing',
        type='f2f',
        )

    for log in ongoing_f2f_logs:
        log.time_out = current_time
        log.admin_remarks = "Did not time out."
        log.status = 'flagged'
        log.save()

    logger.info(f"Timed out {ongoing_f2f_logs.count()} ongoing attendance logs.")
    return f"Timed out {ongoing_f2f_logs.count()} ongoing attendance logs."

@shared_task
def auto_timeout_async_logs():
    logger = logging.getLogger(__name__)
    logger.info("Running auto_timeout_attendance_logs task")

    current_time = localtime()
    today = current_time.date()

    ongoing_async_logs = Attendance.objects.filter(
        time_in__date=today,
        status='ongoing',
        type='async',
        )

    for log in ongoing_async_logs:
        log.time_out = current_time
        log.admin_remarks = "Did not time out."
        log.status = 'flagged'
        log.save()

    logger.info(f"Timed out {ongoing_async_logs.count()} ongoing attendance logs.")
    return f"Timed out {ongoing_async_logs.count()} ongoing attendance logs."