from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ADAUGDB.views import create_registration_event, grade_challenge, regulation_change,\
    first_year_cycle_handler




urlpatterns = [

    path('BTCreateRegistrationEvent', create_registration_event.create_registration_event, name='BTCreateRegistrationEvent'),

    path('BTUpdateManageRegistrations', create_registration_event.update_manage_registrations,name='BTUpdateManageRegistrations'),

    path('BTGradeChallengeUpdate', grade_challenge.grade_challenge, name='BTGradeChallengeUpdate'),
    path('BTGradeChallengeStatus', grade_challenge.grade_challenge_status, name='BTGradeChallengeStatus'),
    
    path('BTRegulationChange', regulation_change.regulation_change, name='BTRegulationChange'),
    path('BTRegulationChangeStatus', regulation_change.regulation_change_status, name='BTRegulationChangeStatus'),

    path('BTRollListCycleHandler', first_year_cycle_handler.cycle_handler, name='BTRollListCycleHandler'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)