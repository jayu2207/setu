from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from decimal import Decimal, InvalidOperation

from .models import Opportunity, Application, StudentProfile
from .matching import match_student
from .auth_utils import auth_required, require_role, parse_body


def _opp_dict(o, posted_by_name):
    return {
        'id': o.id, 'alumni_id': o.alumni_id, 'title': o.title, 'type': o.type,
        'company': o.company, 'location': o.location, 'description': o.description,
        'apply_link': o.apply_link, 'created_at': o.created_at.isoformat(),
        'posted_by_name': posted_by_name,
        'required_skills': o.required_skills, 'required_branch': o.required_branch,
        'min_cgpa': str(o.min_cgpa) if o.min_cgpa is not None else '',
    }


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@auth_required
def opportunities_list(request):
    au = request.auth_user

    if request.method == 'GET':
        rows = []
        qs = Opportunity.objects.select_related('alumni').order_by('-created_at')
        applied_ids = set()
        if au['role'] == 'student':
            applied_ids = set(
                Application.objects.filter(student_id=au['id']).values_list('opportunity_id', flat=True)
            )
        for o in qs:
            d = _opp_dict(o, o.alumni.name)
            if au['role'] == 'student':
                d['already_applied'] = o.id in applied_ids
            rows.append(d)
        return JsonResponse(rows, safe=False)

    # POST — alumni only
    if au['role'] != 'alumni':
        return JsonResponse({'error': 'You are not allowed to perform this action.'}, status=403)

    body = parse_body(request)
    title, otype, company = body.get('title'), body.get('type'), body.get('company')
    if not title or not otype or not company:
        return JsonResponse({'error': 'Title, type and company are required.'}, status=400)
    if otype not in ('job', 'internship'):
        return JsonResponse({'error': 'Type must be job or internship.'}, status=400)

    min_cgpa = None
    if body.get('min_cgpa') not in (None, ''):
        try:
            min_cgpa = Decimal(str(body['min_cgpa']))
        except InvalidOperation:
            return JsonResponse({'error': 'Minimum CGPA must be a number.'}, status=400)
        if not (0 <= min_cgpa <= 10):
            return JsonResponse({'error': 'Minimum CGPA must be between 0 and 10.'}, status=400)

    o = Opportunity.objects.create(
        alumni_id=au['id'], title=title, type=otype, company=company,
        required_skills=body.get('required_skills') or '',
        required_branch=body.get('required_branch') or '', min_cgpa=min_cgpa,
        location=body.get('location') or '', description=body.get('description') or '',
        apply_link=body.get('apply_link') or '',
    )
    return JsonResponse({'message': 'Opportunity posted successfully!', 'id': o.id}, status=201)


@csrf_exempt
@require_http_methods(['GET'])
@auth_required
@require_role('alumni')
def opportunities_mine(request):
    au = request.auth_user
    rows = []
    for o in Opportunity.objects.filter(alumni_id=au['id']).order_by('-created_at'):
        d = _opp_dict(o, None)
        applicants = []
        for a in Application.objects.filter(opportunity_id=o.id).select_related('student'):
            applicants.append({
                'application_id': a.id, 'status': a.status, 'applied_at': a.applied_at.isoformat(),
                'name': a.student.name, 'email': a.student.email,
            })
        d['applicants'] = applicants
        rows.append(d)
    return JsonResponse(rows, safe=False)


@csrf_exempt
@require_http_methods(['DELETE'])
@auth_required
def opportunity_delete(request, opp_id):
    au = request.auth_user
    opp = get_object_or_404(Opportunity, id=opp_id)
    if au['role'] != 'admin' and opp.alumni_id != au['id']:
        return JsonResponse({'error': 'You can only delete your own postings.'}, status=403)
    opp.delete()
    return JsonResponse({'message': 'Opportunity deleted.'})


@csrf_exempt
@require_http_methods(['POST'])
@auth_required
@require_role('student')
def opportunity_apply(request, opp_id):
    au = request.auth_user
    opp = get_object_or_404(Opportunity, id=opp_id)
    profile = StudentProfile.objects.filter(user_id=au['id']).first()
    if not profile or not profile.resume:
        return JsonResponse({'error': 'Please upload your resume in My Profile before applying.',
                             'code': 'RESUME_REQUIRED'}, status=400)
    if Application.objects.filter(opportunity_id=opp.id, student_id=au['id']).exists():
        return JsonResponse({'error': 'You have already applied to this opportunity.'}, status=409)
    Application.objects.create(opportunity_id=opp.id, student_id=au['id'])
    return JsonResponse({'message': 'Applied successfully!'}, status=201)


@csrf_exempt
@require_http_methods(['GET'])
@auth_required
@require_role('student')
def my_applications(request):
    au = request.auth_user
    rows = []
    qs = Application.objects.filter(student_id=au['id']).select_related('opportunity').order_by('-applied_at')
    for a in qs:
        rows.append({
            'id': a.id, 'status': a.status, 'applied_at': a.applied_at.isoformat(),
            'title': a.opportunity.title, 'company': a.opportunity.company,
            'type': a.opportunity.type, 'location': a.opportunity.location,
        })
    return JsonResponse(rows, safe=False)


@csrf_exempt
@require_http_methods(['PUT'])
@auth_required
@require_role('alumni')
def application_status(request, app_id):
    au = request.auth_user
    body = parse_body(request)
    status = body.get('status')
    if status not in ('applied', 'shortlisted', 'rejected', 'selected'):
        return JsonResponse({'error': 'Invalid status.'}, status=400)

    app = get_object_or_404(Application.objects.select_related('opportunity'), id=app_id)
    if app.opportunity.alumni_id != au['id']:
        return JsonResponse({'error': 'Not your posting.'}, status=403)

    app.status = status
    app.save(update_fields=['status'])
    return JsonResponse({'message': 'Application status updated.'})


@csrf_exempt
@require_http_methods(['GET'])
@auth_required
@require_role('alumni')
def opportunity_applicants(request, opp_id):
    """Applicants of ONE posting, scored against that posting's requirements.

    Query params (all optional):
      min_match=60     only applicants matching >= 60% of required skills
      eligible=1       only applicants who pass branch + CGPA criteria
      status=applied   only a given application status
    Results are sorted best match first.
    """
    au = request.auth_user
    opp = get_object_or_404(Opportunity, id=opp_id)
    if opp.alumni_id != au['id']:
        return JsonResponse({'error': 'Not your posting.'}, status=403)

    try:
        min_match = int(request.GET.get('min_match') or 0)
    except ValueError:
        min_match = 0
    only_eligible = request.GET.get('eligible') in ('1', 'true')
    status = request.GET.get('status') or ''

    qs = Application.objects.filter(opportunity=opp).select_related('student__student_profile')
    if status:
        qs = qs.filter(status=status)

    rows = []
    for a in qs:
        profile = getattr(a.student, 'student_profile', None)
        if profile is None:
            continue
        m = match_student(opp, profile)
        if m['match_percent'] < min_match or (only_eligible and not m['eligible']):
            continue
        rows.append({
            'application_id': a.id, 'status': a.status, 'applied_at': a.applied_at.isoformat(),
            'student_id': a.student_id, 'name': a.student.name, 'email': a.student.email,
            'branch': profile.branch, 'year': profile.year,
            'cgpa': str(profile.cgpa) if profile.cgpa is not None else '',
            'skills': profile.skills, 'has_resume': bool(profile.resume),
            **m,
        })
    rows.sort(key=lambda r: r['match_percent'], reverse=True)
    return JsonResponse(rows, safe=False)
