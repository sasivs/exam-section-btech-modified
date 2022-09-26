from django import forms 
from django.db.models import Q 
from BTco_ordinator.models import  BTStudentRegistrations_Staging
from BTsuperintendent.constants import DEPARTMENTS, YEARS, SEMS
from BTco_ordinator.models import BTNotRegistered, BTSubjects_Staging, BTSubjects, BTStudentBacklogs, BTRollLists,\
    BTDroppedRegularCourses, BTStudentMakeups, BTRegularRegistrationSummary, BTBacklogRegistrationSummary, BTMakeupRegistrationSummary
from ADUGDB.models import BTRegistrationStatus
from BTExamStaffDB.models import BTStudentInfo

from BTsuperintendent.validators import validate_file_extension

#Create your forms here


class RegistrationsEventForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(RegistrationsEventForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+\
                 sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                     for oIndex, option in enumerate(regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, \
            widget=forms.Select(choices=myChoices,attrs={'onchange':"submit();"}))

class SubjectsUploadForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(SubjectsUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField(required=False, validators=[validate_file_extension])
        self.fields['file'].widget.attrs.update({'required':'True'})
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        myChoices = [(oIndex, depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ \
            ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) for oIndex, option in enumerate(Options)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', required=False, max_length=26, widget=forms.Select(choices=myChoices, attrs={'required':'True'}))

class SubjectDeletionForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(SubjectDeletionForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = []
        if regIDs:
            self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+\
            ':'+str(option[6])+\
            ':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ \
                ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=26, widget=forms.Select(choices=myChoices,attrs={'onchange':'submit();'}))
        self.eventBox = self['regID']
            
        if('regID' in self.data and self.data['regID']!=''):
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
            currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            self.myFields = []
            self.deptSubjects = BTSubjects_Staging.objects.filter(RegEventId=currentRegEventId)
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
        self.regIDs = BTRegistrationStatus.objects.filter(Status=1)
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
            stud_info = BTStudentInfo.objects.get(RegNo=Options[0][row]) 
            self.fields['RadioMode' + str(Options[0][row])] = forms.CharField(required = True, widget = forms.RadioSelect(choices=Choices))
            self.radioFields.append(self['RadioMode' + str(Options[0][row])])
            self.myFields.append((Options[0][row], stud_info.RollNo, stud_info.Name, Options[1],stud_info.Regulation,self['RadioMode' + str(Options[0][row])]))

class RollListFinalizeForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(RollListFinalizeForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = []
        if regIDs:
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
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3], self['Check' + str(Options[fi][0])]))


class UploadSectionInfoForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(UploadSectionInfoForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField(validators=[validate_file_extension])
        if regIDs:
            myChoices = [(reg.id, reg.__str__())for reg in regIDs]
        myChoices = [('','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))


class RollListFeeUploadForm(forms.Form):
    def __init__(self, regIDs,*args,**kwargs):
        super(RollListFeeUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField(validators=[validate_file_extension])
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
        myChoices = [('','--Choose Event--')]+myChoices
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
    def __init__(self, regIDs, *args,**kwargs):
        super(RegistrationsFinalizeEventForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = []
        if regIDs:
            self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices))


class BacklogRegistrationForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(BacklogRegistrationForm,self).__init__(*args, **kwargs)
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
            currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            
            studentBacklogs = list(BTRollLists.objects.filter(RegEventId_id=currentRegEventId).values_list('student__RegNo', flat=True))
            studentBacklogs = [(row, row) for row in studentBacklogs]
            studentBacklogs = [('','--Select Reg Number--')] + studentBacklogs
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=studentBacklogs,\
                 attrs={'onchange':'submit();'}))  
            if('RegNo' in self.data and self.data['RegNo']!=''):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                self.selectFields = [self.fields['RegEvent'], self.fields['RegNo']]
                studentRegistrations_1 = []
                if asem == 2:
                    reg_status_1 = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=1, Regulation=regulation)
                    for regevent in reg_status_1:
                        studentRegistrations_1 += list(BTStudentRegistrations_Staging.objects.\
                            filter(RegNo=self.data['RegNo'],RegEventId=regevent.id))
                    studentRegistrations_1 = [row.sub_id.id for row in studentRegistrations_1]
                reg_status = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem, Regulation=regulation)
                studentRegistrations=[]
                for regevent in reg_status:
                    studentRegistrations += list(BTStudentRegistrations_Staging.objects.\
                        filter(RegNo=self.data['RegNo'],RegEventId=regevent.id))
                Selection={studentRegistrations[i].sub_id.id:studentRegistrations[i].Mode for i in range(len(studentRegistrations))}
                studentRegularRegistrations = []
                dropped_subjects = []
                registeredBacklogs = []
                for regn in studentRegistrations:
                    regEvent = BTRegistrationStatus.objects.get(id=regn.RegEventId.id)
                    if (regEvent.Mode == 'R'):
                        studentRegularRegistrations.append(regn)
                    elif regEvent.Mode == 'D':
                        dropped_subjects.append(regn)
                    elif regEvent.Mode == 'B':
                        registeredBacklogs.append(regn)
                if byear == 1:
                    studentBacklogs = BTStudentBacklogs.objects.filter(RegNo=self.data['RegNo'], BYear=byear, BSem=bsem, Dept=dept).exclude(AYASBYBS__startswith=ayear)
                    # studentBacklogs = list(BTStudentBacklogs.objects.filter(RegNo=self.data['RegNo']).\
                    #     filter(BYear=byear,Dept=dept,BSem=bsem))
                    # studentBacklogs += list(BTStudentBacklogs.objects.filter(RegNo=self.data['RegNo']).\
                    #     filter(BYear=byear).filter(~Q(Dept=dept)).filter(~Q(BSem=bsem)))
                else:
                    studentBacklogs = list(BTStudentBacklogs.objects.filter(RegNo=self.data['RegNo'], BYear=byear, BSem=bsem, Dept=dept).exclude(AYASBYBS__startswith=ayear))
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
        regBacklogsdict = {row.sub_id.id:row.id for row in registeredBacklogs}
        for bRow in queryset:
            existingSubjects = BTSubjects.objects.filter(id=bRow.sub_id)
            if(len(existingSubjects)!=0):
                if(bRow.sub_id in Selection.keys()):
                    self.fields['Check' + str(bRow.sub_id)] = forms.BooleanField(required=False, \
                        widget=forms.CheckboxInput(attrs={'checked':True}))
                    if(bRow.Grade == 'R'):
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                    else:
                        mode = Selection[bRow.sub_id]
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, choices=[(1, 'Study Mode'), (0, 'Exam Mode')], initial=mode,\
                            widget=forms.RadioSelect())
                        # self.fields['RadioMode' + str(bRow.sub_id)].initial = str(mode)
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
            if row.sub_id.id not in validBacklogs:
                bRow = BTStudentBacklogs.objects.filter(RegNo=self.data['RegNo'], sub_id=row.sub_id.id)
                bRow = bRow[0]
                self.fields['Check' + str(bRow.sub_id)] = forms.BooleanField(required=False, \
                    widget=forms.CheckboxInput(attrs={'checked':True}))
                if(bRow.Grade == 'R'):
                    self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                else:
                    mode = Selection[bRow.sub_id] 
                    self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                        choices=[(1, 'Study Mode'), (0, 'Exam Mode')], initial=mode, widget=forms.RadioSelect(),)
                self.myFields.append((bRow.SubCode, bRow.SubName, bRow.Credits, self['Check' + str(bRow.sub_id)], 
                                    self['RadioMode' + str(bRow.sub_id)],bRow.sub_id in Selection.keys(),'B', bRow.OfferedYear, \
                                        bRow.Regulation, bRow.sub_id, row.id))
                self.checkFields.append(self['Check' + str(bRow.sub_id)])
                self.radioFields.append(self['RadioMode' + str(bRow.sub_id)])

    def addRegularSubjects(self, queryset):
        for bRow in queryset:
            SubjectDetails = BTSubjects.objects.filter(id=bRow.sub_id.id)
            regEvent = BTRegistrationStatus.objects.get(id=SubjectDetails[0].RegEventId_id)
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
            SubjectDetails = BTSubjects.objects.filter(id=bRow.sub_id.id)
            regEvent = BTRegistrationStatus.objects.get(id=SubjectDetails[0].RegEventId_id)
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
    def __init__(self,regIDs, subjects=None, *args,**kwargs):
        super(OpenElectiveRegistrationsForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = regIDs
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices, attrs={'onchange': 'submit()'}))
        subChoices = [('--Select Subject--','--Select Subject--')]
        self.fields['subId'] = forms.CharField(label='Subject', widget=forms.Select(choices=subChoices))
        self.fields['file'] = forms.FileField(label='Select File', required=False, validators=[validate_file_extension])
        if 'regID' in self.data and self.data['regID'] != '--Choose Event--':
            subChoices += subjects
            self.fields['subId'] = forms.CharField(label='Subject', widget=forms.Select(choices=subChoices))


class DeptElectiveRegsForm(forms.Form):
    def __init__(self, regIDs,subjects=None, *args,**kwargs):
        super(DeptElectiveRegsForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = regIDs
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
    def __init__(self,regIDs, *args,**kwargs):
        super(DroppedRegularRegistrationsForm, self).__init__(*args, **kwargs)
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
            currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            dropped_regno = list(BTRollLists.objects.filter(RegEventId_id=currentRegEventId).values_list('student__RegNo', flat=True))
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
                droppedCourses = BTDroppedRegularCourses.objects.filter(student__RegNo=self.data['RegNo'])
                subjects = []
                for row in droppedCourses:
                    if(row.RegEventId.BYear == byear and row.RegEventId.Regulation == regulation):
                        subjects.append(row.subject)
                reg_status = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem, Regulation=regulation)
                studentRegistrations=[]
                for regevent in reg_status:
                    studentRegistrations += list(BTStudentRegistrations_Staging.objects.filter(RegNo=self.data['RegNo'],RegEventId=regevent.id))
                Selection={studentRegistrations[i].sub_id.id:studentRegistrations[i].Mode for i in range(len(studentRegistrations))}
                studentRegularRegistrations = []
                studentBacklogs=[]
                registeredDroppedCourses = []
                for regn in studentRegistrations:
                    regEvent = BTRegistrationStatus.objects.get(id=regn.RegEventId.id)
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
            existingSubjects = BTSubjects.objects.filter(id=bRow.sub_id.id)
            if(len(existingSubjects)!=0):
                if(bRow.sub_id.id in Selection.keys()):
                    subDetails = BTSubjects.objects.get(id=bRow.sub_id.id)
                    regevent = BTRegistrationStatus.objects.get(id=subDetails.RegEventId)
                    self.fields['Check' + str(bRow.sub_id.id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':True}))
                    if(bRow.Grade == 'R'):
                        self.fields['RadioMode' + str(bRow.sub_id.id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                    else:
                        mode = Selection[bRow.sub_id.id] 
                        self.fields['RadioMode' + str(bRow.sub_id.id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
                    self.checkFields.append(self['Check' + str(bRow.sub_id.id)])
                    self.radioFields.append(self['RadioMode' + str(bRow.sub_id.id)])
                    self.myFields.append((subDetails.SubCode, subDetails.SubName, subDetails.Credits, self['Check' + str(bRow.sub_id.id)], 
                                    self['RadioMode' + str(bRow.sub_id)],bRow.sub_id in Selection.keys(),'B', \
                                        regevent.OfferedYear, regevent.Regulation, bRow.sub_id.id, bRow.id))

    def addRegularSubjects(self, queryset):
        for bRow in queryset:
            SubjectDetails = BTSubjects.objects.filter(id=bRow.sub_id.id)
            regEvent = BTRegistrationStatus.objects.get(id=SubjectDetails[0].RegEventId_id)
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
            regEvent = BTRegistrationStatus.objects.get(id=bRow.RegEventId_id)
            print(SubjectDetails.id)
            self.fields['Check' + str(SubjectDetails.id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails.id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            self.checkFields.append(self['Check' + str(SubjectDetails.id)])
            self.radioFields.append(self['RadioMode' + str(SubjectDetails.id)])
            if SubjectDetails.id in Selection.keys():
                dropped_reg = registeredDroppedCourses.filter(RegNo=self.data['RegNo'], sub_id_id=SubjectDetails.id)
                self.myFields.append((SubjectDetails.SubCode, SubjectDetails.SubName, SubjectDetails.Credits, self['Check' + str(SubjectDetails.id)], 
                                self['RadioMode' + str(SubjectDetails.id)],True,'D',regEvent.AYear, regEvent.Regulation,\
                                     SubjectDetails.id, dropped_reg[0].id))
            else:
                self.myFields.append((SubjectDetails.SubCode, SubjectDetails.SubName, SubjectDetails.Credits, self['Check' + str(SubjectDetails.id)], 
                                self['RadioMode' + str(SubjectDetails.id)],True,'D',regEvent.AYear, regEvent.Regulation, \
                                    SubjectDetails.id, ''))
 

class MakeupRegistrationsForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(MakeupRegistrationsForm,self).__init__(*args, **kwargs)
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
            currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            studentMakeupRolls = list(BTRollLists.objects.filter(RegEventId_id=currentRegEventId).values_list('student__RegNo', flat=True))
            studentMakeupRolls.sort()
            studentMakeupRolls = [(row, row) for row in studentMakeupRolls]
            studentMakeupRolls = [(0,'--Select Reg Number--')] + studentMakeupRolls
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=studentMakeupRolls,\
                 attrs={'onchange':'submit();'}))  
            if('RegNo' in self.data and self.data['RegNo']!='--Select Reg Number--'):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                studentMakeups = BTStudentMakeups.objects.filter(RegNo=self.data['RegNo'], BYear=byear, BSem=bsem)
                for mk in studentMakeups:
                    already_registered = BTStudentRegistrations_Staging.objects.filter(RegNo=self.data['RegNo'], sub_id=mk.sub_id, \
                        RegEventId=currentRegEventId)
                    if len(already_registered) != 0:
                        self.fields['Check' + str(mk.sub_id)] = forms.BooleanField(required=False, \
                        widget=forms.CheckboxInput(attrs={'checked':True}))
                    else:
                        self.fields['Check' + str(mk.sub_id)] = forms.BooleanField(required=False, \
                        widget=forms.CheckboxInput())
                    if(mk.Grade == 'I'):
                        self.fields['RadioMode' + str(mk.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(), choices=[('1', 'Study Mode'),('0', 'Exam Mode')])
                    elif mk.Grade == 'F':
                        self.fields['RadioMode' + str(mk.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(), choices=[('1', 'Study Mode'),('0', 'Exam Mode')])
                    elif mk.Grade == 'X':
                        self.fields['RadioMode' + str(mk.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(), choices=[('1', 'Study Mode'),('0', 'Exam Mode')])
                    self.checkFields.append(self['Check' + str(mk.sub_id)])
                    self.radioFields.append(self['RadioMode' + str(mk.sub_id)])
                    self.myFields.append((mk.SubCode, mk.SubName, mk.Credits, self['Check' + str(mk.sub_id)],\
                        self['RadioMode' + str(mk.sub_id)],'M', mk.OfferedYear,mk.Regulation, mk.sub_id))



class NotPromotedListForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(NotPromotedListForm,self).__init__(*args, **kwargs)
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
    def __init__(self, regIDs, *args,**kwargs):
        super(NotPromotedUploadForm,self).__init__(*args, **kwargs)
        regIDs = [(row.AYear, row.BYear, row.Dept, row.Regulation) for row in regIDs]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        regEventIDKVs = [(depts[option[2]-1]+':'+ years[option[1]]+':'+ \
            str(option[0])+ ':'+str(option[3]), depts[option[2]-1]+':'+ years[option[1]]+':'+ \
            str(option[0])+ ':'+str(option[3])) for oIndex, option in enumerate(regIDs)]
        regEventIDKVs = list(set(regEventIDKVs))
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['RegEvent'] = forms.CharField(label='Registration Event', widget = forms.Select(choices=regEventIDKVs))
        self.fields['file'] = forms.FileField(label='Upload not promoted list', validators=[validate_file_extension])    

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
      def __init__(self, regIDs, *args,**kwargs):
        super(NotPromotedStatusForm, self).__init__(*args, **kwargs)
        if regIDs:
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
    def __init__(self, regIDs, *args, **kwargs):
        super(RegularRegistrationsStatusForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs=[]
        if regIDs:
            self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
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
            regNoChoices = BTRegularRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, BYear=byear, BSem=bsem, Dept=dept).values('RegNo').distinct()
            regNoChoices = [(i['RegNo'], i['RegNo']) for i in regNoChoices]
            regNoChoices = [(0,'--Choose RegNo--')] + regNoChoices
            self.fields['RegNo'] = forms.IntegerField(label='Choose RegNo', widget=forms.Select(choices=regNoChoices, \
            attrs={'onchange':"submit()"}), required=False)

class BacklogRegistrationSummaryForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(BacklogRegistrationSummaryForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = []
        if regIDs:
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
            regNoChoices = BTBacklogRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, BYear=byear, BSem=bsem, Dept=dept).values('RegNo').distinct()
            regNoChoices = [(i['RegNo'], i['RegNo']) for i in regNoChoices]
            regNoChoices = [(0,'--Choose RegNo--')] + regNoChoices
            self.fields['RegNo'] = forms.IntegerField(label='Choose RegNo', widget=forms.Select(choices=regNoChoices, \
            attrs={'onchange':"submit()"}), required=False)

class MakeupRegistrationSummaryForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(MakeupRegistrationSummaryForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II', 3:'III'}
        self.regIDs = []
        if regIDs:
            self.regIDs = [(row.AYear, row.ASem, row.BYear, row.Dept, row.Mode, row.Regulation) for row in regIDs]
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
            regNoChoices = BTMakeupRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
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
        myChoices = [('','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, \
        widget=forms.Select(choices=myChoices))

class FacultyAssignmentStatusForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(FacultyAssignmentStatusForm,self).__init__(*args, **kwargs)
        regEventIDKVs = [(reg.id,reg.__str__()) for reg in regIDs]
        regEventIDKVs = [('','-- Select Registration Event --')] + regEventIDKVs
        self.fields['regID'] = forms.CharField(label='Registration Event', required=False, widget = forms.Select(choices=regEventIDKVs, attrs={'required':'True'}))


class NotRegisteredRegistrationsForm(forms.Form):
    def __init__(self, regIDs, *args, **kwargs):
        super(NotRegisteredRegistrationsForm, self).__init__(*args, **kwargs)
        REGID_CHOICES = [('', 'Choose Event')]
        if regIDs:
            REGID_CHOICES += [(reg.id, reg.__str__())for reg in regIDs]
        self.fields['regEvent'] = forms.ChoiceField(label='Choose Event', required=False, choices=REGID_CHOICES, widget=forms.Select(attrs={'onchange':"submit()", 'required':'True'}))

        if self.data.get('regEvent'):
            regEvent = BTRegistrationStatus.objects.get(id=self.data.get('regEvent'))
            not_registered_objs = BTNotRegistered.objects.filter(RegEventId__Dept=regEvent.Dept, RegEventId__BYear=regEvent.BYear, Registered=False).exclude(RegEventId=regEvent).order_by('Student__RegNo', '-RegEventId_id').distinct('Student__RegNo')
            REGNO_CHOICES = [('','Choose RegNo')]
            REGNO_CHOICES += [(nr_obj.id, str(nr_obj.Student.RegNo)+', '+nr_obj.RegEventId.__str__()) for nr_obj in not_registered_objs]
            self.fields['regd_no'] = forms.ChoiceField(label='Choose RegNo', required=False, choices=REGNO_CHOICES, widget=forms.Select(attrs={'required':'True', 'onchange':'submit();'})) 

            if self.data.get('regd_no'):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                self.selectFields = [self.fields['regEvent'], self.fields['regd_no']]
                
                '''
                Query all the courses corresponding to the registration event and display those courses which are not registered even once.
                '''
                selected_nr_object = not_registered_objs.filter(id=self.data.get('regd_no')).first()
                regNo = selected_nr_object.Student.RegNo
                not_registered_courses = BTSubjects.objects.filter(RegEventId=selected_nr_object.RegEventId).exclude(Q(Category='OEC')|Q(Category='DEC'))
                reg_status_objs = BTRegistrationStatus.objects.filter(AYear=regEvent.AYear, ASem=regEvent.ASem, Regulation=regEvent.Regulation)
                student_registrations = BTStudentRegistrations_Staging.objects.filter(RegEventId__in=reg_status_objs.values_list('id', flat=True), RegNo=regNo)
                Selection={student_registrations[i].sub_id:student_registrations[i].Mode for i in range(len(student_registrations))}
                student_regular_regs = student_registrations.filter(RegEventId__in=reg_status_objs.filter(Mode='R').values_list('id', flat=True))
                student_backlog_regs = student_registrations.filter(RegEventId__in=reg_status_objs.filter(Mode='B').values_list('id', flat=True))
                student_dropped_regs = student_registrations.filter(RegEventId__in=reg_status_objs.filter(Mode='D').values_list('id', flat=True))
                registered_courses = BTStudentRegistrations_Staging.objects.filter(RegNo=regNo, sub_id__in=not_registered_courses.values_list('id', flat=True))
                self.addBacklogSubjects(student_backlog_regs, Selection)
                self.addRegularSubjects(student_regular_regs)
                self.addDroppedRegularSubjects(student_dropped_regs)
                self.addNotregisteredCourses(not_registered_courses, registered_courses, Selection)
        
    def addBacklogSubjects(self, queryset,Selection):
        for bRow in queryset:
            existingSubjects = BTSubjects.objects.filter(id=bRow.sub_id)
            if(len(existingSubjects)!=0):
                if(bRow.sub_id in Selection.keys()):
                    subDetails = BTSubjects.objects.get(id=bRow.sub_id)
                    regevent = BTRegistrationStatus.objects.get(id=subDetails.RegEventId)
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
            SubjectDetails = BTSubjects.objects.filter(id=bRow.sub_id)
            regEvent = BTRegistrationStatus.objects.get(id=SubjectDetails[0].RegEventId.id)
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
            SubjectDetails = BTSubjects.objects.filter(id=bRow.sub_id)
            regEvent = BTRegistrationStatus.objects.get(id=SubjectDetails[0].RegEventId)
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
            if not registered_courses.filter(sub_id=row.id).exists():
                self.fields['Check' + str(row.id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
                self.fields['RadioMode' + str(row.id)] = forms.ChoiceField(required=False, \
                        widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                self.myFields.append((row.SubCode, row.SubName, row.Credits, self['Check' + str(row.id)], 
                                self['RadioMode' + str(row.id)],row.id in Selection.keys(),'NR', row.RegEventId.AYear, \
                                    row.RegEventId.Regulation, row.id, ''))


class GradesThresholdEventWise(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(GradesThresholdEventWise, self).__init__(*args, **kwargs)
        MY_CHOICES = []
        if regIDs:
            MY_CHOICES = [(regEvent.id, regEvent.__str__) for regEvent in regIDs]
        MY_CHOICES = [('','--Choose Event--')]+MY_CHOICES
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', required=False,\
            max_length=26, widget=forms.Select(choices=MY_CHOICES, attrs={'required':'True'}))
        self.fields['file'] = forms.FileField(required=False, validators=[validate_file_extension])
        self.fields['file'].widget.attrs.update({'required':'True'})    
