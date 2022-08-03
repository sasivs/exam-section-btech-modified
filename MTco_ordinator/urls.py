from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from MTco_ordinator.views import faculty_subject_assignment, grade_challenge, not_registered_registrations, subjects, RollList,\
    regular_registrations, backlog_registrations, Dec_register_all, Dec_upload_file, \
     makeupReg, status

# create your urls here


urlpatterns = [

    path('MTSupBTSubjectUpload', subjects.subject_upload, name = 'MTSupBTSubjectUpload'),
    path('MTSupBTSubjectsUploadErrorHandler', subjects.subject_upload_error_handler, name = 'MTSupBTSubjectsUploadErrorHandler'),
    path('MTSupBTSubjectUploadStatus', subjects.subject_upload_status, name = 'MTSupBTSubjectUploadStatus'),
    path('MTSupBTSubjectDelete', subjects.subject_delete, name = 'MTSupBTSubjectDelete'),
    path('MTSupBTSubjectFinalize', subjects.subject_finalize, name = 'MTSupBTSubjectFinalize'),
    path('MTDownloadSampleSubjectSheet', subjects.download_sample_subject_sheet, name='MTDownloadSampleSubjectSheet'),

    path('MTSupBTOpenSubjectUpload', subjects.open_subject_upload,name='MTSupBTOpenSubjectUpload'),


    path('MTGenerateRollList',RollList.generateRollList,name='MTGenerateRollList'),
   
    path('MTRollListFeeUpload',RollList.RollListFeeUpload,name='MTRollListFeeUpload'),
    path('MTRollListStatus',RollList.RollList_Status,name='MTRollListStatus'),
    path('MTFinalizeRollLists', RollList.rolllist_finalize, name='MTFinalizeRollLists'),
    path('MTNotRegisteredStatus',RollList.NotRegisteredStatus,name='MTNotRegisteredStatus'),


    path('MTSupBTRegistrations', regular_registrations.mtech_regular_registration, name = 'MTSupBTRegistrations'),


    path('MTDepartmentElectiveRegistrationsUpload',Dec_upload_file.dept_elective_regs_upload, name='MTDepartmentElectiveRegistrationsUpload'),
    path('MTDepartmentElectiveRegistrationsAll',Dec_register_all.dept_elective_regs_all, name='MTDepartmentElectiveRegistrationsAll'),


    path('MTMakeupRegistrations', makeupReg.makeup_registrations, name='MTMakeupRegistrations'),

    path('MTSupBTBacklogRegistrations', backlog_registrations.mtech_backlog_registration, name = 'MTSupBTBacklogRegistrations'),

    path('MTNotRegisteredRegistrations', not_registered_registrations.not_registered_registrations, name='MTNotRegisteredRegistrations'),

    path('MTSupBTRegistrationsFinalize',regular_registrations.registrations_finalize, name = 'MTSupBTRegistrationsFinalize'),


    path('MTGradeChallengeUpdate', grade_challenge.grade_challenge, name='MTGradeChallengeUpdate'),
    path('MTGradeChallengeStatus', grade_challenge.grade_challenge_status, name='MTGradeChallengeStatus'),
 
    path('MTSupBTRegularRegistrationStatus', status.mtech_regular_registration_status, name = 'MTSupBTRegularRegistrationStatus'),
    path('MTSupBTBacklogRegistrationStatus', status.mtech_backlog_registration_status, name = 'MTSupBTBacklogRegistrationStatus'),
    path('MTSupBTMakeupRegistrationStatus', status.mtech_makeup_registration_status, name='MTSupBTMakeupRegistrationStatus'),

    path('MTFacultySubjectAssignment', faculty_subject_assignment.faculty_subject_assignment, name='MTFacultySubjectAssignment'),
    path('MTFacultySubjectAssignmentDetail/<int:pk>', faculty_subject_assignment.faculty_subject_assignment_detail, name='MTFacultySubjectAssignmentDetail'),
    path('MTFacultyAssignmentStatus', faculty_subject_assignment.faculty_assignment_status, name = 'MTFacultyAssignmentStatus'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
