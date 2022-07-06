from unicodedata import name
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

from SupExamDBRegistrations.views import  faculty_user_assignment, backlog_registrations, cancellations, first_backlog_registrations, grades, \
    home, manage, open_elective_registrations, grades,attendance_shortage,\
    regular_registrations, status, subjects, StudInfo, RollList, branch_change, add_regulation, \
        Dec_upload_file,Dec_register_all, dropped_regular_regs, makeupReg, not_promoted, mandatory_credits, grade_points, FacultyAssignment
from SupExamDB import views as supviews
# from SupExamDBRegistrations.views.mandatory_credits import mandatory_credits
urlpatterns = [
    path('sindex',supviews.sup_home, name='sindex'),
    path("logout", supviews.logout_request, name="logout_request"),
    path('home', supviews.sup_home, name='home'),
    path('SupBTPreRegistrationHome', home.pre_registrations_home, name="SupBTPreRegistrationHome"),
    path('SupBTBranchChangeHome', home.branch_change_home, name='SupBTBranchChangeHome'),
    path('SupBTRegistrationHome', home.registration_home, name = 'SupBTRegistrationHome'),
    path('SupBTRollListHome', home.rolllist_home, name='SupBTRollListHome'),
    path('SupBTSubjectHome', subjects.subject_home, name = 'SupBTSubjectHome'),
    path('SupBTGradesHome', home.grades_home, name="SupBTGradesHome"),
    path('SupBTNotPromotedHome', home.not_promoted_home, name="SupBTNotPromotedHome"),
    path('SupBTFacultyHome', home.faculty_home, name='SupBTFacultyHome'),

    path('FacultyInfoUpload', FacultyAssignment.faculty_upload, name = 'FacultyInfoUpload'),
    path('FacultyInfoUploadErrorHandler', FacultyAssignment.FacultyInfo_upload_error_handler, name = 'FacultyInfoUploadErrorHandler'),
    path('FacultyInfoStatus', FacultyAssignment.FacultyInfo_upload_status, name = 'FacultyInfoStatus'),
    path('FacultyInfoDeletion', FacultyAssignment.Faculty_delete, name = 'FacultyInfoDeletion'),
    path('FacultyAssignment', FacultyAssignment.faculty_assignment, name = 'FacultyAssignment'),
    path('FacultyAssignmentStatus', FacultyAssignment.faculty_assignment_status, name = 'FacultyAssignmentStatus'),
    path('FacultyAssignemntDetail/<int:pk>', FacultyAssignment.faculty_assignment_detail, name='FacultyAssignmentDetail'),
    path('FacultyUserAssignment', faculty_user_assignment.faculty_user, name = 'FacultyUserAssignment'),
    path('FacultyUserDetail/<int:pk>', faculty_user_assignment.faculty_user_detail, name='FacultyUserDetail'),
    path('FacultyUserRevoke/<int:pk>', faculty_user_assignment.faculty_user_revoke, name='FacultyUserRevoke'),

    path('FacultyCoordinatorAssignment', faculty_user_assignment.faculty_Coordinator, name = 'FacultyCoordinatorAssignment'),
    path('FacultyCoordinatorDetail/<int:pk>', faculty_user_assignment.faculty_Coordinator_detail, name='FacultyCoordinatorDetail'),
    path('FacultyCoordinatorRevoke/<int:pk>', faculty_user_assignment.faculty_Coordinator_revoke, name='FacultyCoordinatorRevoke'),
    


    path('AddRegulation', add_regulation.addRegulation, name = 'AddRegulation'),

    path('StudentInfoFileUpload',StudInfo.StudInfoFileUpload, name = 'StudentInfoFileUpload'),
    path('StudentInfoUploadErrorHandler', StudInfo.student_info_error_handler, name = 'StudentInfoUploadErrorHandler'),
    path('UpdateRollNumber', StudInfo.update_rollno, name='UpdateRollNumber'),
    path('UpdateNonFirstYearSection', StudInfo.update_non_first_year_section, name='UpdateNonFirstYearSection'),

    path('SupBTRegistrations', regular_registrations.btech_regular_registration, name = 'SupBTRegistrations'),
    path('SupBTRegistrationsFinalize',regular_registrations.registrations_finalize, name = 'SupBTRegistrationsFinalize'),
    # path('SupBTRegistrationUploadErrorHandler', regular_registrations.btech_regular_registration_upload_error_handler, name = 'SupBTRegistrationUploadErrorHandler'),
    
    # path('MakeupRegistrationInfo', backlog_registrations.makeup_registration_info, name='MakeupRegistrationInfo'),
    #path('DeptYearRegistrationStatus/<int:year>/<int:dept>/', regular_registrations.btech_makeup_registration_status, name='DeptYearRegistrationStatus'),
    #path('DeptYearRegistrationStatus/<int:year>/<int:dept>/', regular_registrations.btech_makeup_registration_status, name='DeptYearRegistrationStatus'),
    # path('getBTBacklogRegNos/<int:dept>/<int:byear>/',regular_registrations.get_btbacklog_regnos,name='getBTBacklogRegNos'),
    # path('getBTRegisteredSubjects/<int:regNo>/',regular_registrations.get_btregistered_subjects,name='getBTRegisteredSubjects'),
    
    # path('SupBTBacklogRegistrations', backlog_registrations.btech_backlog_registration, name = 'SupBTBacklogRegistrations'),
    #Registration Status
    path('SupBTBacklogRegistrationStatus', status.btech_backlog_registration_status, name = 'SupBTBacklogRegistrationStatus'),
    path('SupBTRegistrationStatusHome', status.btech_registration_status_home, name = 'SupBTRegistrationStatusHome'),
    path('SupBTRegularRegistrationStatus', status.btech_regular_registration_status, name = 'SupBTRegularRegistrationStatus'),
    path('SupBTMakeupRegistrationStatus', status.btech_makeup_registration_status, name='SupBTMakeupRegistrationStatus'),
    

    path('ManageRegistrations', manage.manage_registrations,name='ManageRegistrations'),
    # path('BTTest',regular_registrations.test_page, name='BTTest'),
    # path('SupBTFirstYearBacklogRegistrations', first_backlog_registrations.btech_first_year_backlog_Registrations ,name = 'SupBTFirstYearBacklogRegistrations'),
    path('SupBTCancellationHome',cancellations.cancellation_home,name='SupBTCancellationHome'),
    path('SupBTSeatCancellation',cancellations.seat_cancellation,name='SupBTSeatCancellation'),
    path('SupBTSemesterCancellation',cancellations.semester_cancellation,name='SupBTSemesterCancellation'),

    path('SupBTSubjectUpload', subjects.subject_upload, name = 'SupBTSubjectUpload'),
    path('SupBTSubjectsUploadErrorHandler', subjects.subject_upload_error_handler, name = 'SupBTSubjectsUploadErrorHandler'),
    path('SupBTSubjectUploadStatus', subjects.subject_upload_status, name = 'SupBTSubjectUploadStatus'),
    path('SupBTSubjectDelete', subjects.subject_delete, name = 'SupBTSubjectDelete'),
    path('SupBTSubjectFinalize', subjects.subject_finalize, name = 'SupBTSubjectFinalize'),
    #path('SupBTSubjectDeleteSuccess', subjects.subject_delete_success, name = 'SupBTSubjectDeleteSuccess'),
    #path('SupBTSubjectDeleteHandler/<str:event>/', subjects.subject_delete_handler, name = 'SupBTSubjectDeleteHandler'),

    path('SupBTBranchChange',branch_change.branch_change, name='SupBTBranchChange'),
    path('SupBTBranchChangeStatus',branch_change.branch_change_status, name='SupBTBranchChangeStatus'),
    path('GenerateRollList',RollList.generateRollList,name='GenerateRollList'),
    path('RollListSectionUpload',RollList.UploadSectionInfo,name='RollListSectionUpload'),
    path('RollListFeeUpload',RollList.RollListFeeUpload,name='RollListFeeUpload'),

    path('FirstYearRollListsCycleHandler',RollList.first_year_rollLists_cycle_handler, name = 'FirstYearRollListsCycleHandler'),
    path('RollListStatus',RollList.RollList_Status,name='RollListStatus'),
    path('FinalizeRollLists', RollList.rolllist_finalize, name='FinalizeRollLists'),
    path('NotRegisteredStatus',RollList.NotRegisteredStatus,name='NotRegisteredStatus'),

    path('OpenElectiveRegistrations',open_elective_registrations.open_elective_regs, name='OpenElectiveRegistrations'),
    path('DepartmentElectiveRegistrationsUpload',Dec_upload_file.dept_elective_regs_upload, name='DepartmentElectiveRegistrationsUpload'),
    path('DepartmentElectiveRegistrationsAll',Dec_register_all.dept_elective_regs_all, name='DepartmentElectiveRegistrationsAll'),

    path('SupBTOpenSubjectUpload', subjects.open_subject_upload,name='SupBTOpenSubjectUpload'),

    path('DroppedRegularRegistrations', dropped_regular_regs.dropped_regular_registrations, name='DroppedRegularRegistrations'),

    path('GradesUpload', grades.upload_grades, name='GradesUpload'),
    path('GradesUploadErrorHandler', grades.grades_upload_error_handler, name='GradesUploadErrorHandler'),
    path('GradesFinalize', grades.grades_finalize, name='GradesFinalize'),

    path('MakeupRegistrations', makeupReg.makeup_registrations, name='MakeupRegistrations'),

    path('NotPromotedList', not_promoted.not_promoted_list, name='NotPromotedList'),


    path('NotPromotedUpload', not_promoted.not_promoted_upload, name='NotPromotedUpload'),
    path('NotPromotedUploadErrorHandler', not_promoted.not_promoted_upload_error_handler, name='NotPromotedUploadErrorHandler'),
    path('NotPromotedStatus', not_promoted.not_promoted_status, name='NotPromotedStatus'),

    path('NotPromotedBModeRegistrations', not_promoted.not_promoted_backlog_mode_regs, name='NotPromotedBModeRegistrations'),

    path('MandatoryCredits',mandatory_credits.mandatory_credits_upload, name='MandatoryCredits'),

    path('GradePointsUpload', grade_points.grade_points_upload, name='GradePointsUpload'),
    path('GradePointsUploadErrorHandler', grade_points.grade_points_upload_error_handler, name='GradePointsUploadErrorHandler'),

    path('GradeChallenge', grades.grade_challenge, name='GradeChallenge'),

    path('AttendanceShoratgeUpload',attendance_shortage.attendance_shortage_upload,name='AttendanceShoratgeUpload'),
    path('AttendanceShoratgeStatus',attendance_shortage.attendance_shortage_status,name='AttendanceShoratgeStatus'),
    path('AttendanceShoratgeDelete/<int:pk>',attendance_shortage.attendance_shortage_delete,name='AttendanceShoratgeDelete'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
