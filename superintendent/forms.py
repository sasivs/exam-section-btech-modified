from django import forms
from django.contrib.auth.models import Group
from superintendent.models import HOD
from SupExamDBRegistrations.models import FacultyInfo
from superintendent.models import ProgrammeModel, Departments, Regulation, RegistrationStatus
from co_ordinator.models import StudentBacklogs
import datetime



class AddRegulationForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(AddRegulationForm, self).__init__(*args, **kwargs)
        admYear = [(0,'--Select AdmYear')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        aYearChoices = [(0,'--Select AYear')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        bYearChoices = [(0,'--Select BYear--'),(1,1), (2, 2),(3, 3),(4, 4)]
        aYearBox = forms.IntegerField(label='Select AYear', widget=forms.Select(choices=aYearChoices))
        bYearBox = forms.IntegerField(label='Select BYear', widget=forms.Select(choices=bYearChoices))
        admYearBox = forms.IntegerField(label='Select AdmYear', widget=forms.Select(choices=admYear))
        self.fields['admYear'] = admYearBox
        self.fields['aYear'] = aYearBox 
        self.fields['bYear'] = bYearBox 
        self.fields['regulation'] = forms.CharField(label='Regulation Code',min_length=1)


class DBYBSAYASSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DBYBSAYASSelectionForm, self).__init__(*args, **kwargs)
        departments = ProgrammeModel.objects.filter(ProgrammeType='UG')
        deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        deptChoices = [(0,'--Select Dept--')] + deptChoices
        bYearChoices = [(0,'--Select BYear--'),(1,1), (2, 2),(3, 3),(4, 4)]
        bSemChoices = [(0,'--Select BSem--'),(1,1),(2,2)]
        aYearChoices = [(0,'--Select AYear--')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        aSemChoices = [(0,'--Select ASem--')] + [(1,1),(2,2),(3,3)]
        aYearBox = forms.IntegerField(label='Select AYear', widget=forms.Select(choices=aYearChoices,attrs={'onchange':'submit();'}))
        aSemBox = forms.IntegerField(label='Select ASem', widget=forms.Select(choices=aSemChoices))
        bYearBox = forms.IntegerField(label='Select BYear', widget=forms.Select(choices=bYearChoices,attrs={'onchange':'submit();'}))
        bSemBox = forms.IntegerField(label='Select BSem', widget=forms.Select(choices=bSemChoices))
        deptBox = forms.CharField(label='Select Department', widget=forms.Select(choices=deptChoices))
        rChoices = [(0,'--Select Regulation--')]
        statusBox = forms.ChoiceField(label='Enable/Disable', widget=forms.RadioSelect(), choices=[(0, 'Disable'), (1, 'Enable')])
        modeBox = forms.ChoiceField(label='Select Mode',widget=forms.RadioSelect(),choices = [('R', 'Regular'),('B','Backlog'),('D','DroppedRegular'),('M','Makeup')])
        regulationBox = forms.IntegerField(label='Select Regulation', widget=forms.Select(choices=rChoices))
        self.fields['aYear'] = aYearBox
        self.fields['aSem'] = aSemBox
        self.fields['bYear'] = bYearBox
        self.fields['bSem'] = bSemBox
        self.fields['dept'] = deptBox
        self.fields['regulation'] = regulationBox
        self.fields['status'] = statusBox
        self.fields['mode'] = modeBox
        if 'aYear' in self.data and 'bYear' in self.data and self.data['aYear']!='' and \
            self.data['bYear']!='' and self.data['aYear']!='0' and \
            self.data['bYear']!='0':
            regulations = Regulation.objects.filter(AYear=self.data.get('aYear')).filter(BYear = self.data.get('bYear'))
            dropped_course_regulations = Regulation.objects.filter(AYear=str(int(self.data.get('aYear'))-1),BYear=self.data.get('bYear'))
            backlog_course_regulations = StudentBacklogs.objects.filter(BYear=self.data.get('bYear'))
            backlog_course_regulations = [(regu.Regulation,regu.Regulation) for regu in backlog_course_regulations]
            dropped_course_regulations = [(regu.Regulation,regu.Regulation) for regu in dropped_course_regulations]
            regulations = [(regu.Regulation,regu.Regulation) for regu in regulations]
            regulations +=  dropped_course_regulations + backlog_course_regulations
            regulations = list(set(regulations))
            rChoices += regulations
            self.fields['regulation'] = forms.IntegerField(label='Select Regulation', widget=forms.Select(choices=rChoices))
        

class GradePointsUploadForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(GradePointsUploadForm, self).__init__(*args, **kwargs)
        regulation = Regulation.objects.all()
        regulation = [(row.Regulation, row.Regulation) for row in regulation]
        regulation = list(set(regulation))
        reguChoices = [('-- Select Regulation --','-- Select Regulation --')] +regulation
        self.fields['Regulation'] = forms.CharField(label='Regulation', widget = forms.Select(choices=reguChoices))
        self.fields['file'] =forms.FileField(label='upload grade points file')

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


class MandatoryCreditsForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(MandatoryCreditsForm, self).__init__(*args, **kwargs)
        regulation = Regulation.objects.all()
        regulation = [(row.Regulation, row.Regulation) for row in regulation]
        regulation = list(set(regulation))
        reguChoices = [('-- Select Regulation --','-- Select Regulation --')] +regulation
        departments = ProgrammeModel.objects.filter(ProgrammeType='UG')
        deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        deptChoices = [('--Select Dept--','--Select Dept--')] + deptChoices
        bYearChoices = [('--Select Dept--','--Select BYear--'),(1,1), (2, 2),(3, 3),(4, 4)]
        self.fields['Regulation'] = forms.CharField(label='Regulation', widget = forms.Select(choices=reguChoices))
        self.fields['BYear'] = forms.CharField(label='BYear', widget = forms.Select(choices=bYearChoices))
        self.fields['Dept'] = forms.CharField(label='Deptatment', widget = forms.Select(choices=deptChoices))
        self.fields['Credits'] = forms.CharField(label='Credits',max_length= 6)

class HODAssignmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(HODAssignmentForm, self).__init__(*args, **kwargs)
        departments = Departments.objects.filter(ProgrammeName='BTech', ProgrammeType='UG')
        DEPT_CHOICES = [('', '--------')]
        HOD_CHOICES = [('', '--------')]
        USER_CHOICES = [('', '--------')]
        DEPT_CHOICES += [(dept.Dept, dept.Specilaization) for dept in departments.values_list('Dept', flat=True)]
        self.fields['dept'] = forms.CharField(label='Department', widget=forms.Select(choices=DEPT_CHOICES, attrs={'onchange':"submit()"}))
        self.fields['hod'] = forms.CharField(label='HOD', widget=forms.Select(choices=HOD_CHOICES))
        self.fields['user'] = forms.CharField(label='User', widget=forms.Select(choices=USER_CHOICES))
        if self.data.get('dept'):
            faculty= FacultyInfo.objects.filter(working=True, Dept=self.data.get('dept'))
            HOD_CHOICES += [(fac.id, fac.Name) for fac in faculty]
            self.fields['hod'] = forms.CharField(label='HOD', widget=forms.Select(choices=HOD_CHOICES))
            group = Group.objects.filter(name='HOD').first()
            assigned_users = HOD.objects.filter(RevokeDate__isnull=True).exclude(Dept=self.data.get('dept'))
            users = group.user_set.exclude(id__in=assigned_users.values_list('User', flat=True))
            self.fields['user'] = forms.CharField(label='User', widget=forms.Select(choices=USER_CHOICES))
            USER_CHOICES += [(user.id, user.username) for user in users]
            initial_hod = HOD.objects.filter(Dept=self.data.get('dept'), RevokeDate__isnull=True).first()
            if initial_hod:
                self.fields['hod'].initial = initial_hod.Faculty.id
                self.fields['user'].initial = initial_hod.User.id


class MarksDistributionForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(MarksDistributionForm, self).__init__(*args, **kwargs)
        self.fields['Distribution'] = forms.CharField(label='Distribution', widget=forms.Textarea(attrs={'rows':5, 'cols':10}))
        self.fields['DistributionName'] = forms.CharField(label='DistributionName', widget=forms.Textarea(attrs={'rows':5, 'cols':10}))


