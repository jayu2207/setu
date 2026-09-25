import jwt
import json
from datetime import datetime, timedelta, timezone
from functools import wraps
from django.conf import settings
from django.http import JsonResponse

from .models import User


def make_token(user):
    payload = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'exp': datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


def auth_required(view_func):
    """Equivalent of authRequired in middleware/auth.js"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        header = request.headers.get('Authorization', '')
        token = header.split(' ')[1] if header.startswith('Bearer ') else None
        if not token:
            return JsonResponse({'error': 'No token provided. Please login.'}, status=401)
        try:
            decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        except jwt.PyJWTError:
            return JsonResponse({'error': 'Invalid or expired token. Please login again.'}, status=403)
        request.auth_user = decoded  # {id, name, email, role}
        return view_func(request, *args, **kwargs)
    return wrapper


def require_role(*roles):
    """Equivalent of requireRole(...roles) in middleware/auth.js"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = getattr(request, 'auth_user', None)
            if not user or user.get('role') not in roles:
                return JsonResponse({'error': 'You are not allowed to perform this action.'}, status=403)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def parse_body(request):
    try:
        return json.loads(request.body or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
