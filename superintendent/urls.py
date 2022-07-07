from django.urls import path
from superintendent.models import MarksDistribution
from superintendent.views import HOD_assignment, Marks_Distribution


urlpatterns = [
    path('HodAssignment', HOD_assignment.hod_assignment, name='HodAssignment'),
    path('AddMarkDistribution', Marks_Distribution.mark_distribution_add, name='AddMarkDistribution'),
]