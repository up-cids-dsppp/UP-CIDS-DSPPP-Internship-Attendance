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
]