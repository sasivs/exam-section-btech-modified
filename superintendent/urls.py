from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from superintendent.views import HOD_assignment,cancellations, Marks_Distribution, add_regulation, create_registration_event, grade_points, branch_change,\
    cycle_coordinator_assignment, home, open_elective_registrations



urlpatterns = [

    path('sindex',home.sup_home, name='sindex'),
    path("logout", home.logout_request, name="logout_request"),
    path('home', home.sup_home, name='home'),
    path('SupBTPreRegistrationHome', home.pre_registrations_home, name="SupBTPreRegistrationHome"),
    path('SupBTBranchChangeHome', home.branch_change_home, name='SupBTBranchChangeHome'),
    path('SupBTRegistrationHome', home.registration_home, name = 'SupBTRegistrationHome'),
    path('SupBTRollListHome', home.rolllist_home, name='SupBTRollListHome'),
    path('SupBTSubjectHome', home.subject_home, name = 'SupBTSubjectHome'),
    path('SupBTGradesHome', home.grades_home, name="SupBTGradesHome"),
    path('SupBTNotPromotedHome', home.not_promoted_home, name="SupBTNotPromotedHome"),
    path('SupBTFacultyHome', home.faculty_home, name='SupBTFacultyHome'),
    path('SupBTMarksHome', home.marks_home, name='SupBTMarksHome'),
    path('SupBTUserManagementHome', home.userassignment_home, name='SupBTUserManagementHome'),
    path('SupBTRegistrationStatusHome', home.btech_registration_status_home, name = 'SupBTRegistrationStatusHome'),
    path('SupBTCancellationHome', home.cancellation_home, name='SupBTCancellationHome'),

    path('AddRegulation', add_regulation.addRegulation, name = 'AddRegulation'),

    path('CreateRegistrationEvent', create_registration_event.create_registration_event, name='CreateRegistrationEvent'),

    path('UpdateManageRegistrations', create_registration_event.update_manage_registrations,name='UpdateManageRegistrations'),

    path('OpenElectiveRegistrations',open_elective_registrations.open_elective_regs, name='OpenElectiveRegistrations'),

    path('GradePointsUpload', grade_points.grade_points_upload, name='GradePointsUpload'),
    path('GradePointsStatus', grade_points.grade_points_status, name='GradePointsStatus'),
    path('GradePointsUploadErrorHandler', grade_points.grade_points_upload_error_handler, name='GradePointsUploadErrorHandler'),


    path('SupBTBranchChange',branch_change.branch_change, name='SupBTBranchChange'),
    path('SupBTBranchChangeStatus',branch_change.branch_change_status, name='SupBTBranchChangeStatus'),

    path('HodAssignment', HOD_assignment.hod_assignment, name='HodAssignment'),
    path('HodAssignmentStatus', HOD_assignment.hod_assignment_status, name='HodAssignmentStatus'),

    path('CycleCoordinatorAssignment', cycle_coordinator_assignment.cycle_coordinator_assignment, name='CycleCoordinatorAssignment'),
    path('CycleCoordinatorAssignmentStatus', cycle_coordinator_assignment.cycle_coordinator_assignment_status, name='CycleCoordinatorAssignmentStatus'),


    path('AddMarkDistribution', Marks_Distribution.mark_distribution_add, name='AddMarkDistribution'),
    path('MarkDistributionStatus', Marks_Distribution.mark_distribution_status, name='MarkDistributionStatus'),

    path('SupBTSeatCancellation',cancellations.seat_cancellation,name='SupBTSeatCancellation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)