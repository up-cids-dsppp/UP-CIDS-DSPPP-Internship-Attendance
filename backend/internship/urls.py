from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('intern/login', views.intern_login, name='intern_login'),
    path('admin/login', views.admin_login, name='admin_login'),  # Admin login endpoint
    path('admin/profile', views.admin_profile, name='admin_profile'),
    path('admin/interns', views.get_interns, name='get_interns'),  # Add this line
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]