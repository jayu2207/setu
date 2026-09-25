from django.urls import path
from . import views_auth, views_profile, views_opportunities, views_mentorship, views_events, views_admin

urlpatterns = [
    # ---------- auth ----------
    path('auth/register', views_auth.register),
    path('auth/login', views_auth.login),

    # ---------- profile ----------
    path('profile/me', views_profile.me),
    path('profile/alumni', views_profile.list_alumni),

    # ---------- opportunities ----------
    path('opportunities', views_opportunities.opportunities_list),
    path('opportunities/mine', views_opportunities.opportunities_mine),
    path('opportunities/my/applications', views_opportunities.my_applications),
    path('opportunities/applications/<int:app_id>/status', views_opportunities.application_status),
    path('opportunities/<int:opp_id>', views_opportunities.opportunity_delete),
    path('opportunities/<int:opp_id>/apply', views_opportunities.opportunity_apply),

    # ---------- mentorship ----------
    path('mentorship', views_mentorship.send_request),
    path('mentorship/sent', views_mentorship.sent_requests),
    path('mentorship/received', views_mentorship.received_requests),
    path('mentorship/<int:req_id>/status', views_mentorship.update_request_status),

    # ---------- events ----------
    path('events', views_events.events_list),
    path('events/<int:event_id>', views_events.event_delete),

    # ---------- admin ----------
    path('admin/stats', views_admin.stats),
    path('admin/users', views_admin.list_users),
    path('admin/users/<int:user_id>/status', views_admin.update_user_status),
    path('admin/users/<int:user_id>', views_admin.delete_user),
    path('admin/opportunities', views_admin.all_opportunities),
    path('admin/mentorship', views_admin.all_mentorship),
    path('admin/events', views_admin.all_events),
]
