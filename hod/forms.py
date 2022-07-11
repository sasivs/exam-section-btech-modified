from django import forms 
from django.contrib.auth.models import Group
from superintendent.models import RegistrationStatus
from hod.models import Coordinator, FacultyInfo



class GradesFinalizeForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(GradesFinalizeForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1)
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices))


class FacultyUploadForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(FacultyUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField()


class FacultyInfoUpdateForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(FacultyInfoUpdateForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + str(Options[fi][0])] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+str(Options[fi][0])].initial = False  
            self.checkFields.append(self['Check' + str(Options[fi][0])])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3],Options[fi][4],Options[fi][5], self['Check' + str(Options[fi][0])]))


class FacultyDeletionForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(FacultyDeletionForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + str(Options[fi][0])] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+str(Options[fi][0])].initial = False  
            self.checkFields.append(self['Check' + str(Options[fi][0])])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3],Options[fi][4],Options[fi][5], self['Check' + str(Options[fi][0])]))



class CoordinatorAssignmentForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(CoordinatorAssignmentForm, self).__init__(*args, **kwargs)
        # self.myFields=[]
        # already_assigned = Coordinator.objects.filter(RevokeDate__isnull=True)
        # g = Group.objects.filter(name='Co-ordinator').first()
        # users = g.user_set.all().exclude(id__in=already_assigned.values_list('User_id', flat=True))
        
      
        COORDINATOR_CHOICES = [('', '--------')]
        USER_CHOICES = [('', '--------')]
        BYEAR_CHOICES =  [('', '--------'),(1,1), (2, 2),(3, 3),(4, 4)]
        self.fields['BYear'] = forms.CharField(label='BYear', widget=forms.Select(choices=BYEAR_CHOICES, attrs={'onchange':"submit()"}))
        self.fields['coordinator'] = forms.CharField(label='HOD', widget=forms.Select(choices=COORDINATOR_CHOICES))
        self.fields['user'] = forms.CharField(label='User', widget=forms.Select(choices=USER_CHOICES))
        if self.data.get('BYear'):
            faculty= FacultyInfo.objects.filter(working=True, Dept=Option) #here1
            COORDINATOR_CHOICES += [(fac.id, fac.Name) for fac in faculty]
            self.fields['coordinator'] = forms.CharField(label='Coordinator', widget=forms.Select(choices=COORDINATOR_CHOICES))
            group = Group.objects.filter(name='Co_ordinator').first()
            assigned_users = Coordinator.objects.filter(RevokeDate__isnull=True).exclude(Dept=Option,BYear=self.data.get('BYear'))
            users = group.user_set.exclude(id__in=assigned_users.values_list('User', flat=True))
            self.fields['user'] = forms.CharField(label='User', widget=forms.Select(choices=USER_CHOICES))
            USER_CHOICES += [(user.id, user.username) for user in users]
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