from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Event
from .auth_utils import auth_required, parse_body


@csrf_exempt
@require_http_methods(['GET', 'POST'])
@auth_required
def events_list(request):
    au = request.auth_user

    if request.method == 'GET':
        rows = []
        for e in Event.objects.select_related('created_by').order_by('event_date'):
            rows.append({
                'id': e.id, 'created_by': e.created_by_id, 'title': e.title,
                'description': e.description, 'event_date': e.event_date, 'location': e.location,
                'created_at': e.created_at.isoformat(),
                'created_by_name': e.created_by.name, 'created_by_role': e.created_by.role,
            })
        return JsonResponse(rows, safe=False)

    # POST — admin or alumni
    if au['role'] not in ('admin', 'alumni'):
        return JsonResponse({'error': 'You are not allowed to perform this action.'}, status=403)

    body = parse_body(request)
    title, event_date = body.get('title'), body.get('event_date')
    if not title or not event_date:
        return JsonResponse({'error': 'Title and date are required.'}, status=400)

    e = Event.objects.create(
        created_by_id=au['id'], title=title, description=body.get('description') or '',
        event_date=event_date, location=body.get('location') or '',
    )
    return JsonResponse({'message': 'Event created!', 'id': e.id}, status=201)


@csrf_exempt
@require_http_methods(['DELETE'])
@auth_required
def event_delete(request, event_id):
    au = request.auth_user
    e = get_object_or_404(Event, id=event_id)
    if au['role'] != 'admin' and e.created_by_id != au['id']:
        return JsonResponse({'error': 'You can only delete your own events.'}, status=403)
    e.delete()
    return JsonResponse({'message': 'Event deleted.'})
