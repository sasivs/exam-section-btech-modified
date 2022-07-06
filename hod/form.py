from email.policy import default
from operator import itemgetter
from random import choices
from shutil import SpecialFileError
from .models import  FacultyInfo,Faculty_user,Coordinator
from django import forms 
from django.forms import CheckboxInput, RadioSelect, ValidationError
from django.db.models import F, Q 
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
import datetime



class CoordinatorAssignmentForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(CoordinatorAssignmentForm, self).__init__(*args, **kwargs)
        self.myFields=[]
        already_assigned = Coordinator.objects.filter(RevokeDate__isnull=True)
        g = Group.objects.filter(name='Co-ordinator').first()
        users = g.user_set.all().exclude(id__in=already_assigned.values_list('User_id', flat=True))










# class AttendanceShoratgeStatusForm(forms.Form):
#     def __init__(self,Option=None , *args,**kwargs):
#         super(AttendanceShoratgeStatusForm, self).__init__(*args, **kwargs)
#         self.myFields=[]
#         depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
#         years = {1:'I',2:'II',3:'III',4:'IV'}
#         sems = {1:'I',2:'II'}
#         self.regIDs = RegistrationStatus.objects.filter(Status=1)
#         self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation, row.id) for row in self.regIDs]
#         myChoices = [(option[7], depts[option[4]-1]+':'+ \
#                 years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
#                     ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
#         myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
#         self.fields['RegEvent'] = forms.CharField(label='Choose Registration ID', \
#             max_length=26, widget=forms.Select(choices=myChoices))