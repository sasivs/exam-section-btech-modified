from django import forms 
from django.db.models import Q 
from co_ordinator.models import StudentRegistrations, StudentRegistrations_Staging
from hod.models import Coordinator
from superintendent.constants import DEPARTMENTS, YEARS, SEMS
from co_ordinator.models import FacultyAssignment, NotRegistered, Subjects_Staging, Subjects, StudentBacklogs, RollLists,\
    DroppedRegularCourses, StudentMakeups, RegularRegistrationSummary, BacklogRegistrationSummary, MakeupRegistrationSummary
from superintendent.models import CycleCoordinator, RegistrationStatus, ProgrammeModel
from ExamStaffDB.models import StudentInfo
from faculty.models import Marks_Staging
import datetime

#Create your forms here


class RegistrationsEventForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(RegistrationsEventForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+\
                 sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                     for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, \
            widget=forms.Select(choices=myChoices,attrs={'onchange':"submit();"}))

class SubjectsUploadForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(SubjectsUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField(required=False)
        self.fields['file'].widget.attrs.update({'required':'True'})
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        myChoices = [(oIndex, depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ \
            ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) for oIndex, option in enumerate(Options)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', required=False, max_length=26, widget=forms.Select(choices=myChoices, attrs={'required':'True'}))

class SubjectDeletionForm(forms.Form):
    def __init__(self,  *args,**kwargs):
        super(SubjectDeletionForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+\
            ':'+str(option[6])+\
            ':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ \
                ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=26, widget=forms.Select(choices=myChoices,attrs={'onchange':'submit();'}))
        self.eventBox = self['regID']
            
        if('regID' in self.data and self.data['regID']!='--Choose Event--'):
            self.fields['regID'].initial = self.data['regID']

            eventDetails = self.data['regID'].split(':')
            depts = {"BTE":1,"CHE":2,"CE":3,"CSE":4,"EEE":5,"ECE":6,"ME":7,"MME":8,"CHEMISTRY":9,"PHYSICS":10}
            romans2int = {"I":1,"II":2,"III":3,"IV":4}
            dept = depts[eventDetails[0]]
            byear = romans2int[eventDetails[1]]
            bsem = romans2int[eventDetails[2]]
            ayear = int(eventDetails[3])
            asem = int(eventDetails[4])
            regulation = int(eventDetails[5])
            mode = eventDetails[6]
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            self.myFields = []
            self.deptSubjects = Subjects_Staging.objects.filter(RegEventId=currentRegEventId)
            for sub in self.deptSubjects:
                self.fields['Check' + sub.SubCode] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
                if('Check'+sub.SubCode in self.data.keys() and self.data['Check'+sub.SubCode]==True):
                    self.fields['Check' + sub.SubCode].initial = True
                self.myFields.append((sub.SubCode,sub.SubName,sub.Creditable,sub.Credits,sub.Type,sub.Category,sub.OfferedBy,regulation, sub.DistributionRatio, sub.MarkDistribution.Distribution,self['Check'+sub.SubCode]))
 

class SubjectFinalizeEventForm(forms.Form):
    def __init__(self, options, *args,**kwargs):
        super(SubjectFinalizeEventForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        print(options)
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in options]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices))

class StudentRegistrationUpdateForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(StudentRegistrationUpdateForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + str(Options[fi][0])] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+str(Options[fi][0])].initial = False
            self.checkFields.append(self['Check' + str(Options[fi][0])])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3],Options[fi][4],Options[fi][5],\
                Options[fi][6],Options[fi][7],Options[fi][8],Options[fi][9], self['Check' + str(Options[fi][0])]))


class RollListStatusForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(RollListStatusForm,self).__init__(*args, **kwargs)
        self.myFields=[]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1)
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))


class RollListRegulationDifferenceForm(forms.Form):
    def __init__(self, Options = None, *args,**kwargs):
        super(RollListRegulationDifferenceForm,self).__init__(*args, **kwargs)
        self.myFields = []
        self.radioFields = []
        Choices = [('YES','YES'),('NO','NO')]
        for row in range(len(Options[0])):
            stud_info = StudentInfo.objects.get(RegNo=Options[0][row]) 
            self.fields['RadioMode' + str(Options[0][row])] = forms.CharField(required = True, widget = forms.RadioSelect(choices=Choices))
            self.radioFields.append(self['RadioMode' + str(Options[0][row])])
            self.myFields.append((Options[0][row],Options[1],stud_info.Regulation,self['RadioMode' + str(Options[0][row])]))

class RollListFinalizeForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(RollListFinalizeForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation, row.id) for row in regIDs]
        myChoices = [(option[7], depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))

class GenerateRollListForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(GenerateRollListForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', required=False,\
            max_length=26, widget=forms.Select(choices=myChoices, attrs={'required':'True'}))


class RollListsCycleHandlerForm(forms.Form):
    def __init__(self, Options = None, *args, **kwargs):
        super(RollListsCycleHandlerForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.radioFields = []
        Choices = [('9','CHEMISTRY'),('10','PHYSICS')]
        for row in range(len(Options)):
            self.fields['RadioMode' + str(Options[row])] = forms.CharField(required = True, widget = forms.RadioSelect(choices=Choices))
            # self.fields['Check'+str(Options[row][0])].initial = False 
            self.radioFields.append(self['RadioMode' + str(Options[row])])
            self.myFields.append((Options[row],self['RadioMode' + str(Options[row])]))

    
class RollListStatusForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(RollListStatusForm,self).__init__(*args, **kwargs)
        self.myFields=[]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))

class UpdateSectionInfoForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(UpdateSectionInfoForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + str(Options[fi][0])] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+str(Options[fi][0])].initial = False  
            self.checkFields.append(self['Check' + str(Options[fi][0])])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3],Options[fi][4], self['Check' + str(Options[fi][0])]))


class UploadSectionInfoForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(UploadSectionInfoForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField()
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))


class RollListFeeUploadForm(forms.Form):
    def __init__(self, regIDs,*args,**kwargs):
        super(RollListFeeUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField()
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation, row.id) for row in regIDs]
        myChoices = [(option[7], depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        #attrs={'onchange':"submit();"}
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))


class NotRegisteredStatusForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(NotRegisteredStatusForm,self).__init__(*args, **kwargs)
        self.myFields=[]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation, row.id) for row in regIDs]
        myChoices = [(option[7], depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))


class RegistrationsUploadForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(RegistrationsUploadForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        myChoices = [(oIndex, depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) for oIndex, option in enumerate(Options)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=26, widget=forms.Select(choices=myChoices))


class RegistrationsFinalizeEventForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(RegistrationsFinalizeEventForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1)
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices))


class BacklogRegistrationForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(BacklogRegistrationForm,self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='B')
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        regEventIDKVs = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(regIDs)]
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['RegEvent'] = forms.CharField(label='Registration Evernt', widget = forms.Select(choices=regEventIDKVs,\
            attrs={'onchange':"submit();"}))
        if 'RegEvent' in self.data and self.data['RegEvent']!= '-- Select Registration Event --':
            regId = self.data.get('RegEvent')
            strs = regId.split(':')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            
            studentBacklogs = list(RollLists.objects.filter(RegEventId_id=currentRegEventId).values_list('student__RegNo', flat=True))
            studentBacklogs = [(row, row) for row in studentBacklogs]
            studentBacklogs = [(0,'--Select Reg Number--')] + studentBacklogs
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=studentBacklogs,\
                 attrs={'onchange':'submit();'}))  
            if('RegNo' in self.data and self.data['RegNo']!='--Select Reg Number--'):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                self.selectFields = [self.fields['RegEvent'], self.fields['RegNo']]
                studentRegistrations_1 = []
                if asem == 2:
                    reg_status_1 = RegistrationStatus.objects.filter(AYear=ayear,ASem=1, Regulation=regulation)
                    for regevent in reg_status_1:
                        studentRegistrations_1 += list(StudentRegistrations_Staging.objects.\
                            filter(RegNo=self.data['RegNo'],RegEventId=regevent.id))
                    studentRegistrations_1 = [row.sub_id for row in studentRegistrations_1]
                reg_status = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem, Regulation=regulation)
                studentRegistrations=[]
                for regevent in reg_status:
                    studentRegistrations += list(StudentRegistrations_Staging.objects.\
                        filter(RegNo=self.data['RegNo'],RegEventId=regevent.id))
                Selection={studentRegistrations[i].sub_id:studentRegistrations[i].Mode for i in range(len(studentRegistrations))}
                studentRegularRegistrations = []
                dropped_subjects = []
                registeredBacklogs = []
                for regn in studentRegistrations:
                    regEvent = RegistrationStatus.objects.get(id=regn.RegEventId)
                    print(regEvent.id,regEvent.Mode)
                    if (regEvent.Mode == 'R'):
                        studentRegularRegistrations.append(regn)
                    elif regEvent.Mode == 'D':
                        dropped_subjects.append(regn)
                    elif regEvent.Mode == 'B':
                        registeredBacklogs.append(regn)
                if byear == 1:
                    studentBacklogs = list(StudentBacklogs.objects.filter(RegNo=self.data['RegNo']).\
                        filter(BYear=byear,Dept=dept,BSem=bsem))
                    studentBacklogs += list(StudentBacklogs.objects.filter(RegNo=self.data['RegNo']).\
                        filter(BYear=byear).filter(~Q(Dept=dept)).filter(~Q(BSem=bsem)))
                else:
                    studentBacklogs = list(StudentBacklogs.objects.filter(RegNo=self.data['RegNo']))
                if len(studentRegistrations_1) != 0:
                    finalStudentBacklogs = []
                    for row in studentBacklogs:
                        if row.sub_id not in studentRegistrations_1:
                            finalStudentBacklogs.append(row)
                    studentBacklogs = finalStudentBacklogs
                self.addBacklogSubjects(studentBacklogs,registeredBacklogs,Selection)
                self.addRegularSubjects(studentRegularRegistrations)
                self.addDroppedRegularSubjects(dropped_subjects)
        else:
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=[], \
                attrs={'onchange':'submit();'}))
    def addBacklogSubjects(self, queryset, registeredBacklogs, Selection):
        validBacklogs = [row.sub_id for row in queryset]
        regBacklogsdict = {row.sub_id:row.id for row in registeredBacklogs}
        for bRow in queryset:
            existingSubjects = Subjects.objects.filter(id=bRow.sub_id)
            if(len(existingSubjects)!=0):
                if(bRow.sub_id in Selection.keys()):
                    self.fields['Check' + str(bRow.sub_id)] = forms.BooleanField(required=False, \
                        widget=forms.CheckboxInput(attrs={'checked':True}))
                    if(bRow.Grade == 'R'):
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                    else:
                        mode = Selection[bRow.sub_id] 
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
                        self.fields['RadioMode' + str(bRow.sub_id)].initial = str(mode)
                        print("here")
                    self.myFields.append((bRow.SubCode, bRow.SubName, bRow.Credits, self['Check' + str(bRow.sub_id)], 
                                    self['RadioMode' + str(bRow.sub_id)],bRow.sub_id in Selection.keys(),'B', bRow.OfferedYear, \
                                        bRow.Regulation, bRow.sub_id, regBacklogsdict[bRow.sub_id]))
                else:
                    self.fields['Check' + str(bRow.sub_id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
                    if(bRow.Grade == 'R'):
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])     
                    else:
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
                    self.myFields.append((bRow.SubCode, bRow.SubName, bRow.Credits, self['Check' + str(bRow.sub_id)], 
                                    self['RadioMode' + str(bRow.sub_id)],bRow.sub_id in Selection.keys(),'B', bRow.OfferedYear,\
                                         bRow.Regulation, bRow.sub_id,''))
                self.checkFields.append(self['Check' + str(bRow.sub_id)])
                self.radioFields.append(self['RadioMode' + str(bRow.sub_id)])
        for row in registeredBacklogs:
            if row.sub_id not in validBacklogs:
                bRow = StudentBacklogs.objects.filter(RegNo=self.data['RegNo'], sub_id=row.sub_id)
                bRow = bRow[0]
                self.fields['Check' + str(bRow.sub_id)] = forms.BooleanField(required=False, \
                    widget=forms.CheckboxInput(attrs={'checked':True}))
                if(bRow.Grade == 'R'):
                    self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                else:
                    mode = Selection[bRow.sub_id] 
                    print(Selection[bRow.sub_id])
                    self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                        widget=forms.RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')], initial=str(mode))
                self.myFields.append((bRow.SubCode, bRow.SubName, bRow.Credits, self['Check' + str(bRow.sub_id)], 
                                    self['RadioMode' + str(bRow.sub_id)],bRow.sub_id in Selection.keys(),'B', bRow.OfferedYear, \
                                        bRow.Regulation, bRow.sub_id, row.id))
                self.checkFields.append(self['Check' + str(bRow.sub_id)])
                self.radioFields.append(self['RadioMode' + str(bRow.sub_id)])

    def addRegularSubjects(self, queryset):
        for bRow in queryset:
            SubjectDetails = Subjects.objects.filter(id=bRow.sub_id)
            regEvent = RegistrationStatus.objects.get(id=SubjectDetails[0].RegEventId)
            self.fields['Check' + str(SubjectDetails[0].id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails[0].id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            # self.fields['RadioMode' + str(SubjectDetails[0].id)].initial = 0
            self.checkFields.append(self['Check' + str(SubjectDetails[0].id)])
            self.radioFields.append(self['RadioMode' + str(SubjectDetails[0].id)])
            self.myFields.append((SubjectDetails[0].SubCode, SubjectDetails[0].SubName, SubjectDetails[0].Credits, \
                self['Check' + str(SubjectDetails[0].id)], self['RadioMode' + str(SubjectDetails[0].id)],True,\
                    'R',regEvent.AYear, regEvent.Regulation, SubjectDetails[0].id, bRow.id))
 
    def addDroppedRegularSubjects(self, queryset):
        for bRow in queryset:
            SubjectDetails = Subjects.objects.filter(id=bRow.sub_id)
            regEvent = RegistrationStatus.objects.get(id=SubjectDetails[0].RegEventId)
            self.fields['Check' + str(SubjectDetails[0].id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails[0].id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            # self.fields['RadioMode' + str(SubjectDetails[0].id)].initial = 0
            self.checkFields.append(self['Check' + str(SubjectDetails[0].id)])
            self.radioFields.append(self['RadioMode' + str(SubjectDetails[0].id)])
            self.myFields.append((SubjectDetails[0].SubCode, SubjectDetails[0].SubName, SubjectDetails[0].Credits, \
                self['Check' + str(SubjectDetails[0].id)], self['RadioMode' + str(SubjectDetails[0].id)],True,\
                    'D',regEvent.AYear, regEvent.Regulation, SubjectDetails[0].id, bRow.id))
 

class OpenElectiveRegistrationsForm(forms.Form):
    def __init__(self, subjects=None, *args,**kwargs):
        super(OpenElectiveRegistrationsForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices, attrs={'onchange': 'submit()'}))
        subChoices = [('--Select Subject--','--Select Subject--')]
        self.fields['subId'] = forms.CharField(label='Subject', widget=forms.Select(choices=subChoices))
        self.fields['file'] = forms.FileField(label='Select File', required=False)
        if 'regID' in self.data and self.data['regID'] != '--Choose Event--':
            subChoices += subjects
            self.fields['subId'] = forms.CharField(label='Subject', widget=forms.Select(choices=subChoices))


class DeptElectiveRegsForm(forms.Form):
    def __init__(self, subjects=None, *args,**kwargs):
        super(DeptElectiveRegsForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices, attrs={'onchange': 'submit()'}))
        subChoices = [('--Select Subject--','--Select Subject--')]
        self.fields['subId'] = forms.CharField(label='Subject', widget=forms.Select(choices=subChoices))
        if 'regID' in self.data and self.data['regID'] != '--Choose Event--':
            subChoices += subjects
            self.fields['subId'] = forms.CharField(label='Subject', widget=forms.Select(choices=subChoices))


class DroppedRegularRegistrationsForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(DroppedRegularRegistrationsForm, self).__init__(*args, **kwargs)
        print(*args)
        print(**kwargs)
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='D')
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        regEventIDKVs = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(regIDs)]
        print(regEventIDKVs)
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['RegEvent'] = forms.CharField(label='Registration Evernt', widget = forms.Select(choices=regEventIDKVs,\
            attrs={'onchange':"submit();"}))
        if 'RegEvent' in self.data and self.data['RegEvent']!= '-- Select Registration Event --':
            print("In if")
            regId = self.data.get('RegEvent')
            strs = regId.split(':')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            dropped_regno = list(RollLists.objects.filter(RegEventId_id=currentRegEventId).values_list('student__RegNo', flat=True))
            dropped_regno = [(reg, reg) for reg in dropped_regno]  
            dropped_regno = [(0,'--Select Roll Number --')] + dropped_regno
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=dropped_regno, \
                attrs={'onchange':'submit();'}))  
            if('RegNo' in self.data and self.data['RegNo']!='--Select Roll Number --'):
                #if('RollList' in self.data):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                self.selectFields = [self.fields['RegEvent'], self.fields['RegNo']]
                droppedCourses = DroppedRegularCourses.objects.filter(RegNo=self.data['RegNo'])
                subjects = []
                for row in droppedCourses:
                    sub = Subjects.objects.get(id=row.sub_id)
                    regEvent = RegistrationStatus.objects.get(id=sub.RegEventId)
                    if(regEvent.BYear == byear and regEvent.Regulation == regulation):
                        subjects.append(sub)
                reg_status = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem, Regulation=regulation)
                studentRegistrations=[]
                for regevent in reg_status:
                    studentRegistrations += list(StudentRegistrations_Staging.objects.filter(RegNo=self.data['RegNo'],RegEventId=regevent.id))
                Selection={studentRegistrations[i].sub_id:studentRegistrations[i].Mode for i in range(len(studentRegistrations))}
                studentRegularRegistrations = []
                studentBacklogs=[]
                registeredDroppedCourses = []
                for regn in studentRegistrations:
                    regEvent = RegistrationStatus.objects.get(id=regn.RegEventId)
                    if (regEvent.Mode == 'R'):
                        studentRegularRegistrations.append(regn)
                    elif regEvent.Mode == 'D' :
                        registeredDroppedCourses.append(regn)
                    elif regEvent.Mode == 'B':
                        studentBacklogs.append(regn)
                self.addBacklogSubjects(studentBacklogs,Selection,ayear)
                self.addRegularSubjects(studentRegularRegistrations)
                self.addDroppedRegularSubjects(subjects,registeredDroppedCourses,Selection)
        else:
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=[], attrs={'onchange':'submit();'}))
    
    def addBacklogSubjects(self, queryset,Selection,ayear):
        for bRow in queryset:
            existingSubjects = Subjects.objects.filter(id=bRow.sub_id)
            if(len(existingSubjects)!=0):
                if(bRow.sub_id in Selection.keys()):
                    subDetails = Subjects.objects.get(id=bRow.sub_id)
                    regevent = RegistrationStatus.objects.get(id=subDetails.RegEventId)
                    self.fields['Check' + str(bRow.sub_id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':True}))
                    if(bRow.Grade == 'R'):
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                    else:
                        mode = Selection[bRow.sub_id] 
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
                    self.checkFields.append(self['Check' + str(bRow.sub_id)])
                    self.radioFields.append(self['RadioMode' + str(bRow.sub_id)])
                    self.myFields.append((subDetails.SubCode, subDetails.SubName, subDetails.Credits, self['Check' + str(bRow.sub_id)], 
                                    self['RadioMode' + str(bRow.sub_id)],bRow.sub_id in Selection.keys(),'B', \
                                        regevent.OfferedYear, regevent.Regulation, bRow.sub_id, bRow.id))

    def addRegularSubjects(self, queryset):
        for bRow in queryset:
            SubjectDetails = Subjects.objects.filter(id=bRow.sub_id)
            regEvent = RegistrationStatus.objects.get(id=SubjectDetails[0].RegEventId)
            self.fields['Check' + str(SubjectDetails[0].id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails[0].id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            self.checkFields.append(self['Check' + str(SubjectDetails[0].id)])
            self.radioFields.append(self['RadioMode' + str(SubjectDetails[0].id)])
            self.myFields.append((SubjectDetails[0].SubCode, SubjectDetails[0].SubName, SubjectDetails[0].Credits, self['Check' + str(SubjectDetails[0].id)], 
                                self['RadioMode' + str(SubjectDetails[0].id)],True,'R',regEvent.AYear, \
                                    regEvent.Regulation, SubjectDetails[0].id, bRow.id))
 
    def addDroppedRegularSubjects(self, queryset, registeredDroppedCourses,Selection):
        for bRow in queryset:
            SubjectDetails = bRow
            regEvent = RegistrationStatus.objects.get(id=bRow.RegEventId)
            print(SubjectDetails.id)
            self.fields['Check' + str(SubjectDetails.id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails.id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            self.checkFields.append(self['Check' + str(SubjectDetails.id)])
            self.radioFields.append(self['RadioMode' + str(SubjectDetails.id)])
            if SubjectDetails.id in Selection.keys():
                dropped_reg = registeredDroppedCourses.filter(RegNo=self.data['RegNo'], sub_id=SubjectDetails.id)
                self.myFields.append((SubjectDetails.SubCode, SubjectDetails.SubName, SubjectDetails.Credits, self['Check' + str(SubjectDetails.id)], 
                                self['RadioMode' + str(SubjectDetails.id)],True,'D',regEvent.AYear, regEvent.Regulation,\
                                     SubjectDetails.id, dropped_reg[0].id))
            else:
                self.myFields.append((SubjectDetails.SubCode, SubjectDetails.SubName, SubjectDetails.Credits, self['Check' + str(SubjectDetails.id)], 
                                self['RadioMode' + str(SubjectDetails.id)],True,'D',regEvent.AYear, regEvent.Regulation, \
                                    SubjectDetails.id, ''))
 

class MakeupRegistrationsForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(MakeupRegistrationsForm,self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='M')
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        regEventIDKVs = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(regIDs)]
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['RegEvent'] = forms.CharField(label='Registration Evernt', widget = forms.Select(choices=regEventIDKVs,\
            attrs={'onchange':"submit();"}))
        if 'RegEvent' in self.data and self.data['RegEvent']!= '-- Select Registration Event --':
            regId = self.data.get('RegEvent')
            strs = regId.split(':')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            studentMakeupRolls = list(RollLists.objects.filter(RegEventId_id=currentRegEventId).values_list('student__RegNo', flat=True))
            studentMakeupRolls = [(row, row) for row in studentMakeupRolls]
            studentMakeupRolls = [(0,'--Select Reg Number--')] + studentMakeupRolls
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=studentMakeupRolls,\
                 attrs={'onchange':'submit();'}))  
            if('RegNo' in self.data and self.data['RegNo']!='--Select Reg Number--'):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                studentMakeups = StudentMakeups.objects.filter(RegNo=self.data['RegNo'], BYear=byear, BSem=bsem)
                for mk in studentMakeups:
                    already_registered = StudentRegistrations_Staging.objects.filter(RegNo=self.data['RegNo'], sub_id=mk.sub_id, \
                        RegEventId=currentRegEventId)
                    if len(already_registered) != 0:
                        self.fields['Check' + str(mk.sub_id)] = forms.BooleanField(required=False, \
                        widget=forms.CheckboxInput(attrs={'checked':True}))
                    else:
                        self.fields['Check' + str(mk.sub_id)] = forms.BooleanField(required=False, \
                        widget=forms.CheckboxInput())
                    if(mk.Grade == 'I'):
                        self.fields['RadioMode' + str(mk.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                    elif mk.Grade == 'F':
                        self.fields['RadioMode' + str(mk.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(attrs={'checked': True}), choices=[('0', 'Exam Mode')])
                    elif mk.Grade == 'X':
                        self.fields['RadioMode' + str(mk.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode'),('0', 'Exam Mode')])
                    self.checkFields.append(self['Check' + str(mk.sub_id)])
                    self.radioFields.append(self['RadioMode' + str(mk.sub_id)])
                    self.myFields.append((mk.SubCode, mk.SubName, mk.Credits, self['Check' + str(mk.sub_id)],\
                        self['RadioMode' + str(mk.sub_id)],'M', mk.OfferedYear,mk.Regulation, mk.sub_id))



class NotPromotedListForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(NotPromotedListForm,self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Mode='R')
        regIDs = [(row.AYear, row.BYear, row.Dept, row.Regulation) for row in regIDs]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        regEventIDKVs = [(depts[option[2]-1]+':'+ years[option[1]]+':'+ \
            str(option[0])+ ':'+str(option[3]), depts[option[2]-1]+':'+ years[option[1]]+':'+ \
            str(option[0])+ ':'+str(option[3])) for oIndex, option in enumerate(regIDs)]
        regEventIDKVs = list(set(regEventIDKVs))
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['RegEvent'] = forms.CharField(label='Registration Evernt', widget = forms.Select(choices=regEventIDKVs)) 

class NotPromotedUploadForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(NotPromotedUploadForm,self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Mode='R')
        regIDs = [(row.AYear, row.BYear, row.Dept, row.Regulation) for row in regIDs]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        regEventIDKVs = [(depts[option[2]-1]+':'+ years[option[1]]+':'+ \
            str(option[0])+ ':'+str(option[3]), depts[option[2]-1]+':'+ years[option[1]]+':'+ \
            str(option[0])+ ':'+str(option[3])) for oIndex, option in enumerate(regIDs)]
        regEventIDKVs = list(set(regEventIDKVs))
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['RegEvent'] = forms.CharField(label='Registration Event', widget = forms.Select(choices=regEventIDKVs))
        self.fields['file'] = forms.FileField(label='Upload not promoted list')    

class NotPromotedUpdateForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(NotPromotedUpdateForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + str(Options[fi][0])] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+str(Options[fi][0])].initial = False  
            self.checkFields.append(self['Check' + str(Options[fi][0])])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3], Options[fi][4], Options[fi][5], self['Check' + str(Options[fi][0])])) 

class NotPromotedStatusForm(forms.Form):
      def __init__(self, Options=None, *args,**kwargs):
        super(NotPromotedStatusForm, self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Mode='R')
        regIDs = [(row.AYear, row.BYear, row.Dept, row.Regulation) for row in regIDs]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        regEventIDKVs = [(depts[option[2]-1]+':'+ years[option[1]]+':'+ \
            str(option[0])+ ':'+str(option[3]), depts[option[2]-1]+':'+ years[option[1]]+':'+ \
            str(option[0])+ ':'+str(option[3])) for oIndex, option in enumerate(regIDs)]
        regEventIDKVs = list(set(regEventIDKVs))
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['RegEvent'] = forms.CharField(label='Registration Event', widget = forms.Select(choices=regEventIDKVs))



class RegularRegistrationsStatusForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(RegularRegistrationsStatusForm, self).__init__(*args, **kwargs)
        groups = user.groups.all().values_list('name', flat=True)
        departments = ProgrammeModel.objects.filter(ProgrammeType='UG')
        if 'Superintendent' in groups:
            deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        elif 'Co-ordinator' in groups:
            coordinator = Coordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
            departments = departments.filter(Dept=coordinator.Dept)
            deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        elif 'Cycle-Co-ordinator' in groups:
            cycle_cord = CycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
            departments = departments.filter(Dept=cycle_cord.Dept)
            deptChoices = [(rec.Dept, rec.Specialization) for rec in departments]
        aYearChoices = [(0,'--Select AYear--')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        aSemChoices = [(0,'--Select ASem--')] + [(1,1),(2,2)]
        regNoChoices = [(0,'--Select RegNo--')]
        deptChoices = [(0,'--Select Dept--')] + deptChoices
        # bYearChoices = [(0,'--Select BYear--'),(1,1), (2, 2),(3, 3),(4, 4)]
        # bSemChoices = [(0,'--Select BSem--'),(1,1),(2,2)]
        aYearBox = forms.IntegerField(label='Select AYear', widget=forms.Select(choices=aYearChoices,attrs={'onchange':'submit();'}))
        aSemBox = forms.IntegerField(label='Select ASem', widget=forms.Select(choices=aSemChoices, attrs={'onchange':'submit()'}),\
             required=False)
        deptBox = forms.IntegerField(label='Select Department', widget=forms.Select(choices=deptChoices, attrs={'onchange':'submit();'}), \
            required=False)
        regNoBox = forms.IntegerField(label='Select RegNo', widget=forms.Select(choices=regNoChoices,attrs={'onchange':'submit();'})\
            , required=False)
        self.fields['aYear'] = aYearBox
        self.fields['aSem'] = aSemBox
        self.fields['dept'] = deptBox
        self.fields['regNo'] = regNoBox
        if 'aYear' in self.data.keys() and self.data['aYear']!='0':
            regNo = RegularRegistrationSummary.objects.filter(AYear=int(self.data['aYear']))
            if 'aSem' in self.data.keys() and self.data['aSem']!='0':
                regNo = regNo.filter(ASem=int(self.data['aSem']))
            if 'dept' in self.data.keys() and self.data['dept']!='0':
                regNo = regNo.filter(Dept=int(self.data['dept']))
            regNo = regNo.values('RegNo').distinct()
            regNo = list(regNo)
            regNoChoices = [(i['RegNo'],i['RegNo']) for i in regNo]
            regNoChoices = [(0,'--Select RegNo--')]+regNoChoices
            regNoBox = forms.IntegerField(label='Select RegNo', widget=forms.Select(choices=regNoChoices,\
                    attrs={'onchange':'submit();'}), required=False)
            self.fields['regNo'] = regNoBox

class BacklogRegistrationSummaryForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(BacklogRegistrationSummaryForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1,Mode='B')
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+\
                 sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                     for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regId'] = forms.CharField(label='Choose Registration ID', max_length=30, \
            widget=forms.Select(choices=myChoices,attrs={'onchange':"submit();"}))
        regNoChoices = [(0,'--Choose RegNo--')]
        self.fields['RegNo'] = forms.IntegerField(label='Choose RegNo', widget=forms.Select(choices=regNoChoices, \
            attrs={'onchange':"submit()"}), required=False)
        if 'regId' in self.data.keys() and self.data['regId']!='--Choose Event--':
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I', 2:'II', 3:'III', 4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            strs = self.data['regId'].split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            regNoChoices = BacklogRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, BYear=byear, BSem=bsem, Dept=dept).values('RegNo').distinct()
            regNoChoices = [(i['RegNo'], i['RegNo']) for i in regNoChoices]
            regNoChoices = [(0,'--Choose RegNo--')] + regNoChoices
            self.fields['RegNo'] = forms.IntegerField(label='Choose RegNo', widget=forms.Select(choices=regNoChoices, \
            attrs={'onchange':"submit()"}), required=False)

class MakeupRegistrationSummaryForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(MakeupRegistrationSummaryForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II', 3:'III'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1,Mode='M')
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        self.regIDs = list(set(self.regIDs))
        myChoices = [(depts[option[3]-1]+':'+ years[option[2]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[5])+':'+str(option[4]), depts[option[3]-1]+':'+ years[option[2]]\
                +':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[5])+':'+str(option[4])) \
                     for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regId'] = forms.CharField(label='Choose Registration ID', max_length=30, \
            widget=forms.Select(choices=myChoices,attrs={'onchange':"submit();"}))
        regNoChoices = [(0,'--Choose RegNo--')]
        self.fields['RegNo'] = forms.IntegerField(label='Choose RegNo', widget=forms.Select(choices=regNoChoices, \
            attrs={'onchange':"submit()"}), required=False)
        if 'regId' in self.data.keys() and self.data['regId']!='--Choose Event--':
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I', 2:'II', 3:'III', 4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            strs = self.data['regId'].split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[2])
            asem = int(strs[3])
            byear = rom2int[strs[1]]
            # bsem = rom2int[strs[2]]
            regulation = int(strs[4])
            mode = strs[5]
            regNoChoices = MakeupRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, BYear=byear, Dept=dept).values('RegNo').distinct()
            regNoChoices = [(i['RegNo'], i['RegNo']) for i in regNoChoices]
            regNoChoices = [(0,'--Choose RegNo--')] + regNoChoices
            self.fields['RegNo'] = forms.IntegerField(label='Choose RegNo', widget=forms.Select(choices=regNoChoices, \
            attrs={'onchange':"submit()"}), required=False)



class FacultySubjectAssignmentForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(FacultySubjectAssignmentForm, self).__init__(*args, **kwargs)
        self.regIDs = []
        if regIDs:
            self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        myChoices = [(DEPARTMENTS[option[4]-1]+':'+ YEARS[option[2]]+':'+ SEMS[option[3]]+':'+ str(option[0])+ ':'+\
            str(option[1])+':'+str(option[6])+':'+str(option[5]), DEPARTMENTS[option[4]-1]+':'+ \
                YEARS[option[2]]+':'+ SEMS[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, \
        widget=forms.Select(choices=myChoices))

class FacultyAssignmentStatusForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(FacultyAssignmentStatusForm,self).__init__(*args, **kwargs)
        regEventIDKVs = [(reg.id,reg.__str__()) for reg in regIDs]
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['regID'] = forms.CharField(label='Registration Event', required=False, widget = forms.Select(choices=regEventIDKVs, attrs={'required':'True'}))

class GradeChallengeForm(forms.Form):
    def __init__(self, co_ordinator, *args, **kwargs):
        super(GradeChallengeForm, self).__init__(*args, **kwargs)
        faculty = FacultyAssignment.objects.filter(Faculty__Dept=co_ordinator.Dept, RegEventId__BYear=co_ordinator.BYear, RegEventId__Status=1)
        # regIDs = RegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Dept, BYear=faculty.BYear)
        regEventIDKVs = [(fac.RegEventId.id,fac.RegEventId.__str__()) for fac in faculty]
        regEventIDKVs = [('','-- Select Registration Event --')] + regEventIDKVs
        SUBJECT_CHOICES = [('', 'Choose Subject')]
        ROLL_CHOICES = [('', '--------')]
        EXAM_TYPE_CHOICES = [('', '--------')]
        self.fields['regID'] = forms.CharField(label='Registration Event', widget = forms.Select(choices=regEventIDKVs, attrs={'onchange':"submit()"}))
        self.fields['subject'] = forms.CharField(label='Choose Subject', widget = forms.Select(choices=SUBJECT_CHOICES))
        self.fields['regd_no'] = forms.ChoiceField(label='Choose Roll Number', widget=forms.Select(choices=ROLL_CHOICES))
        self.fields['exam-type'] = forms.ChoiceField(label='Choose Exam Type', widget=forms.Select(choices=EXAM_TYPE_CHOICES))

        if self.data.get('regID') and self.data.get('subject') and self.data.get('regd_no'):
            subject = Subjects.objects.get(id=self.data.get('subject'))
            self.subject = subject
            EXAM_TYPE_CHOICES += subject.MarkDistribution.distributions()
            self.fields['exam-type'] = forms.ChoiceField(label='Choose Exam Type', widget=forms.Select(choices=EXAM_TYPE_CHOICES))
            self.fields['mark'] = forms.CharField(label='Enter Marks', widget=forms.TextInput(attrs={'type':'number'}))
        elif self.data.get('regID') and self.data.get('subject'):
            marks_list = Marks_Staging.objects.filter(Registration__RegEventId=self.data.get('regID'), Registration__sub_id=self.data.get('subject')).order_by('Registration__RegNo')
            ROLL_CHOICES += [(mark.id, mark.Registration.RegNo) for mark in marks_list]
            self.fields['regd_no'] = forms.ChoiceField(label='Choose Roll Number', widget=forms.Select(choices=ROLL_CHOICES, attrs={'onchange':"submit()"}))
        elif self.data.get('regID'):
            student_registrations = StudentRegistrations.objects.filter(RegEventId=self.data.get('regID'))
            self.regs = student_registrations
            subjects = Subjects.objects.filter(id__in=student_registrations.values_list('sub_id', flat=True))
            SUBJECT_CHOICES += [(sub.id, sub.SubCode) for sub in subjects]
            self.fields['subject'] = forms.CharField(label='Choose Subject', widget = forms.Select(choices=SUBJECT_CHOICES, attrs={'onchange':"submit()"}))
    
    def clean_mark(self):
        if 'mark' in self.cleaned_data.keys():
            mark = self.cleaned_data.get('mark')
            exam_type = self.cleaned_data.get('exam-type')
            exam_inner_index = exam_type.split(',')[1]
            exam_outer_index = exam_type.split(',')[0]
            mark_dis_limit = self.subject.MarkDistribution.get_mark_limit(exam_outer_index, exam_inner_index)
            if mark > mark_dis_limit:
                raise forms.ValidationError('Entered mark is greater than the maximum marks.')
            return mark
        return None

    
class GradeChallengeStatusForm(forms.Form):
    def __init__(self, subjects, *args, **kwargs):
        super(GradeChallengeStatusForm, self).__init__(*args, **kwargs)
        subject_Choices=[]
        for sub in subjects:
            subject_Choices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id),sub.RegEventId.__str__()+', '+\
                str(sub.Subject.SubCode))]
        subject_Choices = list(set(subject_Choices))
        subject_Choices = [('','--Select Subject--')] + subject_Choices
        self.fields['subject'] = forms.CharField(label='Choose Subject', max_length=26, widget=forms.Select(choices=subject_Choices))

class NotRegisteredRegistrationsForm(forms.Form):
    def __init__(self, co_ordinator, *args, **kwargs):
        super(NotRegisteredRegistrationsForm, self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Dept, BYear=co_ordinator.BYear, Mode='R')
        REGID_CHOICES = [('', 'Choose Event')]
        REGID_CHOICES += [(reg.id, reg.__str__())for reg in regIDs]
        self.fields['regEvent'] = forms.ChoiceField(label='Choose Event', widget=forms.Select(choices=REGID_CHOICES, attrs={'onchange':"submit()"}))

        if self.data.get('regEvent'):
            regEvent = RegistrationStatus.objects.get(id=self.data.get('regEvent'))
            not_registered_objs = NotRegistered.objects.filter(RegEventId__Dept=regEvent.Dept, RegEventId__BYear=regEvent.BYear, Registered=False).order_by('Student__RegNo', '-RegEventId_id').distinct('Student__RegNo')
            REGNO_CHOICES = [('','Choose RegNo')]
            REGNO_CHOICES += [(nr_obj.id, str(nr_obj.Student.RegNo)+', '+nr_obj.RegEventId.__str__()) for nr_obj in not_registered_objs]
            self.fields['regd_no'] = forms.ChoiceField(label='Choose RegNo', widget=forms.Select(choices=REGNO_CHOICES)) 

            if self.data.get('regd_no'):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                self.selectFields = [self.fields['regEvent'], self.fields['regd_no']]
                
                '''
                Query all the courses corresponding to the registration event and display those courses which are not registered even once.
                '''
                selected_nr_object = not_registered_objs.filter(id=self.data.get('regd_no'))
                not_registered_courses = Subjects.objects.filter(RegEventId=selected_nr_object.RegEventId).exclude(Q(Category='OEC')|Q(Category='DEC'))
                reg_status_objs = RegistrationStatus.objects.filter(AYear=regEvent.AYear, ASem=regEvent.ASem, Regulation=regEvent.Regulation)
                student_registrations = StudentRegistrations_Staging.objects.filter(RegEventId__in=reg_status_objs.values_list('id', flat=True), RegNo=self.data.get('regd_no'))
                Selection={student_registrations[i].sub_id:student_registrations[i].Mode for i in range(len(student_registrations))}
                student_regular_regs = student_registrations.filter(RegEventId__in=reg_status_objs.filter(Mode='R').values_list('id', flat=True))
                student_backlog_regs = student_registrations.filter(RegEventId__in=reg_status_objs.filter(Mode='B').values_list('id', flat=True))
                student_dropped_regs = student_registrations.filter(RegEventId__in=reg_status_objs.filter(Mode='D').values_list('id', flat=True))
                registered_courses = StudentRegistrations_Staging.objects.filter(RegNo=self.data.get('regd_no'), sub_id__in=not_registered_courses.values_list('id', flat=True))
                self.addBacklogSubjects(student_backlog_regs, Selection)
                self.addRegularSubjects(student_regular_regs)
                self.addDroppedRegularSubjects(student_dropped_regs)
                self.addNotregisteredCourses(not_registered_courses, registered_courses)
        
    def addBacklogSubjects(self, queryset,Selection):
        for bRow in queryset:
            existingSubjects = Subjects.objects.filter(id=bRow.sub_id)
            if(len(existingSubjects)!=0):
                if(bRow.sub_id in Selection.keys()):
                    subDetails = Subjects.objects.get(id=bRow.sub_id)
                    regevent = RegistrationStatus.objects.get(id=subDetails.RegEventId)
                    self.fields['Check' + str(bRow.sub_id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':True}))
                    if(bRow.Grade == 'R'):
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                    else:
                        mode = Selection[bRow.sub_id] 
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
                    self.checkFields.append(self['Check' + str(bRow.sub_id)])
                    self.radioFields.append(self['RadioMode' + str(bRow.sub_id)])
                    self.myFields.append((subDetails.SubCode, subDetails.SubName, subDetails.Credits, self['Check' + str(bRow.sub_id)], 
                                    self['RadioMode' + str(bRow.sub_id)],bRow.sub_id in Selection.keys(),'B', \
                                        regevent.OfferedYear, regevent.Regulation, bRow.sub_id, bRow.id))

    def addRegularSubjects(self, queryset):
        for bRow in queryset:
            SubjectDetails = Subjects.objects.filter(id=bRow.sub_id)
            regEvent = RegistrationStatus.objects.get(id=SubjectDetails[0].RegEventId)
            self.fields['Check' + str(SubjectDetails[0].id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails[0].id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            self.checkFields.append(self['Check' + str(SubjectDetails[0].id)])
            self.radioFields.append(self['RadioMode' + str(SubjectDetails[0].id)])
            self.myFields.append((SubjectDetails[0].SubCode, SubjectDetails[0].SubName, SubjectDetails[0].Credits, self['Check' + str(SubjectDetails[0].id)], 
                                self['RadioMode' + str(SubjectDetails[0].id)],True,'R',regEvent.AYear, \
                                    regEvent.Regulation, SubjectDetails[0].id, bRow.id))
 
    def addDroppedRegularSubjects(self, queryset):
        for bRow in queryset:
            SubjectDetails = Subjects.objects.filter(id=bRow.sub_id)
            regEvent = RegistrationStatus.objects.get(id=SubjectDetails[0].RegEventId)
            self.fields['Check' + str(SubjectDetails[0].id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails[0].id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            # self.fields['RadioMode' + str(SubjectDetails[0].id)].initial = 0
            self.checkFields.append(self['Check' + str(SubjectDetails[0].id)])
            self.radioFields.append(self['RadioMode' + str(SubjectDetails[0].id)])
            self.myFields.append((SubjectDetails[0].SubCode, SubjectDetails[0].SubName, SubjectDetails[0].Credits, \
                self['Check' + str(SubjectDetails[0].id)], self['RadioMode' + str(SubjectDetails[0].id)],True,\
                    'D',regEvent.AYear, regEvent.Regulation, SubjectDetails[0].id, bRow.id))

    def addNotregisteredCourses(self, queryset, registered_courses, Selection):
        for row in queryset:
            # if row.id in Selection.keys():
            #     registration = StudentRegistrations_Staging.objects.filter()
            #     self.fields['Check'+str(row.id)] = forms.BooleanField(required=False,\
            #         widget=forms.CheckboxInput(attrs={'checked':True}))
            #     self.fields['RadioMode' + str(row.id)] = forms.ChoiceField(required=False, \
            #                 widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
            #     self.myFields.append((row.SubCode, row.SubName, row.Credits, self['Check' + str(row.id)], 
            #                         self['RadioMode' + str(row.id)],row.id in Selection.keys(),'R', row.OfferedYear, \
            #                             row.Regulation, row.id))
            # else:
            if not registered_courses.filter(sub_id=row.id).exists():
                self.fields['Check' + str(row.id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
                self.fields['RadioMode' + str(row.id)] = forms.ChoiceField(required=False, \
                        widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                self.myFields.append((row.SubCode, row.SubName, row.Credits, self['Check' + str(row.id)], 
                                self['RadioMode' + str(row.id)],row.id in Selection.keys(),'NR', row.OfferedYear, \
                                    row.Regulation, row.id, ''))
            

