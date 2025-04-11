from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('intern/login', views.intern_login, name='intern_login'),
    path('intern/profile', views.intern_profile, name='intern_profile'),
    path('intern/attendance', views.attendance_logs, name='attendance_logs'),
    path('admin/login', views.admin_login, name='admin_login'),
    path('admin/profile', views.admin_profile, name='admin_profile'),
    path('admin/interns', views.manage_interns, name='manage_interns'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('intern/attendance/f2f', views.log_face_to_face_attendance, name='log_face_to_face_attendance'),
    path('intern/attendance/async', views.log_asynchronous_attendance, name='log_asynchronous_attendance'),
    path('intern/attendance/log/<int:log_id>/', views.attendance_log_details, name='attendance_log_details'),
    path('intern/attendance/log/<int:log_id>/submit', views.submit_timeout, name='submit_timeout'),
]