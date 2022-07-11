from django.urls import path
from ExamStaffDB.views import IX_student
from superintendent.views import HOD_assignment, Marks_Distribution, add_regulation, create_registration_event, grade_points,\
    mandatory_credits



urlpatterns = [

    path('AddRegulation', add_regulation.addRegulation, name = 'AddRegulation'),

    path('ManageRegistrations', create_registration_event.manage_registrations,name='ManageRegistrations'),


    path('MandatoryCredits',mandatory_credits.mandatory_credits_upload, name='MandatoryCredits'),


    path('GradePointsUpload', grade_points.grade_points_upload, name='GradePointsUpload'),
    path('GradePointsUploadErrorHandler', grade_points.grade_points_upload_error_handler, name='GradePointsUploadErrorHandler'),

    path('HodAssignment', HOD_assignment.hod_assignment, name='HodAssignment'),
    path('AddMarkDistribution', Marks_Distribution.mark_distribution_add, name='AddMarkDistribution'),
    path('MarkDistributionStatus', Marks_Distribution.mark_distribution_status, name='MarkDistributionStatus'),
]