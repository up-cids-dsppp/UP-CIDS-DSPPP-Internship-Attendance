from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from .models import Intern
from datetime import timedelta

@api_view(['POST'])
def intern_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(username=email, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return JsonResponse({'message': 'Invalid email or password'}, status=401)

@api_view(['POST'])
def admin_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    try:
        # Get the user by email
        user = User.objects.get(email=email)
        # Authenticate using the username field
        user = authenticate(username=user.username, password=password)
        if user is not None and user.is_superuser:  # Ensure the user is an admin
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
    except User.DoesNotExist:
        pass
    return JsonResponse({'message': 'Invalid admin credentials'}, status=401)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_profile(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return JsonResponse({'email': request.user.email})
    return JsonResponse({'message': 'Unauthorized'}, status=401)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda u: u.is_superuser)  # Ensure only admins can access
def manage_interns(request):
    if request.method == 'GET':
        interns = Intern.objects.all().values('id', 'full_name', 'email', 'start_date', 'time_to_render')
        return JsonResponse(list(interns), safe=False)
    elif request.method == 'POST':
        data = request.data
        hours = int(data['time_to_render'])  # Convert hours to an integer
        intern = Intern.objects.create(
            full_name=data['full_name'],
            email=data['email'],
            password=make_password(data['password']),  # Hash the password
            start_date=data['start_date'],
            time_to_render=timedelta(hours=hours),  # Convert hours to timedelta
        )
        return JsonResponse({'message': 'Intern added successfully', 'id': intern.id})
