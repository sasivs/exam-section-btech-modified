from django import forms 
from django.contrib.auth.models import Group
from MThod.models import MTCoordinator
from MTExamStaffDB.models import MTFacultyInfo




class GradesFinalizeForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(GradesFinalizeForm, self).__init__(*args, **kwargs)
        REG_CHOICES = [('', '--------')]
        if regIDs:
            REG_CHOICES += [(reg.id, reg.__str__()) for reg in regIDs]
        self.fields['regEvent'] = forms.CharField(label='Choose RegEvent', max_length=26, required=False, widget=forms.Select(choices=REG_CHOICES, attrs={'required':'True'}))


class MarksFinalizeForm(forms.Form):
    def __init__(self, regIDs, *args, **kwargs):
        super(MarksFinalizeForm, self).__init__(*args, **kwargs)
        REG_CHOICES = [('', '--------')]
        if regIDs:
            REG_CHOICES += [(reg.id, reg.__str__()) for reg in regIDs]
        self.fields['regEvent'] = forms.CharField(label='Choose RegEvent', max_length=26, required=False, widget=forms.Select(choices=REG_CHOICES,attrs={'required':'True'}))

class CoordinatorAssignmentForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(CoordinatorAssignmentForm, self).__init__(*args, **kwargs)
        COORDINATOR_CHOICES = [('', '--------')]
        USER_CHOICES = [('', '--------')]
        BYEAR_CHOICES =  [('', '--------'),(1, 1),(2, 2)]
        self.fields['MYear'] = forms.CharField(label='MYear',  required=False, widget=forms.Select(choices=BYEAR_CHOICES, attrs={'onchange':"submit()", 'required':'True'}))
        self.fields['coordinator'] = forms.CharField(label='Coordinator',  required=False, widget=forms.Select(choices=COORDINATOR_CHOICES,  attrs={'required':'True'}))
        self.fields['user'] = forms.CharField(label='User',  required=False, widget=forms.Select(choices=USER_CHOICES,  attrs={'required':'True'}))
        if self.data.get('MYear'):
            faculty= MTFacultyInfo.objects.filter(Working=True, Dept=Option) #here1
            COORDINATOR_CHOICES += [(fac.id, fac.Name) for fac in faculty]
            self.fields['coordinator'] = forms.CharField(label='Coordinator',  required=False, widget=forms.Select(choices=COORDINATOR_CHOICES,  attrs={'required':'True'}))
            group = Group.objects.filter(name='Co-ordinator').first()
            assigned_users = MTCoordinator.objects.filter(RevokeDate__isnull=True).exclude(Dept=Option,MYear=self.data.get('MYear'))
            users = group.user_set.exclude(id__in=assigned_users.values_list('User', flat=True))
            USER_CHOICES += [(user.id, user.username) for user in users]
            self.fields['user'] = forms.CharField(label='User', required=False, widget=forms.Select(choices=USER_CHOICES,  attrs={'required':'True'}))
            initial_coordinator = MTCoordinator.objects.filter(Dept=Option,MYear=self.data.get('MYear') ,RevokeDate__isnull=True).first()
            if initial_coordinator:
                self.fields['coordinator'].initial = initial_coordinator.Faculty.id
                self.fields['user'].initial = initial_coordinator.User.id

class GpaStagingForm(forms.Form):
    def __init__(self, regIds, *args,**kwargs):
        super(GpaStagingForm, self).__init__(*args, **kwargs)
        REGID_CHOICES = [('', '------------')]
        if regIds:
            REGID_CHOICES += [(reg.id, reg.__str__) for reg in regIds]
        self.fields['regId'] = forms.ChoiceField(label='Choose Event', required=False, choices=REGID_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        

# class AttendanceShoratgeStatusForm(forms.Form):
#     def __init__(self,Option=None , *args,**kwargs):
#         super(AttendanceShoratgeStatusForm, self).__init__(*args, **kwargs)
#         self.myFields=[]
#         depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
#         years = {1:'I',2:'II'}
#         sems = {1:'I',2:'II'}
#         self.regIDs = MTRegistrationStatus.objects.filter(Status=1)
#         self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation, row.id) for row in self.regIDs]
#         myChoices = [(option[7], depts[option[4]-1]+':'+ \
#                 years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
#                     ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
#         myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
#         self.fields['RegEvent'] = forms.CharField(label='Choose Registration ID', \
#             max_length=26, widget=forms.Select(choices=myChoices))