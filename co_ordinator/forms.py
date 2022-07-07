from django import forms 
from SupExamDBRegistrations.models import RegistrationStatus
from SupExamDBRegistrations.constants import DEPARTMENTS, YEARS, SEMS

#Create your forms here

class FacultySubjectAssignmentForm(forms.Form):
    def __init__(self, current_user, *args,**kwargs):
        super(FacultySubjectAssignmentForm, self).__init__(*args, **kwargs)
        self.regIDs = RegistrationStatus.objects.filter(Status=1, BYear=current_user.Dept)
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        myChoices = [(DEPARTMENTS[option[4]-1]+':'+ YEARS[option[2]]+':'+ SEMS[option[3]]+':'+ str(option[0])+ ':'+\
            str(option[1])+':'+str(option[6])+':'+str(option[5]), DEPARTMENTS[option[4]-1]+':'+ \
                YEARS[option[2]]+':'+ SEMS[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, \
        widget=forms.Select(choices=myChoices))

class FacultyAssignmentStatusForm(forms.Form):
    def __init__(self, faculty, *args,**kwargs):
        super(FacultyAssignmentStatusForm,self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Status=1, Dept=faculty.Dept, BYear=faculty.BYear)
        regEventIDKVs = [(reg.id,reg.__str__) for reg in regIDs]
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['regID'] = forms.CharField(label='Registration Evernt', widget = forms.Select(choices=regEventIDKVs))
