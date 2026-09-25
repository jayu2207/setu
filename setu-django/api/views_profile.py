from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db.models import F

from .models import User, StudentProfile, AlumniProfile
from .auth_utils import auth_required, parse_body


@csrf_exempt
@require_http_methods(['GET', 'PUT'])
@auth_required
def me(request):
    au = request.auth_user
    user = User.objects.filter(id=au['id']).values('id', 'name', 'email', 'role', 'created_at').first()

    if request.method == 'GET':
        profile = None
        if au['role'] == 'student':
            profile = StudentProfile.objects.filter(user_id=au['id']).values(
                'branch', 'year', 'skills', 'bio', 'avatar'
            ).first()
        elif au['role'] == 'alumni':
            profile = AlumniProfile.objects.filter(user_id=au['id']).values(
                'company', 'position', 'graduation_year', 'branch', 'experience', 'skills', 'bio', 'avatar'
            ).first()
        return JsonResponse({'user': user, 'profile': profile})

    # PUT
    body = parse_body(request)
    if au['role'] == 'student':
        StudentProfile.objects.filter(user_id=au['id']).update(
            branch=body.get('branch') or '',
            year=body.get('year') or '',
            skills=body.get('skills') or '',
            bio=body.get('bio') or '',
        )
    elif au['role'] == 'alumni':
        AlumniProfile.objects.filter(user_id=au['id']).update(
            company=body.get('company') or '',
            position=body.get('position') or '',
            graduation_year=body.get('graduation_year') or '',
            branch=body.get('branch') or '',
            experience=body.get('experience') or '',
            skills=body.get('skills') or '',
            bio=body.get('bio') or '',
        )
    else:
        return JsonResponse({'error': 'Admins do not have an editable profile.'}, status=400)

    return JsonResponse({'message': 'Profile updated successfully!'})


@csrf_exempt
@require_http_methods(['GET'])
@auth_required
def list_alumni(request):
    rows = list(
        AlumniProfile.objects.filter(user__role='alumni', user__status='active')
        .select_related('user')
        .order_by('user__name')
        .values(
            'company', 'position', 'graduation_year', 'branch', 'experience', 'skills', 'bio',
            id=F('user_id'), name=F('user__name'), email=F('user__email'),
        )
    )
    return JsonResponse(rows, safe=False)
