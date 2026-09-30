import os
import uuid

from django.core.files.base import ContentFile
from django.http import JsonResponse, FileResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .auth_utils import auth_required, require_role
from .matching import extract_resume_text
from .models import StudentProfile, Application

MAX_RESUME_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED = {'.pdf': b'%PDF', '.docx': b'PK'}  # extension -> magic bytes


@csrf_exempt
@require_http_methods(['POST', 'DELETE'])
@auth_required
@require_role('student')
def my_resume(request):
    au = request.auth_user
    profile, _ = StudentProfile.objects.get_or_create(user_id=au['id'])

    if request.method == 'DELETE':
        if profile.resume:
            profile.resume.delete(save=False)
        profile.resume, profile.resume_name, profile.resume_text, profile.resume_uploaded_at = '', '', '', None
        profile.save()
        return JsonResponse({'message': 'Resume removed.'})

    f = request.FILES.get('resume')
    if not f:
        return JsonResponse({'error': 'Please choose a resume file.'}, status=400)
    ext = os.path.splitext(f.name)[1].lower()
    if ext not in ALLOWED:
        return JsonResponse({'error': 'Only PDF or DOCX resumes are allowed.'}, status=400)
    if f.size > MAX_RESUME_BYTES:
        return JsonResponse({'error': 'Resume must be 5 MB or smaller.'}, status=400)
    data = f.read()
    if not data.startswith(ALLOWED[ext]):
        return JsonResponse({'error': 'This file does not look like a valid %s.' % ext[1:].upper()}, status=400)

    if profile.resume:
        profile.resume.delete(save=False)
    # random server-side name: never trust the user's filename on disk
    profile.resume.save('%s_%s%s' % (au['id'], uuid.uuid4().hex[:12], ext), ContentFile(data), save=False)
    profile.resume_name = os.path.basename(f.name)[:255]
    profile.resume_text = extract_resume_text(data, ext)
    profile.resume_uploaded_at = timezone.now()
    profile.save()
    return JsonResponse({'message': 'Resume uploaded!', 'resume_name': profile.resume_name}, status=201)


@csrf_exempt
@require_http_methods(['GET'])
@auth_required
def resume_download(request, student_id):
    """Student: own resume. Alumni: only students who applied to THEIR posting. Admin: any."""
    au = request.auth_user
    allowed = (
        au['role'] == 'admin'
        or (au['role'] == 'student' and au['id'] == student_id)
        or (au['role'] == 'alumni' and Application.objects.filter(
            student_id=student_id, opportunity__alumni_id=au['id']).exists())
    )
    if not allowed:
        return JsonResponse({'error': 'You are not allowed to view this resume.'}, status=403)

    profile = StudentProfile.objects.filter(user_id=student_id).first()
    if not profile or not profile.resume:
        return JsonResponse({'error': 'No resume uploaded.'}, status=404)

    ext = os.path.splitext(profile.resume.name)[1].lower()
    ctype = 'application/pdf' if ext == '.pdf' else \
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    resp = FileResponse(profile.resume.open('rb'), content_type=ctype)
    resp['Content-Disposition'] = 'inline; filename="%s"' % (profile.resume_name or ('resume' + ext)).replace('"', '')
    resp['X-Content-Type-Options'] = 'nosniff'
    return resp
