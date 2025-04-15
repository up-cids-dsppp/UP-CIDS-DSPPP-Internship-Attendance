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
from django.utils.timezone import localtime


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
        interns = Intern.objects.all().values(
            'id', 
            'full_name', 
            'email', 
            'start_date', 
            'time_to_render', 
            'status'  # Include the status field
        )
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

@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda u: u.is_superuser)  # Ensure only admins can access
def intern_details(request, intern_id):
    try:
        intern = Intern.objects.get(id=intern_id)

        if request.method == 'GET':
            # Retrieve attendance logs linked to the intern
            attendance_logs = Attendance.objects.filter(intern=intern).values(
                'id',
                'type',
                'time_in',
                'time_out',
                'status',
                'work_duration',  # Include work_duration
            )

            # Format attendance logs for the response
            formatted_logs = []
            for log in attendance_logs:
                formatted_logs.append({
                    'id': log['id'],
                    'type': log['type'],
                    'date': format(localtime(log['time_in']), 'Y-m-d'),
                    'time_in': format(localtime(log['time_in']), 'H:i:s'),
                    'time_out': format(localtime(log['time_out']), 'H:i:s') if log['time_out'] else None,
                    'status': log['status'],
                    'work_duration': log['work_duration'].total_seconds() / 3600 if log['work_duration'] else 0,  # Convert to hours
                })

            # Return all details except the password
            intern_data = {
                'id': intern.id,
                'full_name': intern.full_name,
                'email': intern.email,
                'start_date': intern.start_date,
                'time_to_render': intern.time_to_render.total_seconds() / 3600,  # Convert timedelta to hours
                'time_rendered': intern.time_rendered.total_seconds() / 3600 if intern.time_rendered else 0,  # Convert timedelta to hours
                'status': intern.status,
                'attendance_logs': formatted_logs,
            }
            return JsonResponse(intern_data, safe=False)

        elif request.method == 'PUT':
            data = request.data
            intern.full_name = data.get('full_name', intern.full_name)
            intern.email = data.get('email', intern.email)
            if 'password' in data and data['password']:  # Only update if password is provided
                intern.password = make_password(data['password'])  # Hash the new password
            intern.start_date = data.get('start_date', intern.start_date)
            intern.time_to_render = timedelta(hours=int(data['time_to_render']))
            intern.save()
            return JsonResponse({'message': 'Intern details updated successfully.'})

        elif request.method == 'DELETE':
            # Allow deletion only if the intern's status is "dropped" or "completed"
            if intern.status not in ['dropped', 'completed']:
                return JsonResponse({'message': 'Intern can only be deleted if their status is "dropped" or "completed".'}, status=400)

            # Delete the intern
            intern.delete()
            return JsonResponse({'message': 'Intern deleted successfully.'}, status=200)

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

        # Restrict access for completed or dropped interns
        if intern.status in ['completed', 'dropped']:
            return JsonResponse({'message': 'You are not allowed to log attendance with your current status.'}, status=403)

        # Check if the current time is within allowed hours (8 AM to 5 PM)
        now = localtime()
        if not (8 <= now.hour < 17):
            return JsonResponse({'message': 'Time-in is only allowed between 8 AM and 5 PM.'}, status=403)

        # Check if the intern already has a "sent" attendance for the day
        today = now.date()
        if Attendance.objects.filter(intern=intern, time_in__date=today, status='sent').exists():
            return JsonResponse({'message': 'You have already logged attendance for today.'}, status=403)

        # Proceed with logging attendance
        face_screenshot = request.data.get('faceScreenshot')
        if not face_screenshot:
            return JsonResponse({'message': 'Face screenshot is required.'}, status=400)

        # Create a new Task
        task = Task.objects.create(
            description="face to face - in",
            intern_remarks="present"
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
            time_in=now
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

        # Restrict access for completed or dropped interns
        if intern.status in ['completed', 'dropped']:
            return JsonResponse({'message': 'You are not allowed to log attendance with your current status.'}, status=403)

        # Check if the current time is within allowed hours (8 AM to 5 PM)
        now = localtime()
        if not (8 <= now.hour < 17):
            return JsonResponse({'message': 'Time-in is only allowed between 8 AM and 5 PM.'}, status=403)

        # Check if the intern already has a "sent" attendance for the day
        today = now.date()
        if Attendance.objects.filter(intern=intern, time_in__date=today, status='sent').exists():
            return JsonResponse({'message': 'You have already logged attendance for today.'}, status=403)

        # Validate tasks data
        tasks_data = request.data.get('tasks', [])
        if not tasks_data or not all(task.get('description', '').strip() for task in tasks_data):
            return JsonResponse({'message': 'All task descriptions must be filled out.'}, status=400)

        # Create the attendance record
        attendance = Attendance.objects.create(
            intern=intern,
            type='async',
            time_in=now
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

        # Retrieve the specific attendance log and ensure it belongs to the logged-in intern
        attendance = Attendance.objects.get(id=log_id, intern=intern)

# Retrieve associated tasks
        tasks = attendance.tasks.all()
        tasks_data = []
        for task in tasks:
            images = task.images.all().values('id', 'file')
            tasks_data.append({
                'id': task.id,
                'description': task.description,
                'intern_remarks': task.intern_remarks,
                'images': list(images),
            })

        # Format the response
        response_data = {
            'id': attendance.id,
            'type': attendance.type,
            'status': attendance.status,
            'date': format(localtime(attendance.time_in), 'Y-m-d'),
            'time_in': format(localtime(attendance.time_in), 'H:i:s'),
            'time_out': format(localtime(attendance.time_out), 'H:i:s') if attendance.time_out else None,
            'tasks': tasks_data,
            'admin_remarks': attendance.admin_remarks,
            'work_duration': attendance.work_duration.total_seconds() / 3600 if attendance.work_duration else 0,  # Convert to hours
        }

        return JsonResponse(response_data)
    except Attendance.DoesNotExist:
        return JsonResponse({'message': 'Attendance log not found or unauthorized access'}, status=403)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([InternJWTAuthentication, SessionAuthentication])
def submit_timeout(request, log_id):
    try:
        # Extract the email from the JWT token
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(request.headers.get('Authorization').split()[1])
        email = validated_token.get('email')

        # Retrieve the intern using the email
        intern = Intern.objects.get(email=email)

        # Restrict access for completed or dropped interns
        if intern.status in ['completed', 'dropped']:
            return JsonResponse({'message': 'You are not allowed to submit a timeout with your current status.'}, status=403)

        # Retrieve the attendance log
        attendance = Attendance.objects.get(id=log_id, intern=intern)

        # Check if the attendance log is in the "ongoing" state
        if attendance.status != 'ongoing':
            return JsonResponse({'message': 'You can only submit a timeout for an ongoing attendance log.'}, status=403)

        # Check if the current time is within allowed hours (8 AM to 5 PM)
        now = localtime()
        if not (8 <= now.hour < 17):
            return JsonResponse({'message': 'Timeout is only allowed between 8 AM and 5 PM.'}, status=403)

        # Update tasks with remarks and images
        tasks_data = request.POST  # Form data for remarks
        files = request.FILES  # Uploaded files

        for task_id, intern_remarks in tasks_data.items():
            if task_id.startswith('tasks[') and task_id.endswith('][intern_remarks]'):
                # Extract the task ID
                task_id = int(task_id.split('[')[1].split(']')[0])

                # Update the task
                task = Task.objects.get(id=task_id, attendance=attendance)
                task.intern_remarks = intern_remarks
                task.save()

                # Save uploaded images for the task
                image_field_prefix = f'tasks[{task_id}][images]'
                for key, file in files.items():
                    if key.startswith(image_field_prefix):
                        # Save the file to the database
                        Image.objects.create(task=task, file=file)

        # Update the attendance status and time_out
        attendance.status = 'sent'
        attendance.time_out = now
        attendance.save()

        return JsonResponse({'message': 'Timeout submitted successfully.'}, status=200)
    except Attendance.DoesNotExist:
        return JsonResponse({'message': 'Attendance log not found'}, status=404)
    except Task.DoesNotExist:
        return JsonResponse({'message': 'Task not found'}, status=404)
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error for debugging
        return JsonResponse({'message': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda u: u.is_superuser)  # Ensure only admins can access
def get_intern_attendance(request, log_id):
    try:
        # Retrieve the specific attendance log
        attendance = Attendance.objects.get(id=log_id)

# Retrieve associated tasks
        tasks = attendance.tasks.all()
        tasks_data = []
        for task in tasks:
            images = task.images.all().values('id', 'file')
            tasks_data.append({
                'id': task.id,
                'description': task.description,
                'intern_remarks': task.intern_remarks,
                'images': list(images),
                'remarks': task.intern_remarks,  # Include admin remarks
            })

        # Format the response
        response_data = {
            'id': attendance.id,
            'type': attendance.type,
            'status': attendance.status,
            'admin_remarks': attendance.admin_remarks,
            'date': format(localtime(attendance.time_in), 'Y-m-d'),
            'time_in': format(localtime(attendance.time_in), 'H:i:s'),
            'time_out': format(localtime(attendance.time_out), 'H:i:s') if attendance.time_out else None,
            'work_duration': attendance.work_duration.total_seconds() / 3600 if attendance.work_duration else 0,  # Convert to hours
            'tasks': tasks_data,
        }

        return JsonResponse(response_data)
    except Attendance.DoesNotExist:
        return JsonResponse({'message': 'Attendance log not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda u: u.is_superuser)  # Ensure only admins can access
def attendance_feedback(request, log_id):
    try:
        # Retrieve the attendance log by ID
        attendance = Attendance.objects.get(id=log_id)

        # Extract feedback data from the request
        feedback_type = request.data.get('type')
        feedback_remarks = request.data.get('admin_remarks')

        # Validate the feedback data
        if not feedback_type or not feedback_remarks:
            return JsonResponse({'message': 'Both type and remarks are required.'}, status=400)

        # Map feedback type to status
        status_mapping = {
            'Validate': 'validated',
            'Flag': 'flagged',
        }

        # Update the attendance log
        attendance.status = status_mapping.get(feedback_type, attendance.status)  # Default to current status if type is invalid
        attendance.admin_remarks = feedback_remarks  # Update the remarks field

        # If feedback type is "Validate", calculate duration and update intern's time_rendered
        if feedback_type == 'Validate' and attendance.time_out:
            duration = attendance.time_out - attendance.time_in
            attendance.work_duration = duration  # Update work_duration field

        attendance.save()

        return JsonResponse({'message': 'Feedback submitted successfully.'}, status=200)
    except Attendance.DoesNotExist:
        return JsonResponse({'message': 'Attendance log not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda u: u.is_superuser)  # Ensure only admins can access
def evaluate_attendance(request, log_id):
    try:
        # Retrieve the attendance log by ID
        attendance = Attendance.objects.get(id=log_id)

        # Extract evaluation data from the request
        duration = request.data.get('duration')
        admin_remarks = request.data.get('admin_remarks')

        # Validate inputs
        if duration is None or admin_remarks is None:
            return JsonResponse({'message': 'Duration and remarks are required.'}, status=400)

        # Ensure duration is within valid range
        max_duration = (attendance.time_out - attendance.time_in).total_seconds() / 3600  # Convert to hours
        if not (0 <= float(duration) <= max_duration):
            return JsonResponse({'message': 'Invalid duration value.'}, status=400)

        # Update intern's time_rendered
        attendance.work_duration = timedelta(hours=float(duration))  # Convert hours to timedelta

        # Update attendance log
        attendance.admin_remarks = admin_remarks
        attendance.status = 'validated'
        attendance.save()

        return JsonResponse({'message': 'Attendance evaluated successfully.'}, status=200)
    except Attendance.DoesNotExist:
        return JsonResponse({'message': 'Attendance log not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda u: u.is_superuser)  # Ensure only admins can access
def evaluate_intern(request, intern_id):
    try:
        # Retrieve the intern by ID
        intern = Intern.objects.get(id=intern_id)

        # Extract evaluation data from the request
        evaluation_type = request.data.get('evaluation_type')
        admin_remarks = request.data.get('admin_remarks')

        print(f"Evaluation Type: {evaluation_type}, Admin Remarks: {admin_remarks}")

        # Validate inputs
        if not evaluation_type or not admin_remarks:
            return JsonResponse({'message': 'Both type and remarks are required.'}, status=400)

        # Update intern's status and admin remarks
        intern.status = evaluation_type
        intern.admin_remarks = admin_remarks
        intern.save()

        return JsonResponse({'message': 'Intern evaluated successfully.'}, status=200)
    except Intern.DoesNotExist:
        return JsonResponse({'message': 'Intern not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@user_passes_test(lambda u: u.is_superuser)  # Ensure only admins can access
def undrop_intern(request, intern_id):
    try:
        intern = Intern.objects.get(id=intern_id)
        previous_status = request.data.get('previous_status')

        if not previous_status:
            return JsonResponse({'message': 'Previous status is required.'}, status=400)

        intern.status = previous_status
        intern.save()

        return JsonResponse({'message': 'Intern status updated successfully.'}, status=200)
    except Intern.DoesNotExist:
        return JsonResponse({'message': 'Intern not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([InternJWTAuthentication, SessionAuthentication])
def intern_profile_with_logs(request):
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
            'type',  
            'time_in', 
            'time_out',
            'status',  
            'work_duration',  # Include work_duration
        )

        # Format the logs for frontend consumption
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                'id': log['id'],
                'type': log['type'],
                'date': format(localtime(log['time_in']), 'Y-m-d'),
                'time_in': format(localtime(log['time_in']), 'H:i:s'),
                'time_out': format(localtime(log['time_out']), 'H:i:s') if log['time_out'] else None,
                'status': log['status'],
                'work_duration': log['work_duration'].total_seconds() / 3600 if log['work_duration'] else 0,  # Convert to hours
            })

        # Combine intern details and attendance logs
        response_data = {
            'email': intern.email,
            'full_name': intern.full_name,
            'start_date': intern.start_date,
            'time_to_render': intern.time_to_render.total_seconds() / 3600,  # Convert timedelta to hours
            'time_rendered': intern.time_rendered.total_seconds() / 3600 if intern.time_rendered else 0,  # Convert timedelta to hours
            'status': intern.status,
            'admin_remarks': intern.admin_remarks,
            'attendance_logs': formatted_logs,
        }

        return JsonResponse(response_data, safe=False)
    except Intern.DoesNotExist:
        return JsonResponse({'message': 'Intern not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure only authenticated users can access
def hash_password(request):
    """
    Hash a plain password using the backend's hashing algorithm.
    """
    plain_password = request.data.get('password')
    if not plain_password:
        return JsonResponse({'error': 'Password is required'}, status=400)
    hashed_password = make_password(plain_password)
    return JsonResponse({'hashed_password': hashed_password})

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure only authenticated users can access
def check_password_uniqueness(request):
    """
    Check if a hashed password already exists in the database.
    """
    hashed_password = request.data.get('hashed_password')
    if not hashed_password:
        return JsonResponse({'error': 'Hashed password is required'}, status=400)

    # Compare hashed password with existing intern passwords
    for intern in Intern.objects.all():
        if check_password(intern.password, hashed_password):
            return JsonResponse({'is_unique': False})

    return JsonResponse({'is_unique': True})
