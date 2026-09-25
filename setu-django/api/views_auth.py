from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse

from .models import User, StudentProfile, AlumniProfile
from .auth_utils import make_token, parse_body


@csrf_exempt
@require_http_methods(['POST'])
def register(request):
    body = parse_body(request)
    name = (body.get('name') or '').strip()
    email = (body.get('email') or '').strip().lower()
    password = body.get('password') or ''
    role = body.get('role') or ''

    if not name or not email or not password or not role:
        return JsonResponse({'error': 'All fields are required.'}, status=400)
    if role not in ('student', 'alumni'):
        return JsonResponse({'error': 'Role must be student or alumni.'}, status=400)
    if len(password) < 6:
        return JsonResponse({'error': 'Password must be at least 6 characters.'}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({'error': 'An account with this email already exists.'}, status=409)

    user = User.objects.create(name=name, email=email, password=make_password(password), role=role)

    if role == 'student':
        StudentProfile.objects.create(user=user)
    else:
        AlumniProfile.objects.create(user=user)

    token = make_token(user)
    return JsonResponse({
        'message': 'Registration successful!',
        'token': token,
        'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role},
    }, status=201)


@csrf_exempt
@require_http_methods(['POST'])
def login(request):
    body = parse_body(request)
    email = (body.get('email') or '').strip().lower()
    password = body.get('password') or ''

    if not email or not password:
        return JsonResponse({'error': 'Email and password are required.'}, status=400)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Invalid email or password.'}, status=401)

    if user.status == 'blocked':
        return JsonResponse({'error': 'Your account has been blocked by admin.'}, status=403)

    if not check_password(password, user.password):
        return JsonResponse({'error': 'Invalid email or password.'}, status=401)

    token = make_token(user)
    return JsonResponse({
        'message': 'Login successful!',
        'token': token,
        'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role},
    })
