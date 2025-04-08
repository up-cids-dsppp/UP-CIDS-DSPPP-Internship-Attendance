from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test

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
def admin_profile(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return JsonResponse({'email': request.user.email})
    return JsonResponse({'message': 'Unauthorized'}, status=401)

@api_view(['GET'])
@user_passes_test(lambda u: u.is_superuser)  # Ensure only admins can access
def get_interns(request):
    interns = User.objects.filter(is_superuser=False).values('id', 'first_name', 'last_name', 'email')
    interns_list = [{'id': intern['id'], 'full_name': f"{intern['first_name']} {intern['last_name']}", 'email': intern['email']} for intern in interns]
    return JsonResponse(interns_list, safe=False)
