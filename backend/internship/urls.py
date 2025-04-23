from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('intern/login', views.intern_login, name='intern_login'),
    path('intern/profile', views.intern_profile_with_logs, name='intern_profile'),
    path('intern/attendance/f2f', views.submit_f2f_in, name='log_face_to_face_attendance'),
    path('intern/attendance/async', views.submit_async_in, name='log_asynchronous_attendance'),
    path('intern/attendance/<int:log_id>/', views.attendance_log_details, name='attendance_log_details'),
    path('intern/attendance/<int:log_id>/submit/async', views.submit_async_out, name='submit_async_timeout'),
    path('intern/attendance/<int:log_id>/submit/f2f', views.submit_f2f_out, name='submit_f2f_timeout'),


    path('admin/login', views.admin_login, name='admin_login'),
    path('admin/profile', views.admin_profile, name='admin_profile'),
    path('admin/interns', views.manage_interns, name='manage_interns'),
    path('admin/interns/<int:intern_id>/', views.intern_details, name='intern_details'),  # Combined endpoint
    path('admin/interns/attendance/<int:log_id>/', views.get_intern_attendance, name='get_intern_attendance_details'),
    path('admin/interns/attendance/<int:log_id>/feedback', views.attendance_feedback, name='attendance_feedback'),
    path('admin/interns/attendance/<int:log_id>/evaluate', views.evaluate_attendance, name='evaluate_attendance'),
    path('admin/interns/<int:intern_id>/evaluate', views.evaluate_intern, name='evaluate_intern'),
    path('admin/interns/<int:intern_id>/undrop', views.undrop_intern, name='undrop_intern'),
    path('admin/hash-password', views.hash_password, name='hash_password'),
    path('admin/check-password-uniqueness', views.check_password_uniqueness, name='check_password_uniqueness'),
    path('admin/export/interns', views.export_interns_to_csv, name='export_interns_to_csv'),
    path('admin/export/attendance', views.export_attendance_to_csv, name='export_attendance_to_csv'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]