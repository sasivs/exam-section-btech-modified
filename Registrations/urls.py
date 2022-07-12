
from django.urls import path,include

from . import views
import Registrations

urlpatterns = [
    path('index',views.makeup_registrations, name='index'),
    path('cindex',views.makeup_registrations1, name='cindex'),
    path("logout", views.logout_request, name="logout"),
    path('private_place', views.private_place, name = 'private_place'),
    # path('BTechRegularRegistrations', views.btech_regular_registrations,name = 'BTechRegularRegistrations'),
    path('BTechMakeupMarks',views.btech_makeup_marks, name='BTechMakeupMarks'),
    path('BTechMakeupMarksPage/<str:SubCode>',views.btech_makeup_marks_page, name='BTechMakeupMarksPage'),
    path('BTechMakeupRegistrations',views.btech_makeup_registrations, name='BTechMakeupRegistrations'),
    path('BTechMakeupRegistrations1',views.btech_makeup_registrations1, name='BTechMakeupRegistrations1'),
    path('BTechMakeupRegistrationStatus',views.btech_makeup_registration_status, name='BTechMakeupRegistrationStatus'),
    path('BTechMakeupRegistrationStatus1',views.btech_makeup_registration_status1, name='BTechMakeupRegistrationStatus1'),
    path('BTechBacklogRegistrations',views.btech_backlog_registrations, name= 'BTechBacklogRegistrations' ),
    path('BTechBacklogRegistrationPage/<int:regNo>',views.btech_backlog_registration_page, name = 'BTechBacklogRegistrationPage'),
    path('BTechMakeupRegistrationPage1/<int:regNo>',views.btech_makeup_registration_page1, name = 'BTechMakeupRegistrationPage1'),
    path('BTechMakeupRegistrationPage/<int:regNo>',views.btech_makeup_registration_page, name = 'BTechMakeupRegistrationPage'),
    path('TestFormView/<int:regNo>', views.test_form_view, name='TestFormView'),
    path('success_view', views.success_view, name = 'success_view'),
    path('BTechMakeupResults',views.btech_makeup_results, name='BTechMakeupResults'),
    path('StudentMakeupMarkStatus',views.student_makeup_mark_status, name= 'StudentMakeupMarkStatus' ),
    path('BTechMakeupResultsPage/<str:SubCode>',views.student_makeup_mark_results_page, name='BTechMakeupResultsPage'),
    path('BTechMakeupResults1',views.btech_makeup_results1, name='BTechMakeupResults1'),
    path('StudentMakeupMarkStatus1',views.student_makeup_mark_status1, name= 'StudentMakeupMarkStatus1' ),
    path('BTechMakeupResultsPage1/<str:SubCode>',views.student_makeup_mark_results_page1, name='BTechMakeupResultsPage1'),
    path('BTechMakeupMarks1',views.btech_makeup_marks1, name='BTechMakeupMarks1'),
    path('BTechMakeupMarksPage1/<str:SubCode>',views.btech_makeup_marks_page1, name='BTechMakeupMarksPage1'),
    path('TestForm', views.test_form, name='TestForm'),
    path('gphome', views.gp_home, name='gphome')
]