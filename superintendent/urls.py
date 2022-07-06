from django.urls import path
from superintendent.views.hod_assignment import hod_assignment



urlpatterns = [
    path('HodAssignment', hod_assignment.hod_assignment, name='HodAssignment'),
]