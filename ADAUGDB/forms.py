from django import forms
from ADAUGDB.models import BTRegistrationStatus
from ADAUGDB.models import BTProgrammeModel,BTRegulation
from BTco_ordinator.models import BTNotPromoted, BTStudentBacklogs, BTSubjects, BTStudentRegistrations
from BTfaculty.models import BTMarks_Staging
from django.db.models import Q
import datetime
from django import forms
from django.contrib.auth.models import Group
from django.db.models import Q
from ADAUGDB.models import BTRegistrationStatus
from ADAUGDB.models import BTHOD, BTCancelledStudentInfo, BTCourseStructure, BTCycleCoordinator,BTCourses
from BTExamStaffDB.models import BTFacultyInfo, BTStudentInfo
from ADAUGDB.models import BTProgrammeModel, BTDepartments, BTRegulation
from BTco_ordinator.models import BTSubjects
from ADAUGDB.constants import DEPARTMENTS, YEARS, SEMS
from ADAUGDB.validators import validate_file_extension
import datetime

class DBYBSAYASSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DBYBSAYASSelectionForm, self).__init__(*args, **kwargs)
        # departments = BTProgrammeModel.objects.filter(ProgrammeType='UG')
        # deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        deptChoices = [(0,'--Select Dept--')] 
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
        rollBox = forms.ChoiceField(label='RollList Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        regBox = forms.ChoiceField(label='Registration Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        marksBox = forms.ChoiceField(label='Marks Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        gradesBox = forms.ChoiceField(label='Grades Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        modeBox = forms.ChoiceField(label='Select Mode', required=False, widget=forms.RadioSelect(attrs={'required':'True'}),choices = [('R', 'Regular'),('B','Backlog'),('D','DroppedRegular'),('M','Makeup')])
        regulationBox = forms.FloatField(label='Select Regulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))
        self.fields['aYear'] = aYearBox
        self.fields['aSem'] = aSemBox
        self.fields['bYear'] = bYearBox
        self.fields['bSem'] = bSemBox
        self.fields['dept'] = deptBox
        self.fields['regulation'] = regulationBox
        self.fields['status'] = statusBox
        self.fields['roll-status'] = rollBox
        self.fields['reg-status'] = regBox
        self.fields['marks-status'] = marksBox
        self.fields['grades-status'] = gradesBox
        self.fields['oerolls-status'] = forms.ChoiceField(label='OE Rolllist Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        self.fields['oeregs-status'] = forms.ChoiceField(label='OE Registrations Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        self.fields['mode'] = modeBox
        if 'aYear' in self.data and 'bYear' in self.data and self.data['aYear']!='' and \
            self.data['bYear']!='' and self.data['aYear']!='0' and \
            self.data['bYear']!='0':
            regulations = BTRegulation.objects.filter(AYear=self.data.get('aYear')).filter(BYear = self.data.get('bYear')).order_by('Regulation')
            dropped_course_regulations = BTRegulation.objects.filter(AYear=str(int(self.data.get('aYear'))-1),BYear=self.data.get('bYear'))
            backlog_course_regulations = BTStudentBacklogs.objects.filter(BYear=self.data.get('bYear'))
            backlog_course_regulations = [(regu.Regulation,regu.Regulation) for regu in backlog_course_regulations]
            dropped_course_regulations = [(regu.Regulation,regu.Regulation) for regu in dropped_course_regulations]
            regulations = [(regu.Regulation,regu.Regulation) for regu in regulations]
            regulations +=  dropped_course_regulations + backlog_course_regulations
            regulations = list(set(regulations))
            rChoices += regulations
            self.fields['regulation'] = forms.FloatField(label='Select Regulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))
            if self.data.get('bYear')!='1':
                departments = BTProgrammeModel.objects.filter(ProgrammeType='UG').exclude(Dept__in=[10,9])
            else:
                departments = BTProgrammeModel.objects.filter(ProgrammeType='UG',Dept__in=[10,9])
            deptChoices +=[(rec.Dept, rec.Specialization) for rec in departments ]
            deptBox = forms.CharField(label='Select Department', required=False, widget=forms.Select(choices=deptChoices, attrs={'required':'True'}))
            self.fields['dept'] = deptBox
        elif self.data.get('bYear'):
            if self.data.get('bYear') != '1':
                departments = BTProgrammeModel.objects.filter(ProgrammeType='UG').exclude(Dept__in=[10,9])
            else:
                departments = BTProgrammeModel.objects.filter(ProgrammeType='UG',Dept__in=[10,9])
            deptChoices +=[(rec.Dept, rec.Specialization) for rec in departments ]
            deptBox = forms.CharField(label='Select Department', required=False, widget=forms.Select(choices=deptChoices, attrs={'required':'True'}))
            self.fields['dept'] = deptBox



class CreateRegistrationEventForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CreateRegistrationEventForm, self).__init__(*args, **kwargs)
        deptChoices = [('','--Select Dept--')]
        bYearChoices = [('','--Select BYear--'),(1,1), (2, 2),(3, 3),(4, 4)]
        bSemChoices = [('','--Select BSem--'),(1,1),(2,2)]
        aYearChoices = [('','--Select AYear--')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        aSemChoices = [('','--Select ASem--')] + [(1,1),(2,2),(3,3)]
        aYearBox = forms.IntegerField(label='Select AYear', required=False, widget=forms.Select(choices=aYearChoices,attrs={'onchange':'submit();', 'required':'True'}))
        aSemBox = forms.IntegerField(label='Select ASem', required=False, widget=forms.Select(choices=aSemChoices, attrs={'required':'True'}))
        bYearBox = forms.IntegerField(label='Select BYear', required=False, widget=forms.Select(choices=bYearChoices,attrs={'onchange':'submit();', 'required':'True'}))
        bSemBox = forms.IntegerField(label='Select BSem', required=False, widget=forms.Select(choices=bSemChoices, attrs={'required':'True'}))
        deptBox = forms.CharField(label='Select Department', required=False, widget=forms.Select(choices=deptChoices, attrs={'required':'True'}))
        rChoices = [('','--Select Regulation--')]
        regulationBox = forms.FloatField(label='Select Regulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))
        modeBox = forms.ChoiceField(label='Select Mode', required=False, widget=forms.RadioSelect(attrs={'required':'True'}),choices = [('R', 'Regular'),('B','Backlog'),('D','DroppedRegular'),('M','Makeup')])
        self.fields['aYear'] = aYearBox
        self.fields['aSem'] = aSemBox
        self.fields['bYear'] = bYearBox
        self.fields['bSem'] = bSemBox
        self.fields['dept'] = deptBox
        self.fields['regulation'] = regulationBox
        self.fields['mode'] = modeBox
        if self.data.get('aYear') and self.data.get('bYear'):
            regulations = BTRegulation.objects.filter(AYear=self.data.get('aYear')).filter(BYear = self.data.get('bYear')).order_by('Regulation')
            dropped_course_regulations = BTRegulation.objects.filter(AYear=str(int(self.data.get('aYear'))-1),BYear=self.data.get('bYear'))
            backlog_course_regulations = BTStudentBacklogs.objects.filter(BYear=self.data.get('bYear'))
            backlog_course_regulations = [(regu.Regulation,regu.Regulation) for regu in backlog_course_regulations]
            dropped_course_regulations = [(regu.Regulation,regu.Regulation) for regu in dropped_course_regulations]
            regulations = [(regu.Regulation,regu.Regulation) for regu in regulations]
            regulations +=  dropped_course_regulations + backlog_course_regulations
            regulations = list(set(regulations))
            rChoices += regulations
            self.fields['regulation'] = forms.FloatField(label='Select Regulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))
            if self.data.get('bYear')!='1':
                departments = BTProgrammeModel.objects.filter(ProgrammeType='UG').exclude(Dept__in=[10,9])
            else:
                departments = BTProgrammeModel.objects.filter(ProgrammeType='UG',Dept__in=[10,9])
            deptChoices = [('','--Select Dept--')]
            deptChoices +=[(rec.Dept, rec.Specialization) for rec in departments ]
            deptChoices += [('all', 'All Departments')]
            deptBox = forms.CharField(label='Select Department', required=False, widget=forms.Select(choices=deptChoices, attrs={'required':'True'}))
            self.fields['dept'] = deptBox

        elif self.data.get('bYear'):
            if self.data.get('bYear') != '1':
                departments = BTProgrammeModel.objects.filter(ProgrammeType='UG').exclude(Dept__in=[10,9])
            else:
                departments = BTProgrammeModel.objects.filter(ProgrammeType='UG',Dept__in=[10,9])
            deptChoices = [('','--Select Dept--')]
            deptChoices +=[(rec.Dept, rec.Specialization) for rec in departments ]
            deptChoices += [('all', 'All Departments')]
            deptBox = forms.CharField(label='Select Department', required=False, widget=forms.Select(choices=deptChoices, attrs={'required':'True'}))
            self.fields['dept'] = deptBox
class RegulationChangeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(RegulationChangeForm, self).__init__(*args, **kwargs)
        events = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, ASem=1)
        REGEVENT_CHOICES = [('', 'Choose Event')]
        REGEVENT_CHOICES += [(event.id, event.__str__()) for event in events]
        REGNO_CHOICES = [('', 'Choose RegNo')]
        self.fields['regid'] = forms.CharField(label='Registration Event', required=False, widget = forms.Select(choices=REGEVENT_CHOICES, attrs={'onchange':"submit()", 'required':'True'}))
        self.fields['regno'] = forms.CharField(label='RegNo', required=False, widget = forms.Select(choices=REGNO_CHOICES))
        if self.data.get('regid'):
            event = events.filter(id=self.data.get('regid')).first()
            if event.BYear == 1:
                not_promoted_r_mode = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear, PoA_sem1='R', PoA_sem2='R').exclude(Regulation=event.Regulation)
                not_promoted_b_mode = BTNotPromoted.objects.filter(Q(PoA_sem1='B')|Q(PoA_sem2='B'), AYear=event.AYear-2, BYear=event.BYear-1).exclude(Regulation=event.Regulation)
            else:
                not_promoted_r_mode = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear, PoA_sem1='R', PoA_sem2='R', student__Dept=event.Dept).exclude(Regulation=event.Regulation)
                not_promoted_b_mode = BTNotPromoted.objects.filter(Q(PoA_sem1='B')|Q(PoA_sem2='B'), AYear=event.AYear-2, BYear=event.BYear-1, student__Dept=event.Dept).exclude(Regulation=event.Regulation)
            REGNO_CHOICES = [(row.id, row.student.RegNo) for row in not_promoted_r_mode|not_promoted_b_mode]
            REGNO_CHOICES = sorted(REGNO_CHOICES, key=lambda x:x[1])
            REGNO_CHOICES = [('', 'Choose RegNo')] + REGNO_CHOICES
            self.fields['regno'] = forms.CharField(label='RegNo', required=False, widget=forms.Select(choices=REGNO_CHOICES, attrs={'onchange':"submit()", 'required':'True'}))
            if self.data.get('regno'):
                self.fields['newRegulation'] = forms.CharField(label='New Regulation', required=False, widget=forms.TextInput(attrs={'type':'number', 'step':0.1, 'required':'True'}))

    def clean_newRegulation(self):
        if self.cleaned_data.get('newRegulation'):
            newRegulation = float(self.cleaned_data.get('newRegulation'))
            student_obj = BTNotPromoted.objects.filter(id=self.cleaned_data.get('regno')).first().student
            if student_obj.Regulation == newRegulation:
                raise forms.ValidationError('Updated regulation and old regulation cannot be same')
            return newRegulation
        return None


class CycleHandlerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CycleHandlerForm, self).__init__(*args, **kwargs)
        events = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, ASem=1, Mode='R')
        REGEVENT_CHOICES = [('', 'Choose Event')]
        REGEVENT_CHOICES += [(event.id, event.__str__()) for event in events]
        REGNO_CHOICES = [('', 'Choose RegNo')]
        self.fields['regid'] = forms.CharField(label='Registration Event', required=False, widget = forms.Select(choices=REGEVENT_CHOICES, attrs={'onchange':"submit()", 'required':'True'}))
        self.fields['regno'] = forms.CharField(label='RegNo', required=False, widget = forms.Select(choices=REGNO_CHOICES))
        if self.data.get('regid'):
            event = events.filter(id=self.data.get('regid')).first()
            if event.ASem == 1:
                not_promoted_r_mode = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear, PoA_sem1='R', student__Regulation=event.Regulation)
            else:
                not_promoted_r_mode = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear, PoA_sem2='R', student__Regulation=event.Regulation)
            REGNO_CHOICES = [(row.id, row.student.RegNo) for row in not_promoted_r_mode]
            REGNO_CHOICES = sorted(REGNO_CHOICES, key=lambda x:x[1])
            REGNO_CHOICES = [('', 'Choose RegNo')] + REGNO_CHOICES
            self.fields['regno'] = forms.CharField(label='RegNo', required=False, widget=forms.Select(choices=REGNO_CHOICES, attrs={'onchange':"submit()", 'required':'True'}))
            if self.data.get('regno'):
                CYCLE_CHOICES = [('', 'Choose Cycle')]
                CYCLE_CHOICES += [(9, 'Chemistry'), (10, 'Physics')]
                self.fields['cycle'] = forms.CharField(label='Cycle', required=False, widget=forms.Select(choices=CYCLE_CHOICES, attrs={'required':'True'}))

class RegulationChangeStatusForm(forms.Form):
    def __init__(self, regulation_change_objs, *args, **kwargs):
        super(RegulationChangeStatusForm, self).__init__(*args, **kwargs)
        YEAR_CHOICES = [(reg.RegEventId.AYear, reg.RegEventId.AYear) for reg in regulation_change_objs]
        YEAR_CHOICES = list(set(YEAR_CHOICES))
        YEAR_CHOICES = sorted(YEAR_CHOICES, key=lambda x:x[1])
        YEAR_CHOICES = [('', 'Choose Year')] + YEAR_CHOICES
        self.fields['ayear'] = forms.CharField(label='Academic Year', required=False, widget=forms.Select(choices=YEAR_CHOICES, attrs={'required':'true'}))




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


class CourseStructureForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CourseStructureForm, self).__init__(*args, **kwargs)
        regulations = BTRegulation.objects.all().distinct('Regulation')
        REGULATION_CHOICES = [('', 'Choose Regulation')]
        REGULATION_CHOICES += [(regulation.Regulation, regulation.Regulation)for regulation in regulations]
        self.fields['regulation'] = forms.CharField(label='Regulation', widget = forms.Select(choices=REGULATION_CHOICES))
        self.fields['file'] =forms.FileField(label='Course Structure', validators=[validate_file_extension])

class CourseStructureStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CourseStructureStatusForm, self).__init__(*args, **kwargs)
        regulations = BTRegulation.objects.all().distinct('Regulation')
        CHOICES = [('', 'Choose Event')]
        CHOICES += [(str(dept)+':'+str(year)+':'+str(sem)+':'+str(regulation.Regulation),str(DEPARTMENTS[dept-1])+':'+str(YEARS[year])+':'+str(SEMS[sem])+':'+str(regulation.Regulation))for regulation in regulations for dept in range(1,11) for year in range(1,5) for sem in range(1,3) if not((year==1 and dept<9)or(year>=2 and dept>=9))]
        self.fields['event'] = forms.CharField(label='Event', widget = forms.Select(choices=CHOICES))


class CourseStructureDeletionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CourseStructureDeletionForm, self).__init__(*args, **kwargs)
        regulations = BTRegulation.objects.all().distinct()
        CHOICES = [('', 'Choose Event')]
        CHOICES += [(str(dept)+':'+str(year)+':'+str(sem)+':'+str(regulation.Regulation),str(DEPARTMENTS[dept-1])+':'+str(YEARS[year])+':'+str(SEMS[sem])+':'+str(regulation.Regulation))for regulation in regulations for dept in range(1,11) for year in range(1,5) for sem in range(1,3) if not((year==1 and dept<9)or(year>=2 and dept>=9))]
        self.fields['event'] = forms.CharField(label='Event', widget = forms.Select(choices=CHOICES, attrs={'onchange':'submit();'}))
        self.eventBox = self['event']

        if self.data.get('event'):
            event = [int(x) for x in self.data.get('event').split(':')]
            course_structure = BTCourseStructure.objects.filter(Dept=event[0], BYear=event[1], BSem=event[2], Regulation=event[3]) 
            self.myFields = []
            for cs in course_structure:
                self.fields['Check'+str(cs.id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
                if self.data.get('Check'+str(cs.id)) == True:
                    self.fields['check'+str(cs.id)].initial = True
                self.myFields.append((cs.BYear, cs.BSem, cs.Dept, cs.Regulation, cs.Category, cs.Type, cs.Creditable, cs.Credits, self['Check'+str(cs.id)], cs.id))
            




class GradePointsUploadForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(GradePointsUploadForm, self).__init__(*args, **kwargs)
        regulation = BTRegulation.objects.all().order_by('Regulation')
        regulation = [(row.Regulation, row.Regulation) for row in regulation]
        regulation = list(set(regulation))
        reguChoices = [('-- Select Regulation --','-- Select Regulation --')] +regulation
        self.fields['Regulation'] = forms.CharField(label='Regulation', widget = forms.Select(choices=reguChoices))
        self.fields['file'] =forms.FileField(label='upload grade points file', validators=[validate_file_extension])

class GradePointsStatusForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(GradePointsStatusForm, self).__init__(*args, **kwargs)
        regulation = BTRegulation.objects.all().order_by('Regulation')
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
        regulations = BTRegulation.objects.all().distinct()
        REGULATION_CHOICES = [('', 'Choose Regulation')]
        REGULATION_CHOICES += [(regulation.Regulation, regulation.Regulation)for regulation in regulations]
        self.fields['Regulation'] = forms.FloatField(label='Select Regulation', widget=forms.Select(choices=REGULATION_CHOICES, attrs={'required':'True'}))
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
class OpenElectiveRegistrationsFinalizeForm(forms.Form):
    def __init__(self, regIDs, *args, **kwargs):
        super(OpenElectiveRegistrationsFinalizeForm, self).__init__(*args, **kwargs)
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = regIDs
        myChoices = [( 'OE'+':'+years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]),'OE'+':'+\
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices, attrs={'onchange': 'submit()'}))

            
class OpenElectiveRollListForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(OpenElectiveRollListForm, self).__init__(*args, **kwargs)
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = BTSubjects.objects.filter(RegEventId__Status=1, RegEventId__OERollListStatus=1, course__CourseStructure__Category__in=['OEC', 'OPC'])
        myChoices = [( years[option.RegEventId.BYear]+':'+ sems[option.RegEventId.BSem]+':'+ \
            str(option.RegEventId.AYear)+ ':'+str(option.RegEventId.BSem)+':'+str(option.RegEventId.Regulation), years[option.RegEventId.BYear]+':'+ sems[option.RegEventId.BSem]+':'+ \
            str(option.RegEventId.AYear)+ ':'+str(option.RegEventId.BSem)+':'+str(option.RegEventId.Regulation)) \
                    for oIndex, option in enumerate(self.regIDs.distinct('RegEventId'))]
        myChoices = [(option[0]+':'+mode, option[1]+':'+mode) for option in myChoices for mode in ['R', 'B']]
        myChoices = [('','Choose Event')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices, attrs={'onchange': 'submit()'}))
        if self.data.get('regID'):
            regid = self.data.get('regID')
            strs = regid.split(':')
            ayear = int(strs[3])
            asem = int(strs[4])
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = float(strs[5])
            # mode = strs[6]

            subjects = BTSubjects.objects.filter(RegEventId__AYear=ayear,RegEventId__ASem=asem,\
            RegEventId__BYear=byear,RegEventId__BSem=asem,RegEventId__Regulation=regulation,RegEventId__Mode='R',\
                RegEventId__Status=1, RegEventId__OERollListStatus=1, course__CourseStructure__Category__in=['OEC', 'OPC'])
            SUBJECT_CHOICES = [('', 'Choose Subject')]
            SUBJECT_CHOICES += [(sub.id, str(sub.course.SubCode)+', '+str(sub.course.SubName))for sub in subjects]
            self.fields['sub'] = forms.CharField(label='Subject', widget=forms.Select(choices=SUBJECT_CHOICES))
            self.fields['file'] =forms.FileField(label='OE RollList', validators=[validate_file_extension])

        
class OERollListStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(OERollListStatusForm, self).__init__(*args, **kwargs)
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = BTSubjects.objects.filter(RegEventId__Status=1, RegEventId__OERollListStatus=1, course__CourseStructure__Category__in=['OEC', 'OPC'])
        myChoices = [( 'OE'+':'+years[option.RegEventId.BYear]+':'+ sems[option.RegEventId.BSem]+':'+ \
            str(option.RegEventId.AYear)+ ':'+str(option.RegEventId.BSem)+':'+str(option.RegEventId.Regulation), 'OE'+':'+years[option.RegEventId.BYear]+':'+ sems[option.RegEventId.BSem]+':'+ \
            str(option.RegEventId.AYear)+ ':'+str(option.RegEventId.BSem)+':'+str(option.RegEventId.Regulation)) \
                    for oIndex, option in enumerate(self.regIDs.distinct('RegEventId'))]
        myChoices = [(option[0]+':'+mode, option[1]+':'+mode) for option in myChoices for mode in ['R', 'B']]
        myChoices = [('','Choose Event')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices, attrs={'onchange': 'submit()'}))
        if self.data.get('regID'):
            regid = self.data.get('regID')
            strs = regid.split(':')
            ayear = int(strs[3])
            asem = int(strs[4])
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = float(strs[5])
            mode = strs[6]

            subjects = BTSubjects.objects.filter(RegEventId__AYear=ayear,RegEventId__ASem=asem,\
            RegEventId__BYear=byear,RegEventId__BSem=asem,RegEventId__Regulation=regulation,RegEventId__Mode=mode,\
                RegEventId__Status=1, RegEventId__OERollListStatus=1, course__CourseStructure__Category__in=['OEC', 'OPC'])
            SUBJECT_CHOICES = [('', 'Choose Subject')]
            SUBJECT_CHOICES += [(sub.id, str(sub.course.SubCode)+', '+str(sub.course.SubName))for sub in subjects]
            self.fields['sub'] = forms.CharField(label='Subject', widget=forms.Select(choices=SUBJECT_CHOICES))
            
class AddCoursesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AddCoursesForm, self).__init__(*args, **kwargs)
        regulations = BTRegulation.objects.all().distinct('Regulation')
        REGULATION_CHOICES = [('', 'Choose Regulation')]
        REGULATION_CHOICES += [(regulation.Regulation, regulation.Regulation)for regulation in regulations]
        self.fields['Regulation'] = forms.FloatField(label='Select Regulation', required=False, widget=forms.Select(choices=REGULATION_CHOICES, attrs={'required':'True'}))
        BYEAR_CHOICES = [('', 'Choose BTech Year'), (1,1), (2,2), (3,3), (4,4)]
        self.fields['BYear'] = forms.IntegerField(label='Select BYear', required=False, widget=forms.Select(choices=BYEAR_CHOICES, attrs={'required':'True'}))
        self.fields['file'] = forms.FileField(validators=[validate_file_extension], required=False)

class CoursesStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CoursesStatusForm, self).__init__(*args, **kwargs)
        regulations = BTRegulation.objects.all().distinct('Regulation')
        REGULATION_CHOICES = [('', 'Choose Regulation')]
        REGULATION_CHOICES += [(regulation.Regulation, regulation.Regulation)for regulation in regulations]
        self.fields['Regulation'] = forms.FloatField(label='Select Regulation', widget=forms.Select(choices=REGULATION_CHOICES, attrs={'required':'True'}))
        BYEAR_CHOICES = [('', 'Choose BTech Year'), (1,1), (2,2), (3,3), (4,4)]
        self.fields['BYear'] = forms.IntegerField(label='Select BYear', widget=forms.Select(choices=BYEAR_CHOICES, attrs={'required':'True'}))

