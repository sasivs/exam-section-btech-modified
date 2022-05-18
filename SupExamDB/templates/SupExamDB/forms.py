from Registrations import forms
from django import forms
from Transcripts.models import ProgrammeModel 

class DeptYearSelectionForm(forms.Form,):
    departments = ProgrammeModel.objects.filter(ProgrammeType='UG')
    deptChoices =[(rec.Dept, rec.Specialization) for rec in departments]
    yearChoices = [(1, 1),(2, 2),(3, 3),(4, 4)]
    deptBox = forms.CharField(label='Select Department', widget=forms.Select(choices=deptChoices))
    yearBox = forms.IntegerField(label='Select Year', widget=forms.Select(choices=yearChoices))
    #print(deptChoices,deptChoices)
    