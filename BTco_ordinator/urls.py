from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from BTco_ordinator.views import faculty_subject_assignment, grade_challenge, not_registered_registrations, subjects, RollList,\
    regular_registrations, backlog_registrations, Dec_register_all, Dec_upload_file, \
    dropped_regular_regs, makeupReg, not_promoted, status

# create your urls here


urlpatterns = [

    path('BTSupBTSubjectUpload', subjects.subject_upload, name = 'BTSupBTSubjectUpload'),
    path('BTSupBTSubjectsUploadErrorHandler', subjects.subject_upload_error_handler, name = 'BTSupBTSubjectsUploadErrorHandler'),
    path('BTSupBTSubjectUploadStatus', subjects.subject_upload_status, name = 'BTSupBTSubjectUploadStatus'),
    path('BTSupBTSubjectDelete', subjects.subject_delete, name = 'BTSupBTSubjectDelete'),
    path('BTSupBTSubjectFinalize', subjects.subject_finalize, name = 'BTSupBTSubjectFinalize'),
    path('BTDownloadSampleSubjectSheet', subjects.download_sample_subject_sheet, name='BTDownloadSampleSubjectSheet'),

    path('BTSupBTOpenSubjectUpload', subjects.open_subject_upload,name='BTSupBTOpenSubjectUpload'),


    path('BTGenerateRollList',RollList.generateRollList,name='BTGenerateRollList'),
    path('BTRollListSectionUpload',RollList.UploadSectionInfo,name='BTRollListSectionUpload'),
    path('BTRollListFeeUpload',RollList.RollListFeeUpload,name='BTRollListFeeUpload'),
    path('BTFirstYearRollListsCycleHandler',RollList.first_year_rollLists_cycle_handler, name = 'BTFirstYearRollListsCycleHandler'),
    path('BTRollListStatus',RollList.RollList_Status,name='BTRollListStatus'),
    path('BTFinalizeRollLists', RollList.rolllist_finalize, name='BTFinalizeRollLists'),
    path('BTNotRegisteredStatus',RollList.NotRegisteredStatus,name='BTNotRegisteredStatus'),


    path('BTSupBTRegistrations', regular_registrations.btech_regular_registration, name = 'BTSupBTRegistrations'),


    path('BTDepartmentElectiveRegistrationsUpload',Dec_upload_file.dept_elective_regs_upload, name='BTDepartmentElectiveRegistrationsUpload'),
    path('BTDepartmentElectiveRegistrationsAll',Dec_register_all.dept_elective_regs_all, name='BTDepartmentElectiveRegistrationsAll'),

    path('BTDroppedRegularRegistrations', dropped_regular_regs.dropped_regular_registrations, name='BTDroppedRegularRegistrations'),

    path('BTMakeupRegistrations', makeupReg.makeup_registrations, name='BTMakeupRegistrations'),

    path('BTSupBTBacklogRegistrations', backlog_registrations.btech_backlog_registration, name = 'BTSupBTBacklogRegistrations'),

    path('BTNotRegisteredRegistrations', not_registered_registrations.not_registered_registrations, name='BTNotRegisteredRegistrations'),

    path('BTSupBTRegistrationsFinalize',regular_registrations.registrations_finalize, name = 'BTSupBTRegistrationsFinalize'),


    path('BTGradeChallengeUpdate', grade_challenge.grade_challenge, name='BTGradeChallengeUpdate'),
    path('BTGradeChallengeStatus', grade_challenge.grade_challenge_status, name='BTGradeChallengeStatus'),

    
    path('BTGradeChallengeStatus', grade_challenge.grade_challenge_status, name='BTGradeChallengeStatus'),
    path('BTNotPromotedList', not_promoted.not_promoted_list, name='BTNotPromotedList'),
    path('BTNotPromotedUpload', not_promoted.not_promoted_upload, name='BTNotPromotedUpload'),
    path('BTNotPromotedUploadErrorHandler', not_promoted.not_promoted_upload_error_handler, name='BTNotPromotedUploadErrorHandler'),
    path('BTNotPromotedStatus', not_promoted.not_promoted_status, name='BTNotPromotedStatus'),


    path('BTSupBTRegularRegistrationStatus', status.btech_regular_registration_status, name = 'BTSupBTRegularRegistrationStatus'),
    path('BTSupBTBacklogRegistrationStatus', status.btech_backlog_registration_status, name = 'BTSupBTBacklogRegistrationStatus'),
    path('BTSupBTMakeupRegistrationStatus', status.btech_makeup_registration_status, name='BTSupBTMakeupRegistrationStatus'),

    path('BTFacultySubjectAssignment', faculty_subject_assignment.faculty_subject_assignment, name='BTFacultySubjectAssignment'),
    path('BTFacultySubjectAssignmentDetail/<int:pk>', faculty_subject_assignment.faculty_subject_assignment_detail, name='BTFacultySubjectAssignmentDetail'),
    path('BTFacultyAssignmentStatus', faculty_subject_assignment.faculty_assignment_status, name = 'BTFacultyAssignmentStatus'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
