from django.urls import path
from superintendent.views import HOD_assignment, IX_student, Marks_Distribution



urlpatterns = [
    path('HodAssignment', HOD_assignment.hod_assignment, name='HodAssignment'),
    path('IXGradeStudentsAdd', IX_student.ix_student_assignment, name='IXGradeStudentsAdd'),
    path('AddMarkDistribution', Marks_Distribution.mark_distribution_add, name='AddMarkDistribution'),
    path('MarkDistributionStatus', Marks_Distribution.mark_distribution_status, name='MarkDistributionStatus'),

]