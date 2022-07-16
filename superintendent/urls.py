from django.urls import path
from superintendent.views import HOD_assignment,cancellations, Marks_Distribution, add_regulation, create_registration_event, grade_points, branch_change,\
    cycle_coordinator_assignment



urlpatterns = [

    path('AddRegulation', add_regulation.addRegulation, name = 'AddRegulation'),

    path('ManageRegistrations', create_registration_event.manage_registrations,name='ManageRegistrations'),


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