from django import forms
from django.contrib.auth.models import Group
from django.db.models import Q
from MTsuperintendent.models import MTHOD
from MTExamStaffDB.models import MTFacultyInfo, MTStudentInfo
from MTsuperintendent.models import MTProgrammeModel, MTDepartments, MTRegulation
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


class CreateRegistrationEventForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CreateRegistrationEventForm, self).__init__(*args, **kwargs)
        departments = MTProgrammeModel.objects.filter(ProgrammeType='PG')
        deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        deptChoices += [('all', 'All Departments')]
        deptChoices = [('','--Select Dept--')] + deptChoices
        mYearChoices = [('','--Select MYear--'),(1,1), (2, 2)]
        mSemChoices = [('','--Select MSem--'),(1,1),(2,2)]
        aYearChoices = [('','--Select AYear--')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        aSemChoices = [('','--Select ASem--')] + [(1,1),(2,2),(3,3)]
        aYearBox = forms.IntegerField(label='Select AYear', required=False, widget=forms.Select(choices=aYearChoices,attrs={'onchange':'submit();', 'required':'True'}))
        aSemBox = forms.IntegerField(label='Select ASem', required=False, widget=forms.Select(choices=aSemChoices, attrs={'required':'True'}))
        mYearBox = forms.IntegerField(label='Select MYear', required=False, widget=forms.Select(choices=mYearChoices,attrs={'onchange':'submit();', 'required':'True'}))
        mSemBox = forms.IntegerField(label='Select MSem', required=False, widget=forms.Select(choices=mSemChoices, attrs={'required':'True'}))
        deptBox = forms.CharField(label='Select Department', required=False, widget=forms.Select(choices=deptChoices, attrs={'required':'True'}))
        rChoices = [('','--Select Regulation--')]
        regulationBox = forms.IntegerField(label='Select Regulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))
        modeBox = forms.ChoiceField(label='Select Mode', required=False, widget=forms.RadioSelect(attrs={'required':'True'}),choices = [('R', 'Regular'),('B','Backlog'),('M','Makeup')])
        self.fields['aYear'] = aYearBox
        self.fields['aSem'] = aSemBox
        self.fields['mYear'] = mYearBox
        self.fields['mSem'] = mSemBox
        self.fields['dept'] = deptBox
        self.fields['regulation'] = regulationBox
        self.fields['mode'] = modeBox
        if self.data.get('aYear') and self.data.get('mYear'):
            regulations = MTRegulation.objects.filter(AYear=self.data.get('aYear')).filter(MYear = self.data.get('mYear'))
            backlog_course_regulations = MTStudentBacklogs.objects.filter(MYear=self.data.get('mYear'))
            backlog_course_regulations = [(regu.Regulation,regu.Regulation) for regu in backlog_course_regulations]
            regulations = [(regu.Regulation,regu.Regulation) for regu in regulations]
            regulations += backlog_course_regulations
            regulations = list(set(regulations))
            rChoices += regulations
            self.fields['regulation'] = forms.IntegerField(label='Select Regulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))



class DMYMSAYASSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DMYMSAYASSelectionForm, self).__init__(*args, **kwargs)
        departments = MTProgrammeModel.objects.filter(ProgrammeType='PG')
        deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        deptChoices = [(0,'--Select Dept--')] + deptChoices
        mYearChoices = [(0,'--Select MYear--'),(1,1), (2, 2)]
        mSemChoices = [(0,'--Select MSem--'),(1,1),(2,2)]
        aYearChoices = [(0,'--Select AYear--')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        aSemChoices = [(0,'--Select ASem--')] + [(1,1),(2,2),(3,3)]
        aYearBox = forms.IntegerField(label='Select AYear', required=False, widget=forms.Select(choices=aYearChoices,attrs={'onchange':'submit();', 'required':'True'}))
        aSemBox = forms.IntegerField(label='Select ASem', required=False, widget=forms.Select(choices=aSemChoices))
        mYearBox = forms.IntegerField(label='Select MYear', required=False, widget=forms.Select(choices=mYearChoices,attrs={'onchange':'submit();', 'required':'True'}))
        mSemBox = forms.IntegerField(label='Select MSem', required=False, widget=forms.Select(choices=mSemChoices, attrs={'required':'True'}))
        deptBox = forms.CharField(label='Select Department', required=False, widget=forms.Select(choices=deptChoices, attrs={'required':'True'}))
        rChoices = [(0,'--Select Regulation--')]
        statusBox = forms.ChoiceField(label='Enable/Disable', required=False, widget=forms.RadioSelect(), choices=[(0, 'Disable'), (1, 'Enable')])
        rollBox = forms.ChoiceField(label='RollList Status', required=False, widget=forms.RadioSelect(), choices=[(0, 'Disable'), (1, 'Enable')])
        regBox = forms.ChoiceField(label='Registration Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        marksBox = forms.ChoiceField(label='Marks Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        gradesBox = forms.ChoiceField(label='Grades Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        modeBox = forms.ChoiceField(label='Regular/Backlog', required=False, widget=forms.RadioSelect(attrs={'required':'True'}),choices = [('R', 'Regular'),('B','Backlog'),('M','Makeup')] )
        regulationBox = forms.IntegerField(label='Select Regulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))
        self.fields['aYear'] = aYearBox
        self.fields['aSem'] = aSemBox
        self.fields['mYear'] = mYearBox
        self.fields['mSem'] = mSemBox
        self.fields['dept'] = deptBox
        self.fields['regulation'] = regulationBox
        self.fields['status'] = statusBox
        self.fields['roll-status'] = rollBox
        self.fields['reg-status'] = regBox
        self.fields['marks-status'] = marksBox
        self.fields['grades-status'] = gradesBox
        self.fields['mode'] = modeBox
        if 'aYear' in self.data and 'mYear' in self.data and self.data['aYear']!='' and \
            self.data['mYear']!='' and self.data['aYear']!='0' and \
            self.data['mYear']!='0':
            regulations = MTRegulation.objects.filter(AYear=self.data.get('aYear')).filter(MYear = self.data.get('mYear'))
            backlog_course_regulations = MTStudentBacklogs.objects.filter(MYear=self.data.get('mYear'))
            backlog_course_regulations = [(regu.Regulation,regu.Regulation) for regu in backlog_course_regulations]
            regulations = [(regu.Regulation,regu.Regulation) for regu in regulations]
            regulations += backlog_course_regulations
            regulations = list(set(regulations))
            rChoices += regulations
            self.fields['regulation'] = forms.IntegerField(label='Select MTRegulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))


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
    
    def clean_RegNo(self):
        regd_no = self.cleaned_data.get('RegNo')
        if not MTStudentInfo.objects.filter(RegNo=regd_no).exists():
            raise forms.ValidationError('Invalid Reg No.')
        return regd_no

