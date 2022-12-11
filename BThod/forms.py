from django import forms 
from django.contrib.auth.models import Group
from numpy import require
from BThod.models import BTCoordinator
from BTExamStaffDB.models import BTFacultyInfo
from BTco_ordinator.models import BTStudentRegistrations, BTNotRegistered



class GradesFinalizeForm(forms.Form):
    def __init__(self, regIDs, *args, **kwargs):
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
        BYEAR_CHOICES =  [('', '--------'),(2, 2),(3, 3),(4, 4)]
        self.fields['BYear'] = forms.ChoiceField(label='BYear',  required=False, choices=BYEAR_CHOICES, widget=forms.Select(attrs={'onchange':"submit()", 'required':'True'}))
        self.fields['coordinator'] = forms.ChoiceField(label='Coordinator',  required=False, choices=COORDINATOR_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        self.fields['user'] = forms.ChoiceField(label='User',  required=False, choices=USER_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        if self.data.get('BYear'):
            faculty= BTFacultyInfo.objects.filter(Working=True, Dept=Option) #here1
            COORDINATOR_CHOICES += [(fac.id, fac.Name) for fac in faculty]
            self.fields['coordinator'] = forms.ChoiceField(label='Coordinator', required=False, choices=COORDINATOR_CHOICES, widget=forms.Select(attrs={'required':'True'}))
            group = Group.objects.filter(name='Co-ordinator').first()
            assigned_users = BTCoordinator.objects.filter(RevokeDate__isnull=True).exclude(Dept=Option,BYear=self.data.get('BYear'))
            users = group.user_set.exclude(id__in=assigned_users.values_list('User', flat=True))
            USER_CHOICES += [(user.id, user.username) for user in users]
            self.fields['user'] = forms.ChoiceField(label='User', required=False, choices=USER_CHOICES, initial=10, widget=forms.Select(attrs={'required':'True'}))
            initial_coordinator = BTCoordinator.objects.filter(Dept=Option,BYear=self.data.get('BYear') ,RevokeDate__isnull=True).first()
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
        
            
class DeptStudentStatusForm(forms.Form):
    def __init__(self, *args,**kwargs):
        import datetime
        super(DeptStudentStatusForm, self).__init__(*args, **kwargs)
        ADMISSION_YEAR_CHOICES = [(0,'Select AdmYear')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        self.fields['AdmYear'] = forms.IntegerField(label='Select AdmYear', required=False, widget=forms.Select(choices=ADMISSION_YEAR_CHOICES,attrs={'onchange':'submit();', 'required':'True'}))

class StudentHistoryForm(forms.Form):
    def __init__(self, student, *args,**kwargs):
        super(StudentHistoryForm, self).__init__(*args, **kwargs)
        registrations = BTStudentRegistrations.objects.filter(student__student__RegNo=student.RegNo).distinct('RegEventId__AYear').values_list('RegEventId__AYear', flat=True)
        not_registered = BTNotRegistered.objects.filter(Student__RegNo=student.RegNo).distinct('RegEventId__AYear').values_list('RegEventId__AYear', flat=True)
        ayears = registrations.distinct('RegEventId__AYear').values_list('RegEventId__AYear', flat=True)+not_registered.distinct('RegEventId__AYear').values_list('RegEventId__AYear', flat=True)
        AYEAR_CHOICES = [('', 'Choose year')]+[(ayear, ayear) for ayear in set(ayears)]
        self.fields['AYear'] = forms.IntegerField(label='Select Acad. year', required=False, widget=forms.Select(choices=AYEAR_CHOICES,attrs={'onchange':'submit();', 'required':'True'}))
        if self.data.get('AYear'):
            reg_events = registrations.distinct('RegEventId_id')
            nr_events = not_registered.distinct('RegEventId_id')
            REGEVENT_CHOICES = [('', 'Choose Event')]+[(event.id, event.__str__()) for event in reg_events]+\
                [(event.id, event.__str__()) for event in nr_events]
            REGEVENT_CHOICES = list(set(REGEVENT_CHOICES))
            self.fields['event'] = forms.CharField(label='Select event', required=False, widget=forms.Select(choices=REGEVENT_CHOICES, attrs={'required':'True'}))
            

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