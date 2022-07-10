from django.urls import path
from co_ordinator.views import faculty_subject_assignment, grade_challenge, not_registered_registrations

# create your urls here


urlpatterns = [
    path('FacultySubjectAssignment', faculty_subject_assignment.faculty_subject_assignment, name='FacultySubjectAssignment'),
    path('FacultySubjectAssignmentDetail/<int:pk>', faculty_subject_assignment.faculty_subject_assignment_detail, name='FacultySubjectAssignmentDetail'),
    path('FacultyAssignmentStatus', faculty_subject_assignment.faculty_assignment_status, name = 'FacultyAssignmentStatus'),
    path('GradeChallengeUpdate', grade_challenge.grade_challenge, name='GradeChallengeUpdate'),
    path('GradeChallengeStatus', grade_challenge.grade_challenge_status, name='GradeChallengeStatus'),
    path('NotRegisteredRegistrations', not_registered_registrations.not_registered_registrations, name='NotRegisteredRegistrations'),
]