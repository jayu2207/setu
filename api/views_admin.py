from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import User, Opportunity, MentorshipRequest, Event, Application
from .auth_utils import auth_required, require_role, parse_body


@csrf_exempt
@require_http_methods(['GET'])
@auth_required
@require_role('admin')
def stats(request):
    return JsonResponse({
        'totalStudents': User.objects.filter(role='student').count(),
        'totalAlumni': User.objects.filter(role='alumni').count(),
        'totalOpportunities': Opportunity.objects.count(),
        'totalMentorships': MentorshipRequest.objects.count(),
        'totalEvents': Event.objects.count(),
        'totalApplications': Application.objects.count(),
    })


@csrf_exempt
@require_http_methods(['GET'])
@auth_required
@require_role('admin')
def list_users(request):
    rows = list(
        User.objects.order_by('-created_at').values('id', 'name', 'email', 'role', 'status', 'created_at')
    )
    for r in rows:
        r['created_at'] = r['created_at'].isoformat()
    return JsonResponse(rows, safe=False)


@csrf_exempt
@require_http_methods(['PUT'])
@auth_required
@require_role('admin')
def update_user_status(request, user_id):
    body = parse_body(request)
    status = body.get('status')
    if status not in ('active', 'blocked'):
        return JsonResponse({'error': 'Invalid status.'}, status=400)

    target = get_object_or_404(User, id=user_id)
    if target.role == 'admin':
        return JsonResponse({'error': 'Cannot modify an admin account.'}, status=400)

    target.status = status
    target.save(update_fields=['status'])
    return JsonResponse({'message': f"User {'blocked' if status == 'blocked' else 'unblocked'} successfully."})


@csrf_exempt
@require_http_methods(['DELETE'])
@auth_required
@require_role('admin')
def delete_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    if target.role == 'admin':
        return JsonResponse({'error': 'Cannot delete an admin account.'}, status=400)
    target.delete()
    return JsonResponse({'message': 'User deleted successfully.'})


@csrf_exempt
@require_http_methods(['GET'])
@auth_required
@require_role('admin')
def all_opportunities(request):
    rows = []
    for o in Opportunity.objects.select_related('alumni').order_by('-created_at'):
        rows.append({
            'id': o.id, 'alumni_id': o.alumni_id, 'title': o.title, 'type': o.type,
            'company': o.company, 'location': o.location, 'description': o.description,
            'apply_link': o.apply_link, 'created_at': o.created_at.isoformat(),
            'posted_by_name': o.alumni.name,
        })
    return JsonResponse(rows, safe=False)


@csrf_exempt
@require_http_methods(['GET'])
@auth_required
@require_role('admin')
def all_mentorship(request):
    rows = []
    for m in MentorshipRequest.objects.select_related('student', 'alumni').order_by('-created_at'):
        rows.append({
            'id': m.id, 'student_id': m.student_id, 'alumni_id': m.alumni_id, 'field': m.field,
            'message': m.message, 'status': m.status, 'created_at': m.created_at.isoformat(),
            'student_name': m.student.name, 'alumni_name': m.alumni.name,
        })
    return JsonResponse(rows, safe=False)


@csrf_exempt
@require_http_methods(['GET'])
@auth_required
@require_role('admin')
def all_events(request):
    rows = []
    for e in Event.objects.select_related('created_by').order_by('-event_date'):
        rows.append({
            'id': e.id, 'created_by': e.created_by_id, 'title': e.title,
            'description': e.description, 'event_date': e.event_date, 'location': e.location,
            'created_at': e.created_at.isoformat(), 'created_by_name': e.created_by.name,
        })
    return JsonResponse(rows, safe=False)
