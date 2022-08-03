from django import forms
# from django import forms
# from Transcripts.models import BTProgrammeModel
# from .models import BTFacultyInfo
# from import_export import resources
# from django.forms.widgets import CheckboxInput, RadioSelect

# class DeptYearSelectionForm(forms.Form,):
#     departments = BTProgrammeModel.objects.filter(ProgrammeType='UG')
#     deptChoices =[(rec.Dept, rec.Specialization) for rec in departments]
#     yearChoices = [(1, 1),(2, 2),(3, 3),(4, 4)]
#     deptBox = forms.CharField(label='Select Department', widget=forms.Select(choices=deptChoices))
#     yearBox = forms.IntegerField(label='Select Year', widget=forms.Select(choices=yearChoices))
#     #print(deptChoices,deptChoices)


class UploadFileForm(forms.Form):
    file = forms.FileField()


class FacultyUpdateForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(FacultyUpdateForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + Options[fi][0]] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+Options[fi][0]].initial = False  
            self.checkFields.append(self['Check' + Options[fi][0]])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2], self['Check' + Options[fi][0]]))

