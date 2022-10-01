from django import forms
from django.contrib.auth.models import Group
from django.db.models import Q
from ADUGDB.models import BTRegistrationStatus
from BTsuperintendent.models import BTHOD, BTCancelledStudentInfo, BTCycleCoordinator
from BTExamStaffDB.models import BTFacultyInfo, BTStudentInfo
from BTsuperintendent.models import BTProgrammeModel, BTDepartments, BTRegulation
from BTco_ordinator.models import BTSubjects
from BTsuperintendent.validators import validate_file_extension
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


class GradePointsUploadForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(GradePointsUploadForm, self).__init__(*args, **kwargs)
        regulation = BTRegulation.objects.all()
        regulation = [(row.Regulation, row.Regulation) for row in regulation]
        regulation = list(set(regulation))
        reguChoices = [('-- Select Regulation --','-- Select Regulation --')] +regulation
        self.fields['Regulation'] = forms.CharField(label='Regulation', widget = forms.Select(choices=reguChoices))
        self.fields['file'] =forms.FileField(label='upload grade points file', validators=[validate_file_extension])

class GradePointsStatusForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(GradePointsStatusForm, self).__init__(*args, **kwargs)
        regulation = BTRegulation.objects.all()
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
        departments = BTProgrammeModel.objects.filter(ProgrammeType='UG').filter(Q(Dept__lte=8) & Q(Dept__gte=1))
        deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        deptChoices = [(0,'--Select Dept--')] + deptChoices
        self.fields['CurrentDept'] = forms.CharField(label='CurrentDept',widget=forms.Select(choices=deptChoices))
        aYearChoices = [(0,'--Select AYear')] + [(i,i) for i in range(2016,datetime.datetime.now().year+1)]
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
        departments = BTDepartments.objects.all()
        DEPT_CHOICES = [('', '--------')]
        HOD_CHOICES = [('', '--------')]
        USER_CHOICES = [('', '--------')]
        DEPT_CHOICES += [(dept.Dept, dept.Name) for dept in departments]
        self.fields['dept'] = forms.ChoiceField(label='Department', required=False, choices=DEPT_CHOICES, widget=forms.Select(attrs={'onchange':"submit()", 'required':'True'}))
        self.fields['hod'] = forms.ChoiceField(label='HOD', required=False, choices=HOD_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        self.fields['user'] = forms.ChoiceField(label='User', required=False, choices=USER_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        if self.data.get('dept'):
            faculty= BTFacultyInfo.objects.filter(Working=True, Dept=self.data.get('dept'))
            HOD_CHOICES += [(fac.id, fac.Name) for fac in faculty]
            self.fields['hod'] = forms.ChoiceField(label='HOD', required=False, choices=HOD_CHOICES, widget=forms.Select(attrs={'required':'True'}))
            group = Group.objects.filter(name='HOD').first()
            assigned_users = BTHOD.objects.filter(RevokeDate__isnull=True).exclude(Dept=self.data.get('dept'))
            users = group.user_set.exclude(id__in=assigned_users.values_list('User', flat=True))
            USER_CHOICES += [(user.id, user.username) for user in users]
            self.fields['user'] = forms.ChoiceField(label='User', required=False, choices=USER_CHOICES, widget=forms.Select(attrs={'required':'True'}))
            initial_hod = BTHOD.objects.filter(Dept=self.data.get('dept'), RevokeDate__isnull=True).first()
            if initial_hod:
                self.fields['hod'].initial = initial_hod.Faculty.id
                self.fields['user'].initial = initial_hod.User.id

class CycleCoordinatorAssignmentForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(CycleCoordinatorAssignmentForm, self).__init__(*args, **kwargs)
        CYCLE_CHOICES =  [('', '--------'), (9, 'Chemistry'), (10,'Physics')]
        COORDINATOR_CHOICES = [('', '--------')]
        USER_CHOICES = [('', '--------')]
        self.fields['cycle'] = forms.ChoiceField(label='Cycle',  required=False, choices=CYCLE_CHOICES, widget=forms.Select(attrs={'required':'True', 'onchange':"submit();"}))
        self.fields['coordinator'] = forms.ChoiceField(label='Coordinator',  required=False, choices=COORDINATOR_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        self.fields['user'] = forms.ChoiceField(label='User',  required=False, choices=USER_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        if self.data.get('cycle'):
            assigned_faculty = BTCycleCoordinator.objects.filter(RevokeDate__isnull=True).exclude(Cycle=self.data.get('cycle'))
            faculty= BTFacultyInfo.objects.filter(Working=True).exclude(id__in=assigned_faculty.values_list('Faculty_id', flat=True)) #here1
            COORDINATOR_CHOICES += [(fac.id, fac.Name) for fac in faculty]
            group = Group.objects.filter(name='Cycle-Co-ordinator').first()
            assigned_users = BTCycleCoordinator.objects.filter(RevokeDate__isnull=True).exclude(Cycle=self.data.get('cycle'))
            users = group.user_set.exclude(id__in=assigned_users.values_list('User', flat=True))
            USER_CHOICES += [(user.id, user.username) for user in users]
            self.fields['coordinator'] = forms.ChoiceField(label='Coordinator', required=False, choices=COORDINATOR_CHOICES, widget=forms.Select(attrs={'required':'True'}))
            self.fields['user'] = forms.ChoiceField(label='User', required=False, choices=USER_CHOICES, widget=forms.Select(attrs={'required':'True'}))
            initial_cycle_cord = BTCycleCoordinator.objects.filter(Cycle=self.data.get('cycle'), RevokeDate__isnull=True).first()
            print('Here')
            if initial_cycle_cord:
                self.fields['coordinator'].initial = initial_cycle_cord.Faculty.id
                self.fields['user'].initial = initial_cycle_cord.User.id 


class MarksDistributionForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(MarksDistributionForm, self).__init__(*args, **kwargs)
        self.fields['Distribution'] = forms.CharField(label='Distribution', widget=forms.Textarea(attrs={'rows':10, 'cols':10}))
        self.fields['DistributionName'] = forms.CharField(label='DistributionName', widget=forms.Textarea(attrs={'rows':10, 'cols':10}))
        self.fields['PromoteThreshold'] = forms.CharField(label='Passing Thresholds', widget=forms.Textarea(attrs={'rows':10, 'cols':10}))
    
    def clean(self):
        cleaned_data = super().clean()
        distribution = cleaned_data.get('Distribution')
        distribution_name = cleaned_data.get('DistributionName')
        promote_threshold = cleaned_data.get('PromoteThreshold')
        distribution = distribution.split(',')
        distribution_name = distribution_name.split(',')
        promote_threshold = promote_threshold.split(',')
        distribution = [dis.split('+') for dis in distribution]
        distribution_name = [dis.split('+') for dis in distribution_name]
        promote_threshold = [dis.split('+') for dis in promote_threshold]
        if len(distribution) == len(distribution_name) and len(distribution) == len(promote_threshold):
            for index in range(len(distribution)):
                if (len(distribution[index]) != len(distribution_name[index])) or (len(distribution[index]) != len(promote_threshold[index])):
                    raise forms.ValidationError("All fields of distribution are not given in the strings.")
        else:
            raise forms.ValidationError("All fields of distribution are not given in the strings.")
        return cleaned_data


class StudentCancellationForm(forms.Form):
    def __init__ (self,*args, **kwargs):
        super(StudentCancellationForm, self).__init__(*args, **kwargs)
        self.fields['RegNo'] = forms.CharField(label='Registration Number',max_length=7,min_length=6)
        self.fields['Date'] = forms.DateField(label='Cancelled Date', widget=forms.DateInput(attrs={'type':'date'}))
        self.fields['remark'] = forms.CharField(label='Remarks', widget=forms.Textarea())
    
    def clean_RegNo(self):
        regd_no = self.cleaned_data.get('RegNo')
        if not BTStudentInfo.objects.filter(RegNo=regd_no).exists():
            raise forms.ValidationError('Invalid Reg No.')
        if BTCancelledStudentInfo.objects.filter(RegNo=regd_no).exists():
            cancelled_student = BTCancelledStudentInfo.objects.filter(RegNo=regd_no).first()
            raise forms.ValidationError("{}, {} seat is already cancelled.".format(cancelled_student.RegNo, cancelled_student.Name))
        return regd_no

class StudentCancellationStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StudentCancellationStatusForm, self).__init__(*args, **kwargs)
        AYEAR_CHOICES = [(0,'--Select AYear')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        self.fields['AYear'] = forms.CharField(label='Academic Year',\
            widget = forms.Select(choices=AYEAR_CHOICES, attrs={'onchange':'submit();'}))


class HeldInForm(forms.Form):
    def __init__ (self,*args, **kwargs):
        super(HeldInForm, self).__init__(*args, **kwargs)
        regEvents = BTRegistrationStatus.objects.filter(Status=1, Mode='R')
        AYASBYBS_CHOICES = [('', '---------')] + [(((((((reg.AYear*10)+reg.ASem)*10)+reg.BYear)*10)+reg.BSem), ((((((reg.AYear*10)+reg.ASem)*10)+reg.BYear)*10)+reg.BSem))for reg in regEvents]
        self.fields['ayasbybs'] = forms.ChoiceField(label='AYASBYBS', required=False, choices=AYASBYBS_CHOICES, widget=forms.Select(attrs={'required':'True', 'onchange':'submit()'}))
        MONTH_CHOICES = [('', '---------')]
        self.fields['held_in_month'] = forms.ChoiceField(label='Held In Month', choices=MONTH_CHOICES, required=False, widget=forms.Select(attrs={'required':'True'}))
        YEAR_CHOICES = [('', '--------')]
        self.fields['held_in_year'] = forms.ChoiceField(label='Held In Year', required=False, choices=YEAR_CHOICES, widget=forms.Select(attrs={'required':'True'}))
        if self.data.get('ayasbybs'):
            import calendar
            months_list = list(calendar.month_name)
            months_list.pop(0)
            MONTH_CHOICES += [(month,month) for month in months_list]
            self.fields['held_in_month'] = forms.ChoiceField(label='Held In Month', choices=MONTH_CHOICES, required=False, widget=forms.Select(attrs={'required':'True'}))
            YEAR_CHOICES += [(i,i) for i in range(int(self.data.get('ayasbybs')[:4]),datetime.datetime.now().year+1)]
            self.fields['held_in_year'] = forms.ChoiceField(label='Held In Year', required=False, choices=YEAR_CHOICES, widget=forms.Select(attrs={'required':'True'}))

class OpenElectiveRegistrationsFinalizeForm(forms.Form):
    def __init__(self, regIDs, *args, **kwargs):
        super(OpenElectiveRegistrationsFinalizeForm, self).__init__(*args, **kwargs)
        EVENT_CHOICES = [('', 'Choose Event')]
        if regIDs:
            EVENT_CHOICES += [(event.id, event.__str__)for event in regIDs]
        self.fields['regID'] = forms.CharField(label='Choose Registration Event', max_length=55, widget=forms.Select(choices=EVENT_CHOICES))
        if self.data.get('regID'):
            subjects = BTSubjects.objects.filter(RegEventId_id=self.data.get('regID'), Category__in=['OEC','OPC'])
            SUBJECT_CHOICES = [('', 'Choose Subject')]
            SUBJECT_CHOICES += [(sub.id, str(sub.SubCode)+', '+str(sub.SubName))for sub in subjects]
            self.fields['sub'] = forms.CharField(label='Subject', widget=forms.Select(choices=SUBJECT_CHOICES))