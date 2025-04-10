from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Intern, Attendance, Task, Image  # Assuming these models exist
from .auth import InternJWTAuthentication
from datetime import timedelta
from django.utils.dateformat import format
from django.utils.timezone import now


@api_view(['POST'])
def intern_login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    try:
        intern = Intern.objects.get(email=email)
        if check_password(password, intern.password):
            # Manually create a token payload
            refresh = RefreshToken.for_user(intern)
            refresh['user_id'] = intern.id
            refresh['email'] = intern.email
            refresh['user_type'] = 'intern'
            return JsonResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
    except Intern.DoesNotExist:
        pass
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
            password=data['password'],
            start_date=data['start_date'],
            time_to_render=timedelta(hours=hours),  # Convert hours to timedelta
        )
        return JsonResponse({'message': 'Intern added successfully', 'id': intern.id})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([InternJWTAuthentication, SessionAuthentication])
def intern_profile(request):
    try:
        # Extract the email from the JWT token
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(request.headers.get('Authorization').split()[1])
        email = validated_token.get('email')

        # Retrieve the intern using the email
        intern = Intern.objects.get(email=email)
        return JsonResponse({
            'email': intern.email,
            'full_name': intern.full_name,
        })
    except Intern.DoesNotExist:
        return JsonResponse({'message': 'Intern not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([InternJWTAuthentication, SessionAuthentication])
def attendance_logs(request):
    try:
        # Extract the email from the JWT token
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(request.headers.get('Authorization').split()[1])
        email = validated_token.get('email')

        # Retrieve the intern using the email
        intern = Intern.objects.get(email=email)

        # Retrieve and order attendance logs (most recent first)
        logs = Attendance.objects.filter(intern=intern).order_by('-time_in').prefetch_related('tasks').values(
            'id', 
            'type',  # Include the type field
            'time_in', 
            'time_out',
            'status',  # Include the status field
        )

        # Format the logs for frontend consumption
        formatted_logs = []
        for log in logs:
            # Retrieve tasks associated with the attendance log
            tasks = Task.objects.filter(attendance=log['id']).values('id', 'description', 'remarks')
            formatted_logs.append({
                'id': log['id'],
                'type': log['type'],  # Add type to the response
                'date': format(log['time_in'], 'Y-m-d'),
                'time_in': format(log['time_in'], 'H:i:s'),
                'time_out': format(log['time_out'], 'H:i:s') if log['time_out'] else None,
                'status': log['status'],  # Add status to the response
                'tasks': list(tasks),  # Include tasks in the response
            })

        return JsonResponse(formatted_logs, safe=False)
    except Intern.DoesNotExist:
        return JsonResponse({'message': 'Intern not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([InternJWTAuthentication, SessionAuthentication])
def log_face_to_face_attendance(request):
    try:
        # Extract the email from the JWT token
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(request.headers.get('Authorization').split()[1])
        email = validated_token.get('email')

        # Retrieve the intern using the email
        intern = Intern.objects.get(email=email)
        face_screenshot = request.data.get('faceScreenshot')

        if not face_screenshot:
            return JsonResponse({'message': 'Face screenshot is required.'}, status=400)

        # Create a new Task
        task = Task.objects.create(
            description="face to face - in",
            remarks="present"
        )

        # Create a new Image tied to the Task
        image = Image.objects.create(
            task=task,
            file=face_screenshot  # Assuming face_screenshot is a valid file or base64-encoded image
        )

        # Create the Attendance record and associate the Task
        attendance = Attendance.objects.create(
            intern=intern,
            type='f2f',
            time_in=now()
        )
        attendance.tasks.add(task)  # Link the task to the attendance

        return JsonResponse({'message': 'Face-to-Face attendance logged successfully.'})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([InternJWTAuthentication, SessionAuthentication])
def log_asynchronous_attendance(request):
    try:
         # Extract the email from the JWT token
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(request.headers.get('Authorization').split()[1])
        email = validated_token.get('email')

        # Retrieve the intern using the email
        intern = Intern.objects.get(email=email)
        tasks_data = request.data.get('tasks', [])

        if not tasks_data or not all(task.get('description', '').strip() for task in tasks_data):
            return JsonResponse({'message': 'All task descriptions must be filled out.'}, status=400)

        # Create the attendance record
        attendance = Attendance.objects.create(
            intern=intern,
            type='async',
            time_in=now()
        )

        # Create and link tasks to the attendance
        for task_data in tasks_data:
            task = Task.objects.create(description=task_data['description'])
            attendance.tasks.add(task)  # Link the task to the attendance

        return JsonResponse({'message': 'Asynchronous attendance logged successfully.'})
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([InternJWTAuthentication, SessionAuthentication])
def attendance_log_details(request, log_id):
    try:
        # Extract the email from the JWT token
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(request.headers.get('Authorization').split()[1])
        email = validated_token.get('email')

        # Retrieve the intern using the email
        intern = Intern.objects.get(email=email)

        # Retrieve the specific attendance log
        attendance = Attendance.objects.get(id=log_id, intern=intern)

        # Retrieve associated tasks
        tasks = attendance.tasks.all()
        tasks_data = []
        for task in tasks:
            images = task.images.all().values('id', 'file')
            tasks_data.append({
                'id': task.id,
                'description': task.description,
                'remarks': task.remarks,
                'images': list(images),
            })

        # Format the response
        response_data = {
            'id': attendance.id,
            'type': attendance.type,
            'date': format(attendance.time_in, 'Y-m-d'),
            'time_in': format(attendance.time_in, 'H:i:s'),
            'time_out': format(attendance.time_out, 'H:i:s') if attendance.time_out else None,
            'tasks': tasks_data,
        }

        return JsonResponse(response_data)
    except Attendance.DoesNotExist:
        return JsonResponse({'message': 'Attendance log not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)
