from django.urls import path
from co_ordinator.views.faculty_subject_assignment import faculty_subject_assignment

# create your urls here


urlpatterns = [
    path('FacultySubjectAssignment', faculty_subject_assignment.faculty_subject_assignment, name='FacultySubjectAssignment'),
    path('FacultySubjectAssignmentDetail/<int:pk>', faculty_subject_assignment.faculty_subject_assignment_detail, name='FacultySubjectAssignmentDetail'),
    path('FacultyAssignmentStatus', faculty_subject_assignment.faculty_assignment_status, name = 'FacultyAssignmentStatus'),
]