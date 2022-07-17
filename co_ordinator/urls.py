from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from co_ordinator.views import faculty_subject_assignment, grade_challenge, not_registered_registrations, subjects, RollList,\
    regular_registrations, backlog_registrations, open_elective_registrations, Dec_register_all, Dec_upload_file, \
    dropped_regular_regs, makeupReg, not_promoted, status

# create your urls here


urlpatterns = [

    path('SupBTSubjectUpload', subjects.subject_upload, name = 'SupBTSubjectUpload'),
    path('SupBTSubjectsUploadErrorHandler', subjects.subject_upload_error_handler, name = 'SupBTSubjectsUploadErrorHandler'),
    path('SupBTSubjectUploadStatus', subjects.subject_upload_status, name = 'SupBTSubjectUploadStatus'),
    path('SupBTSubjectDelete', subjects.subject_delete, name = 'SupBTSubjectDelete'),
    path('SupBTSubjectFinalize', subjects.subject_finalize, name = 'SupBTSubjectFinalize'),

    path('SupBTOpenSubjectUpload', subjects.open_subject_upload,name='SupBTOpenSubjectUpload'),


    path('GenerateRollList',RollList.generateRollList,name='GenerateRollList'),
    path('RollListSectionUpload',RollList.UploadSectionInfo,name='RollListSectionUpload'),
    path('RollListFeeUpload',RollList.RollListFeeUpload,name='RollListFeeUpload'),
    path('FirstYearRollListsCycleHandler',RollList.first_year_rollLists_cycle_handler, name = 'FirstYearRollListsCycleHandler'),
    path('RollListStatus',RollList.RollList_Status,name='RollListStatus'),
    path('FinalizeRollLists', RollList.rolllist_finalize, name='FinalizeRollLists'),
    path('NotRegisteredStatus',RollList.NotRegisteredStatus,name='NotRegisteredStatus'),


    path('SupBTRegistrations', regular_registrations.btech_regular_registration, name = 'SupBTRegistrations'),

    path('OpenElectiveRegistrations',open_elective_registrations.open_elective_regs, name='OpenElectiveRegistrations'),

    path('DepartmentElectiveRegistrationsUpload',Dec_upload_file.dept_elective_regs_upload, name='DepartmentElectiveRegistrationsUpload'),
    path('DepartmentElectiveRegistrationsAll',Dec_register_all.dept_elective_regs_all, name='DepartmentElectiveRegistrationsAll'),

    path('DroppedRegularRegistrations', dropped_regular_regs.dropped_regular_registrations, name='DroppedRegularRegistrations'),

    path('MakeupRegistrations', makeupReg.makeup_registrations, name='MakeupRegistrations'),

    path('SupBTBacklogRegistrations', backlog_registrations.btech_backlog_registration, name = 'SupBTBacklogRegistrations'),

    path('NotRegisteredRegistrations', not_registered_registrations.not_registered_registrations, name='NotRegisteredRegistrations'),

    path('SupBTRegistrationsFinalize',regular_registrations.registrations_finalize, name = 'SupBTRegistrationsFinalize'),


    path('GradeChallengeUpdate', grade_challenge.grade_challenge, name='GradeChallengeUpdate'),
    path('GradeChallengeStatus', grade_challenge.grade_challenge_status, name='GradeChallengeStatus'),

    
    path('NotPromotedList', not_promoted.not_promoted_list, name='NotPromotedList'),
    path('NotPromotedUpload', not_promoted.not_promoted_upload, name='NotPromotedUpload'),
    path('NotPromotedUploadErrorHandler', not_promoted.not_promoted_upload_error_handler, name='NotPromotedUploadErrorHandler'),
    path('NotPromotedStatus', not_promoted.not_promoted_status, name='NotPromotedStatus'),


    path('SupBTRegularRegistrationStatus', status.btech_regular_registration_status, name = 'SupBTRegularRegistrationStatus'),
    path('SupBTBacklogRegistrationStatus', status.btech_backlog_registration_status, name = 'SupBTBacklogRegistrationStatus'),
    path('SupBTMakeupRegistrationStatus', status.btech_makeup_registration_status, name='SupBTMakeupRegistrationStatus'),

    path('FacultySubjectAssignment', faculty_subject_assignment.faculty_subject_assignment, name='FacultySubjectAssignment'),
    path('FacultySubjectAssignmentDetail/<int:pk>', faculty_subject_assignment.faculty_subject_assignment_detail, name='FacultySubjectAssignmentDetail'),
    path('FacultyAssignmentStatus', faculty_subject_assignment.faculty_assignment_status, name = 'FacultyAssignmentStatus'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)