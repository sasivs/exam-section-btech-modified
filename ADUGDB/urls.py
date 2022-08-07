from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ADUGDB.views import create_registration_event, grade_challenge




urlpatterns = [

    path('BTCreateRegistrationEvent', create_registration_event.create_registration_event, name='BTCreateRegistrationEvent'),

    path('BTUpdateManageRegistrations', create_registration_event.update_manage_registrations,name='BTUpdateManageRegistrations'),

    path('BTGradeChallengeUpdate', grade_challenge.grade_challenge, name='BTGradeChallengeUpdate'),
    path('BTGradeChallengeStatus', grade_challenge.grade_challenge_status, name='BTGradeChallengeStatus'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)