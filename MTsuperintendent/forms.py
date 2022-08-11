from django import forms
from django.contrib.auth.models import Group
from django.db.models import Q
from MTsuperintendent.models import MTHOD
from MTExamStaffDB.models import MTFacultyInfo, MTStudentInfo
from ADPGDB.models import MTRegistrationStatus
from MTsuperintendent.models import MTDepartments, MTRegulation
from MTco_ordinator.models import MTStudentBacklogs
import datetime
from MTsuperintendent.validators import validate_file_extension


# Register your models here.


class AddRegulationForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(AddRegulationForm, self).__init__(*args, **kwargs)
        admYear = [(0,'--Select AdmYear')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        aYearChoices = [(0,'--Select AYear')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        mYearChoices = [(0,'--Select MYear--'),(1,1), (2, 2)]
        aYearBox = forms.IntegerField(required = True,label='Select AYear', widget=forms.Select(choices=aYearChoices))
        mYearBox = forms.IntegerField(required = True,label='Select MYear', widget=forms.Select(choices=mYearChoices))
        admYearBox = forms.IntegerField(required = True,label='Select AdmYear', widget=forms.Select(choices=admYear))
        self.fields['admYear'] = admYearBox
        self.fields['aYear'] = aYearBox 
        self.fields['mYear'] = mYearBox 
        self.fields['regulation'] = forms.CharField(label='Regulation Code',min_length=1)


class GradePointsUploadForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(GradePointsUploadForm, self).__init__(*args, **kwargs)
        regulation = MTRegulation.objects.all()
        regulation = [(row.Regulation, row.Regulation) for row in regulation]
        regulation = list(set(regulation))
        reguChoices = [('-- Select Regulation --','-- Select Regulation --')] +regulation
        self.fields['Regulation'] = forms.CharField(label='Regulation', widget = forms.Select(choices=reguChoices))
        self.fields['file'] =forms.FileField(label='upload grade points file',validators=[validate_file_extension])



class GradePointsStatusForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(GradePointsStatusForm, self).__init__(*args, **kwargs)
        regulation = MTRegulation.objects.all()
        regulation = [(row.Regulation, row.Regulation) for row in regulation]
        regulation = list(set(regulation))
        reguChoices = [('','-- Select Regulation --')] +regulation
        self.fields['Regulation'] = forms.CharField(label='Regulation', widget = forms.Select(choices=reguChoices))

class GradePointsUpdateForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(GradePointsUpdateForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + str(Options[fi][0])] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+str(Options[fi][0])].initial = False  
            self.checkFields.append(self['Check' + str(Options[fi][0])])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2], self['Check' + str(Options[fi][0])])) 

class HODAssignmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(HODAssignmentForm, self).__init__(*args, **kwargs)
        departments = MTDepartments.objects.all()
        DEPT_CHOICES = [('', '--------')]
        HOD_CHOICES = [('', '--------')]
        USER_CHOICES = [('', '--------')]
        DEPT_CHOICES += [(dept.Dept, dept.Name) for dept in departments]
        self.fields['dept'] = forms.ChoiceField(label='Department', required=False, choices=DEPT_CHOICES, widget=forms.Select(attrs={'onchange':"submit()", 'required':'True'}))
        self.fields['hod'] = forms.ChoiceField(label='HOD', required=False, choices=HOD_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        self.fields['user'] = forms.ChoiceField(label='User', required=False, choices=USER_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        if self.data.get('dept'):
            faculty= MTFacultyInfo.objects.filter(Working=True, Dept=self.data.get('dept'))
            HOD_CHOICES += [(fac.id, fac.Name) for fac in faculty]
            self.fields['hod'] = forms.ChoiceField(label='HOD', required=False, choices=HOD_CHOICES, widget=forms.Select(attrs={'required':'True'}))
            group = Group.objects.filter(name='HOD').first()
            assigned_users = MTHOD.objects.filter(RevokeDate__isnull=True).exclude(Dept=self.data.get('dept'))
            users = group.user_set.exclude(id__in=assigned_users.values_list('User', flat=True))
            USER_CHOICES += [(user.id, user.username) for user in users]
            self.fields['user'] = forms.ChoiceField(label='User', required=False, choices=USER_CHOICES, widget=forms.Select(attrs={'required':'True'}))
            initial_hod = MTHOD.objects.filter(Dept=self.data.get('dept'), RevokeDate__isnull=True).first()
            if initial_hod:
                self.fields['hod'].initial = initial_hod.Faculty.id
                self.fields['user'].initial = initial_hod.User.id


class MarksDistributionForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(MarksDistributionForm, self).__init__(*args, **kwargs)
        self.fields['Distribution'] = forms.CharField(label='Distribution', widget=forms.Textarea(attrs={'rows':10, 'cols':10}))
        self.fields['DistributionName'] = forms.CharField(label='DistributionName', widget=forms.Textarea(attrs={'rows':10, 'cols':10}))



class StudentCancellationForm(forms.Form):
    def __init__ (self,*args, **kwargs):
        super(StudentCancellationForm, self).__init__(*args, **kwargs)
        self.fields['RegNo'] = forms.CharField(label='Registration Number',max_length=7,min_length=2)
        self.fields['Date'] = forms.DateField(label='Cancelled Date')
    
    def clean_RegNo(self):
        regd_no = self.cleaned_data.get('RegNo')
        if not MTStudentInfo.objects.filter(RegNo=regd_no).exists():
            raise forms.ValidationError('Invalid Reg No.')
        return regd_no

class HeldInForm(forms.Form):
    def __init__ (self,*args, **kwargs):
        super(HeldInForm, self).__init__(*args, **kwargs)
        regEvents = MTRegistrationStatus.objects.filter(Status=1, Mode='R')
        AYASMYMS_CHOICES = [('', '---------')] + [(((((((reg.AYear*10)+reg.ASem)*10)+reg.MYear)*10)+reg.MSem), ((((((reg.AYear*10)+reg.ASem)*10)+reg.MYear)*10)+reg.MSem))for reg in regEvents]
        self.fields['ayasmyms'] = forms.ChoiceField(label='AYASMYMS', required=False, choices=AYASMYMS_CHOICES, widget=forms.Select(attrs={'required':'True', 'onchange':'submit()'}))
        MONTH_CHOICES = [('', '---------')]
        self.fields['held_in_month'] = forms.ChoiceField(label='Held In Month', choices=MONTH_CHOICES, required=False, widget=forms.Select(attrs={'required':'True'}))
        YEAR_CHOICES = [('', '--------')]
        self.fields['held_in_year'] = forms.ChoiceField(label='Held In Year', required=False, choices=YEAR_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        if self.data.get('ayasmyms'):
            import calendar
            months_list = list(calendar.month_name)
            months_list.pop(0)
            MONTH_CHOICES += [(month,month) for month in months_list]
            self.fields['held_in_month'] = forms.ChoiceField(label='Held In Month', choices=MONTH_CHOICES, required=False, widget=forms.Select(attrs={'required':'True'}))
            YEAR_CHOICES += [(i,i) for i in range(int(self.data.get('ayasmyms')[:4]),datetime.datetime.now().year+1)]
            self.fields['held_in_year'] = forms.ChoiceField(label='Held In Year', required=False, choices=YEAR_CHOICES, widget=forms.Select(attrs={'required':'True'}))

