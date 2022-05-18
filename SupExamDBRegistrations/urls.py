from django.urls import path,include

from SupExamDBRegistrations.views import backlog_registrations, cancellations, first_backlog_registrations, home, manage, regular_registrations, status, subjects
from SupExamDB import views as supviews
urlpatterns = [
    path('sindex',supviews.sup_home, name='sindex'),
    path("logout", supviews.logout_request, name="logout_request"),
    path('home', supviews.sup_home, name='home'),
    path('SupBTRegistrationHome', home.registration_home, name = 'SupBTRegistrationHome'),

    path('SupBTRegistrationUpload', regular_registrations.btech_regular_registration_upload, name = 'SupBTRegistrationUpload'),
    path('SupBTRegistrationUploadErrorHandler', regular_registrations.btech_regular_registration_upload_error_handler, name = 'SupBTRegistrationUploadErrorHandler'),
    
    path('MakeupRegistrationInfo', backlog_registrations.makeup_registration_info, name='MakeupRegistrationInfo'),
    #path('DeptYearRegistrationStatus/<int:year>/<int:dept>/', regular_registrations.btech_makeup_registration_status, name='DeptYearRegistrationStatus'),
    #path('DeptYearRegistrationStatus/<int:year>/<int:dept>/', regular_registrations.btech_makeup_registration_status, name='DeptYearRegistrationStatus'),
    path('getBTBacklogRegNos/<int:dept>/<int:byear>/',regular_registrations.get_btbacklog_regnos,name='getBTBacklogRegNos'),
    path('getBTRegisteredSubjects/<int:regNo>/',regular_registrations.get_btregistered_subjects,name='getBTRegisteredSubjects'),
    
    path('SupBTBacklogRegistrations', backlog_registrations.btech_backlog_registration, name = 'SupBTBacklogRegistrations'),
    #path('SupBTBacklogRegistrationStatus', regular_registrations.btech_backlog_registration_status, name = 'SupBTBacklogRegistrationStatus'),
    #Registration Status
    path('SupBTRegistrationStatusHome', status.btech_registration_status_home, name = 'SupBTRegistrationStatusHome'),
    path('SupBTRegularRegistrationStatus', status.btech_regular_registration_status, name = 'SupBTRegularRegistrationStatus'),
    

    path('ManageRegistrations', manage.manage_registrations,name='ManageRegistrations'),
    path('BTTest',regular_registrations.test_page, name='BTTest'),
    path('SupBTFirstYearBacklogRegistrations', first_backlog_registrations.btech_first_year_backlog_Registrations ,name = 'SupBTFirstYearBacklogRegistrations'),
    path('SupBTCancellationHome',cancellations.cancellation_home,name='SupBTCancellationHome'),
    path('SupBTSeatCancellation',cancellations.seat_cancellation,name='SupBTSeatCancellation'),
    path('SupBTSemesterCancellation',cancellations.semester_cancellation,name='SupBTSemesterCancellation'),

    path('SupBTSubjectHome', subjects.subject_home, name = 'SupBTSubjectHome'),
    path('SupBTSubjectUpload', subjects.subject_upload, name = 'SupBTSubjectUpload'),
    path('SupBTSubjectsUploadErrorHandler', subjects.subject_upload_error_handler, name = 'SupBTSubjectsUploadErrorHandler'),
    path('SupBTSubjectUploadStatus', subjects.subject_upload_status, name = 'SupBTSubjectUploadStatus'),
    path('SupBTSubjectDelete', subjects.subject_delete, name = 'SupBTSubjectDelete'),
    #path('SupBTSubjectDeleteSuccess', subjects.subject_delete_success, name = 'SupBTSubjectDeleteSuccess'),
    #path('SupBTSubjectDeleteHandler/<str:event>/', subjects.subject_delete_handler, name = 'SupBTSubjectDeleteHandler'),

    path('SupBTBranchChange',backlog_registrations.branch_change, name='SupBTBranchChange'),
    path('SupBTBranchChangeStatus',backlog_registrations.branch_change_status, name='SupBTBranchChangeStatus'),
]