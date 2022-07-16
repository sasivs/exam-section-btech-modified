from django import forms
from django.contrib.auth.models import Group
from django.db.models import Q
from superintendent.models import HOD, CycleCoordinator
from ExamStaffDB.models import FacultyInfo
from superintendent.models import ProgrammeModel, Departments, Regulation
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
        aYearBox = forms.IntegerField(label='Select AYear', required=False, widget=forms.Select(choices=aYearChoices,attrs={'onchange':'submit();', 'required':'True'}))
        aSemBox = forms.IntegerField(label='Select ASem', required=False, widget=forms.Select(choices=aSemChoices, attrs={'required':'True'}))
        bYearBox = forms.IntegerField(label='Select BYear', required=False, widget=forms.Select(choices=bYearChoices,attrs={'onchange':'submit();', 'required':'True'}))
        bSemBox = forms.IntegerField(label='Select BSem', required=False, widget=forms.Select(choices=bSemChoices, attrs={'required':'True'}))
        deptBox = forms.CharField(label='Select Department', required=False, widget=forms.Select(choices=deptChoices, attrs={'required':'True'}))
        rChoices = [(0,'--Select Regulation--')]
        statusBox = forms.ChoiceField(label='Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        regBox = forms.ChoiceField(label='Registration Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        marksBox = forms.ChoiceField(label='Marks Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        gradesBox = forms.ChoiceField(label='Grades Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        modeBox = forms.ChoiceField(label='Select Mode', required=False, widget=forms.RadioSelect(attrs={'required':'True'}),choices = [('R', 'Regular'),('B','Backlog'),('D','DroppedRegular'),('M','Makeup')])
        regulationBox = forms.IntegerField(label='Select Regulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))
        self.fields['aYear'] = aYearBox
        self.fields['aSem'] = aSemBox
        self.fields['bYear'] = bYearBox
        self.fields['bSem'] = bSemBox
        self.fields['dept'] = deptBox
        self.fields['regulation'] = regulationBox
        self.fields['status'] = statusBox
        self.fields['reg-status'] = regBox
        self.fields['marks-status'] = marksBox
        self.fields['grades-status'] = gradesBox
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
            self.fields['regulation'] = forms.IntegerField(label='Select Regulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))
        

class GradePointsUploadForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(GradePointsUploadForm, self).__init__(*args, **kwargs)
        regulation = Regulation.objects.all()
        regulation = [(row.Regulation, row.Regulation) for row in regulation]
        regulation = list(set(regulation))
        reguChoices = [('-- Select Regulation --','-- Select Regulation --')] +regulation
        self.fields['Regulation'] = forms.CharField(label='Regulation', widget = forms.Select(choices=reguChoices))
        self.fields['file'] =forms.FileField(label='upload grade points file')

class GradePointsStatusForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(GradePointsStatusForm, self).__init__(*args, **kwargs)
        regulation = Regulation.objects.all()
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



class BranchChangeForm(forms.Form):
    def __init__(self,  *args,**kwargs):
        super(BranchChangeForm, self).__init__(*args, **kwargs)
        self.fields['RegNo'] = forms.CharField(label='Registration Number',max_length=7,min_length=6)
        departments = ProgrammeModel.objects.filter(ProgrammeType='UG').filter(Q(Dept__lte=8) & Q(Dept__gte=1))
        deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        deptChoices = [(0,'--Select Dept--')] + deptChoices
        self.fields['CurrentDept'] = forms.CharField(label='CurrentDept',widget=forms.Select(choices=deptChoices))
        aYearChoices = [(0,'--Select AYear')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        self.fields['AYear'] = forms.CharField(label='AYear',widget = forms.Select(choices=aYearChoices))
        self.fields['NewDept'] = forms.CharField(label='NewDept',widget = forms.Select(choices=deptChoices))

class BranchChangeStausForm(forms.Form):
    def __init__(self,  *args,**kwargs):
        super(BranchChangeStausForm, self).__init__(*args, **kwargs)
        self.aYearChoices = [(0,'--Select AYear')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        self.fields['AYear'] = forms.CharField(label='AYear',\
            widget = forms.Select(choices=self.aYearChoices, attrs={'onchange':'submit();'}))


class HODAssignmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(HODAssignmentForm, self).__init__(*args, **kwargs)
        departments = Departments.objects.all()
        DEPT_CHOICES = [('', '--------')]
        HOD_CHOICES = [('', '--------')]
        USER_CHOICES = [('', '--------')]
        DEPT_CHOICES += [(dept.Dept, dept.Name) for dept in departments]
        self.fields['dept'] = forms.ChoiceField(label='Department', required=False, choices=DEPT_CHOICES, widget=forms.Select(attrs={'onchange':"submit()", 'required':'True'}))
        self.fields['hod'] = forms.ChoiceField(label='HOD', required=False, choices=HOD_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        self.fields['user'] = forms.ChoiceField(label='User', required=False, choices=USER_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        if self.data.get('dept'):
            faculty= FacultyInfo.objects.filter(Working=True, Dept=self.data.get('dept'))
            HOD_CHOICES += [(fac.id, fac.Name) for fac in faculty]
            self.fields['hod'] = forms.ChoiceField(label='HOD', required=False, choices=HOD_CHOICES, widget=forms.Select(attrs={'required':'True'}))
            group = Group.objects.filter(name='HOD').first()
            assigned_users = HOD.objects.filter(RevokeDate__isnull=True).exclude(Dept=self.data.get('dept'))
            users = group.user_set.exclude(id__in=assigned_users.values_list('User', flat=True))
            USER_CHOICES += [(user.id, user.username) for user in users]
            self.fields['user'] = forms.ChoiceField(label='User', required=False, choices=USER_CHOICES, widget=forms.Select(attrs={'required':'True'}))
            initial_hod = HOD.objects.filter(Dept=self.data.get('dept'), RevokeDate__isnull=True).first()
            if initial_hod:
                self.fields['hod'].initial = initial_hod.Faculty.id
                self.fields['user'].initial = initial_hod.User.id

class CycleCoordinatorAssignmentForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(CycleCoordinatorAssignmentForm, self).__init__(*args, **kwargs)
        CYCLE_CHOICES =  [('', '--------'), (9, 'Chemistry'), (10,'Physics')]
        COORDINATOR_CHOICES = [('', '--------')]
        USER_CHOICES = [('', '--------')]
        self.fields['cycle'] = forms.CharField(label='Cycle',  required=False, widget=forms.Select(choices=CYCLE_CHOICES, attrs={'required':'True', 'onchange':"submit();"}))
        self.fields['coordinator'] = forms.CharField(label='Coordinator',  required=False, widget=forms.Select(choices=COORDINATOR_CHOICES,  attrs={'required':'True'}))
        self.fields['user'] = forms.CharField(label='User',  required=False, widget=forms.Select(choices=USER_CHOICES,  attrs={'required':'True'}))
        if self.data.get('cycle'):
            assigned_faculty = CycleCoordinator.objects.filter(RevokeDate__isnull=True).exclude(Cycle=self.data.get('cycle'))
            faculty= FacultyInfo.objects.filter(Working=True).exclude(id__in=assigned_faculty.values_list('Faculty_id', flat=True)) #here1
            COORDINATOR_CHOICES += [(fac.id, fac.Name) for fac in faculty]
            group = Group.objects.filter(name='Cycle-Co-ordinator').first()
            assigned_users = CycleCoordinator.objects.filter(RevokeDate__isnull=True).exclude(Cycle=self.data.get('cycle'))
            users = group.user_set.exclude(id__in=assigned_users.values_list('User', flat=True))
            USER_CHOICES += [(user.id, user.username) for user in users]
            self.fields['coordinator'] = forms.CharField(label='Coordinator',  required=False, widget=forms.Select(choices=COORDINATOR_CHOICES,  attrs={'required':'True'}))
            self.fields['user'] = forms.CharField(label='User',  required=False, widget=forms.Select(choices=USER_CHOICES,  attrs={'required':'True'}))
        # if self.data.get('cycle'):
        #     cycle_cord = CycleCoordinator.objects.filter(Cycle=self.data.get('cycle'), RevokeDate__isnull=True)


class MarksDistributionForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(MarksDistributionForm, self).__init__(*args, **kwargs)
        self.fields['Distribution'] = forms.CharField(label='Distribution', widget=forms.Textarea(attrs={'rows':10, 'cols':10}))
        self.fields['DistributionName'] = forms.CharField(label='DistributionName', widget=forms.Textarea(attrs={'rows':10, 'cols':10}))


class StudentCancellationForm(forms.Form):
    def __init__ (self,*args, **kwargs):
        super(StudentCancellationForm, self).__init__(*args, **kwargs)
        self.fields['RegNo'] = forms.CharField(label='Registration Number',max_length=7,min_length=6)