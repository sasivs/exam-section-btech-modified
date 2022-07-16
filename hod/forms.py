from django import forms 
from django.contrib.auth.models import Group
from superintendent.models import RegistrationStatus
from hod.models import Coordinator
from ExamStaffDB.models import FacultyInfo



class GradesFinalizeForm(forms.Form):
    def __init__(self, subjects, *args,**kwargs):
        super(GradesFinalizeForm, self).__init__(*args, **kwargs)
        subject_Choices=[]
        for sub in subjects:
            subject_Choices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id),sub.RegEventId.__str__()+', '+\
                str(sub.Subject.SubCode))]
        subject_Choices = [('','--Select Subject--')] + subject_Choices
        self.fields['subject'] = forms.CharField(label='Choose Subject', max_length=26, widget=forms.Select(choices=subject_Choices))



class CoordinatorAssignmentForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(CoordinatorAssignmentForm, self).__init__(*args, **kwargs)
        COORDINATOR_CHOICES = [('', '--------')]
        USER_CHOICES = [('', '--------')]
        BYEAR_CHOICES =  [('', '--------'),(2, 2),(3, 3),(4, 4)]
        self.fields['BYear'] = forms.ChoiceField(label='BYear',  required=False, choices=BYEAR_CHOICES, widget=forms.Select(attrs={'onchange':"submit()", 'required':'True'}))
        self.fields['coordinator'] = forms.ChoiceField(label='Coordinator',  required=False, choices=COORDINATOR_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        self.fields['user'] = forms.ChoiceField(label='User',  required=False, choices=USER_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        if self.data.get('BYear'):
            faculty= FacultyInfo.objects.filter(Working=True, Dept=Option) #here1
            COORDINATOR_CHOICES += [(fac.id, fac.Name) for fac in faculty]
            self.fields['coordinator'] = forms.ChoiceField(label='Coordinator', required=False, choices=COORDINATOR_CHOICES, widget=forms.Select(attrs={'required':'True'}))
            group = Group.objects.filter(name='Co-ordinator').first()
            assigned_users = Coordinator.objects.filter(RevokeDate__isnull=True).exclude(Dept=Option,BYear=self.data.get('BYear'))
            users = group.user_set.exclude(id__in=assigned_users.values_list('User', flat=True))
            USER_CHOICES += [(user.id, user.username) for user in users]
            self.fields['user'] = forms.ChoiceField(label='User', required=False, choices=USER_CHOICES, initial=10, widget=forms.Select(attrs={'required':'True'}))
            initial_coordinator = Coordinator.objects.filter(Dept=Option,BYear=self.data.get('BYear') ,RevokeDate__isnull=True).first()
            if initial_coordinator:
                self.fields['coordinator'].initial = initial_coordinator.Faculty.id
                self.fields['user'].initial = initial_coordinator.User.id


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