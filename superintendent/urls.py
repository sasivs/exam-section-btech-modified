from django.urls import path
from superintendent.views import hod_assignment, IX_student



urlpatterns = [
    path('HodAssignment', hod_assignment.hod_assignment, name='HodAssignment'),
    path('IXGradeStudentsAdd', IX_student.ix_student_assignment, name='IXGradeStudentsAdd'),
]