from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ADAUGDB.views import hod_assignment,cancellations, Marks_Distribution, add_regulation, grade_points ,\
    cycle_coordinator_assignment, open_elective_registrations, course_structure, courses, open_elective_rollList, create_registration_event,\
        regulation_change, first_year_cycle_handler
urlpatterns = [

    # path('BTsindex',home.sup_home, name='BTsindex'),
    # path("BTlogout", home.logout_request, name="BTlogout_request"),
    # path('BThome', home.sup_home, name='BThome'),
    # path('BTSupBTPreRegistrationHome', home.pre_registrations_home, name="BTSupBTPreRegistrationHome"),
    # path('BTSupBTBranchChangeHome', home.branch_change_home, name='BTSupBTBranchChangeHome'),
    # path('BTSupBTRegistrationHome', home.registration_home, name = 'BTSupBTRegistrationHome'),
    # path('BTSupBTRollListHome', home.rolllist_home, name='BTSupBTRollListHome'),
    # path('BTSupBTSubjectHome', home.subject_home, name = 'BTSupBTSubjectHome'),
    # path('BTSupBTGradesHome', home.grades_home, name="BTSupBTGradesHome"),
    # path('BTSupBTNotPromotedHome', home.not_promoted_home, name="BTSupBTNotPromotedHome"),
    # path('BTYearMandatoryCredits',mandatory_credits.mandatory_credits_upload, name='BTYearMandatoryCredits'),
 
    # path('BTSupBTFacultyHome', home.faculty_home, name='BTSupBTFacultyHome'),
    # path('BTSupBTMarksHome', home.marks_home, name='BTSupBTMarksHome'),
    # path('BTSupBTUserManagementHome', home.userassignment_home, name='BTSupBTUserManagementHome'),
    # path('BTSupBTRegistrationStatusHome', home.btech_registration_status_home, name = 'BTSupBTRegistrationStatusHome'),
    # path('BTSupBTCancellationHome', home.cancellation_home, name='BTSupBTCancellationHome'),

    path('BTAddRegulation', add_regulation.addRegulation, name = 'BTAddRegulation'),

    path('BTAddCourseStructure', course_structure.add_course_structre, name = 'BTAddCourseStructure'),
    path('BTCourseStructureStatus', course_structure.course_structure_status, name = 'BTCourseStructureStatus'),
    path('BTCourseStructureDelete', course_structure.course_structure_delete, name = 'BTCourseStructureDelete'),
    path('BTAddCourses', courses.add_courses, name = 'BTAddCourses'),
    path('BTCoursesStatus', courses.course_upload_status, name='BTCoursesStatus'),


    path('BTCreateRegistrationEvent', create_registration_event.create_registration_event, name='BTCreateRegistrationEvent'),

    path('BTUpdateManageRegistrations', create_registration_event.update_manage_registrations,name='BTUpdateManageRegistrations'),

    path('BTOpenElectiveRegistrations',open_elective_registrations.open_elective_regs, name='BTOpenElectiveRegistrations'),
    path('BTOpenElectiveRegistrationsFinalilze',open_elective_registrations.open_elective_regs_finalize, name='BTOpenElectiveRegistrationsFinalize'),

    path('BTGradePointsUpload', grade_points.grade_points_upload, name='BTGradePointsUpload'),
    path('BTGradePointsStatus', grade_points.grade_points_status, name='BTGradePointsStatus'),
    path('BTGradePointsUploadErrorHandler', grade_points.grade_points_upload_error_handler, name='BTGradePointsUploadErrorHandler'),


    # path('BTSupBTBranchChange',branch_change.branch_change, name='BTSupBTBranchChange'),
    # path('BTSupBTBranchChangeStatus',branch_change.branch_change_status, name='BTSupBTBranchChangeStatus'),

    path('BTHodAssignment', hod_assignment.hod_assignment, name='BTHodAssignment'),
    path('BTHodAssignmentStatus', hod_assignment.hod_assignment_status, name='BTHodAssignmentStatus'),

    path('BTCycleCoordinatorAssignment', cycle_coordinator_assignment.cycle_coordinator_assignment, name='BTCycleCoordinatorAssignment'),
    path('BTCycleCoordinatorAssignmentStatus', cycle_coordinator_assignment.cycle_coordinator_assignment_status, name='BTCycleCoordinatorAssignmentStatus'),


    path('BTAddMarkDistribution', Marks_Distribution.mark_distribution_add, name='BTAddMarkDistribution'),
    path('BTMarkDistributionStatus', Marks_Distribution.mark_distribution_status, name='BTMarkDistributionStatus'),
    path('BTMarksDistributionUpdate/<int:pk>', Marks_Distribution.mark_distribution_update, name='BTMarksDistributionUpdate'),

    path('BTSupBTSeatCancellation',cancellations.seat_cancellation,name='BTSupBTSeatCancellation'),
    path('BTSupBTSeatCancellationStatus',cancellations.seat_cancellation_status,name='BTSupBTSeatCancellationStatus'),

    # path('BTHeldIn', heldin.update_heldin, name='BTHeldIn'),


    path('BTOERollList', open_elective_rollList.open_elective_rollList, name='BTOERollList'),
    path('BTOERollListStatus',open_elective_rollList.OERollList_Status,name='BTOERollListStatus'),
    path('BTCreateRegistrationEvent', create_registration_event.create_registration_event, name='BTCreateRegistrationEvent'),

    path('BTUpdateManageRegistrations', create_registration_event.update_manage_registrations,name='BTUpdateManageRegistrations'),

    # path('BTGradeChallengeUpdate', grade_challenge.grade_challenge, name='BTGradeChallengeUpdate'),
    # path('BTGradeChallengeStatus', grade_challenge.grade_challenge_status, name='BTGradeChallengeStatus'),
    
    path('BTRegulationChange', regulation_change.regulation_change, name='BTRegulationChange'),
    path('BTRegulationChangeStatus', regulation_change.regulation_change_status, name='BTRegulationChangeStatus'),

    path('BTRollListCycleHandler', first_year_cycle_handler.cycle_handler, name='BTRollListCycleHandler'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)