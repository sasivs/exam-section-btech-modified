from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ADPGDB.views import create_registration_event, grade_challenge




urlpatterns = [

    path('MTCreateRegistrationEvent', create_registration_event.create_registration_event, name='MTCreateRegistrationEvent'),

    path('MTUpdateManageRegistrations', create_registration_event.update_manage_registrations,name='MTUpdateManageRegistrations'),


    path('MTGradeChallengeUpdate', grade_challenge.grade_challenge, name='MTGradeChallengeUpdate'),
    path('MTGradeChallengeStatus', grade_challenge.grade_challenge_status, name='MTGradeChallengeStatus'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)