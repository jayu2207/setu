from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import User, MentorshipRequest
from .auth_utils import auth_required, require_role, parse_body


@csrf_exempt
@require_http_methods(['POST'])
@auth_required
@require_role('student')
def send_request(request):
    au = request.auth_user
    body = parse_body(request)
    alumni_id, field = body.get('alumni_id'), body.get('field')
    if not alumni_id or not field:
        return JsonResponse({'error': 'Alumni and field are required.'}, status=400)

    if not User.objects.filter(id=alumni_id, role='alumni').exists():
        return JsonResponse({'error': 'Alumni not found.'}, status=404)

    MentorshipRequest.objects.create(
        student_id=au['id'], alumni_id=alumni_id, field=field, message=body.get('message') or '',
    )
    return JsonResponse({'message': 'Mentorship request sent!'}, status=201)


@csrf_exempt
@require_http_methods(['GET'])
@auth_required
@require_role('student')
def sent_requests(request):
    au = request.auth_user
    rows = []
    for m in MentorshipRequest.objects.filter(student_id=au['id']).select_related('alumni').order_by('-created_at'):
        rows.append({
            'id': m.id, 'student_id': m.student_id, 'alumni_id': m.alumni_id, 'field': m.field,
            'message': m.message, 'status': m.status, 'created_at': m.created_at.isoformat(),
            'alumni_name': m.alumni.name, 'alumni_email': m.alumni.email,
        })
    return JsonResponse(rows, safe=False)


@csrf_exempt
@require_http_methods(['GET'])
@auth_required
@require_role('alumni')
def received_requests(request):
    au = request.auth_user
    rows = []
    for m in MentorshipRequest.objects.filter(alumni_id=au['id']).select_related('student').order_by('-created_at'):
        rows.append({
            'id': m.id, 'student_id': m.student_id, 'alumni_id': m.alumni_id, 'field': m.field,
            'message': m.message, 'status': m.status, 'created_at': m.created_at.isoformat(),
            'student_name': m.student.name, 'student_email': m.student.email,
        })
    return JsonResponse(rows, safe=False)


@csrf_exempt
@require_http_methods(['PUT'])
@auth_required
@require_role('alumni')
def update_request_status(request, req_id):
    au = request.auth_user
    body = parse_body(request)
    status = body.get('status')
    if status not in ('accepted', 'rejected', 'completed'):
        return JsonResponse({'error': 'Invalid status.'}, status=400)

    m = get_object_or_404(MentorshipRequest, id=req_id)
    if m.alumni_id != au['id']:
        return JsonResponse({'error': 'Not your request.'}, status=403)

    m.status = status
    m.save(update_fields=['status'])
    return JsonResponse({'message': 'Request updated.'})
