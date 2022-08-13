from django import forms 
from django.db.models import Q 
from MTco_ordinator.models import MTStudentRegistrations, MTStudentRegistrations_Staging
from MThod.models import MTCoordinator
from MTsuperintendent.constants import DEPARTMENTS, YEARS, SEMS
from MTco_ordinator.models import MTFacultyAssignment, MTNotRegistered, MTSubjects_Staging, MTSubjects, MTStudentBacklogs, MTRollLists,\
     MTStudentMakeups, MTRegularRegistrationSummary, MTBacklogRegistrationSummary, MTMakeupRegistrationSummary
from MTsuperintendent.models import MTProgrammeModel
from ADPGDB.models import MTRegistrationStatus
from MTExamStaffDB.models import MTStudentInfo
from MTfaculty.models import MTMarks_Staging
import datetime
from MTsuperintendent.validators import validate_file_extension

#Create your forms here

class RegistrationsEventForm(forms.Form):
    def __init__(self,regIDs, *args,**kwargs):
        super(RegistrationsEventForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode,row.Regulation) for row in regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, widget=forms.Select(choices=myChoices,attrs={'onchange':"submit();"}))


class StudentRegistrationUpdateForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(StudentRegistrationUpdateForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + str(Options[fi][0])] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+str(Options[fi][0])].initial = False  
            self.checkFields.append(self['Check' + str(Options[fi][0])])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3],Options[fi][4],Options[fi][5],Options[fi][6],Options[fi][7],Options[fi][8],Options[fi][9], Options[fi][10], self['Check' + str(Options[fi][0])]))





class SubjectsUploadForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(SubjectsUploadForm, self).__init__(*args, **kwargs)
        self.fields['file']=forms.FileField(required=False)
        self.fields['file'].widget.attrs.update({'required':'True'})
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        myChoices = [(oIndex, depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) for oIndex, option in enumerate(Options)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID',required=False, max_length=20, widget=forms.Select(choices=myChoices))


class SubjectDeletionForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(SubjectDeletionForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs = []
        if regIDs:
            self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode,row.Regulation) for row in regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('','--Choose Event--')]+myChoices
        #attrs={'onchange':"submit();"}
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=26, widget=forms.Select(choices=myChoices,attrs={'onchange':'submit();'}))
        self.eventBox = self['regID']
            
        if('regID' in self.data and self.data['regID']!='--Choose Event--'):
            self.fields['regID'].initial = self.data['regID']

            eventDetails = self.data['regID'].split(':')
            print(self.data['regID'])
            depts = {"BTE":1,"CHE":2,"CE":3,"CSE":4,"EEE":5,"ECE":6,"ME":7,"MME":8}
            romans2int = {"I":1,"II":2}
            dept = depts[eventDetails[0]]
            myear = romans2int[eventDetails[1]]
            msem = romans2int[eventDetails[2]]
            ayear = int(eventDetails[3])
            asem = int(eventDetails[4])
            regulation=int(eventDetails[5])
            mode = eventDetails[6]
            currentRegEventId=MTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,MYear=myear,MSem=msem,Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId=currentRegEventId[0].id
            self.myFields = []
            self.deptSubjects = MTSubjects_Staging.objects.filter(RegEventId=currentRegEventId)
            for sub in self.deptSubjects:
                self.fields['Check' + sub.SubCode] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
                if('Check'+sub.SubCode in self.data.keys() and self.data['Check'+sub.SubCode]==True):
                    self.fields['Check' + sub.SubCode].initial = True
                self.myFields.append((sub.SubCode,sub.SubName,sub.Creditable,sub.Credits, sub.Type,sub.Category,sub.OfferedBy,sub.ProgrammeCode, sub.DistributionRatio, sub.MarkDistribution.Distribution,self['Check'+sub.SubCode]))
 
 
class SubjectFinalizeEventForm(forms.Form):
    def __init__(self,options, *args,**kwargs):
        super(SubjectFinalizeEventForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode,row.Regulation) for row in options]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        #attrs={'onchange':"submit();"}
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, widget=forms.Select(choices=myChoices))


class RollListStatusForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(RollListStatusForm,self).__init__(*args, **kwargs)
        self.myFields=[]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs = MTRegistrationStatus.objects.filter(Status=1)
        self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))




class RollListFinalizeForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(RollListFinalizeForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation, row.id) for row in regIDs]
        myChoices = [(option[7], depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))

class GenerateRollListForm(forms.Form):
    def __init__(self,  regIDs, *args,**kwargs):
        super(GenerateRollListForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        #attrs={'onchange':"submit();"}
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', required=False,\
            max_length=26, widget=forms.Select(choices=myChoices, attrs={'required':'True'}))

    
class RollListStatusForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(RollListStatusForm,self).__init__(*args, **kwargs)
        self.myFields=[]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
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
        self.fields['file'] = forms.FileField(validators=[validate_file_extension])
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation, row.id) for row in regIDs]
        myChoices = [(option[7], depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        #attrs={'onchange':"submit();"}
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))



class NotRegisteredStatusForm(forms.Form):
    def __init__(self,regIDs, *args,**kwargs):
        super(NotRegisteredStatusForm,self).__init__(*args, **kwargs)
        self.myFields=[]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation, row.id) for row in regIDs]
        myChoices = [(option[7], depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))


class RegistrationsUploadForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(RegistrationsUploadForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        myChoices = [(oIndex, depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) for oIndex, option in enumerate(Options)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, widget=forms.Select(choices=myChoices))

class RegistrationsFinalizeEventForm(forms.Form):
    def __init__(self, regIDs,*args,**kwargs):
        super(RegistrationsFinalizeEventForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs = []
        if regIDs:
            self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode,row.Regulation) for row in regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices))



class BacklogRegistrationForm(forms.Form):
    def __init__(self,regIDs, *args,**kwargs):
        super(BacklogRegistrationForm,self).__init__(*args, **kwargs)
        print(regIDs)
        regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
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
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
            years = {1:'I',2:'II'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2}
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            myear = rom2int[strs[1]]
            msem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]

            currentRegEventId = MTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,MYear=myear,MSem=msem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            
            studentBacklogs = list(MTRollLists.objects.filter(RegEventId_id=currentRegEventId).values_list('student__RegNo', flat=True))
            studentBacklogs = [(rec, rec) for rec in studentBacklogs]
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
                    reg_status_1 = MTRegistrationStatus.objects.filter(AYear=ayear,ASem=1, Regulation=regulation)
                    for regevent in reg_status_1:
                        studentRegistrations_1 += list(MTStudentRegistrations_Staging.objects.\
                            filter(RegNo=self.data['RegNo'],RegEventId=regevent.id))
                    studentRegistrations_1 = [row.sub_id for row in studentRegistrations_1]
                reg_status = MTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem, Regulation=regulation)
                studentRegistrations=[]
                for regevent in reg_status:
                    studentRegistrations += list(MTStudentRegistrations_Staging.objects.\
                        filter(RegNo=self.data['RegNo'],RegEventId=regevent.id))
                Selection={studentRegistrations[i].sub_id:studentRegistrations[i].Mode for i in range(len(studentRegistrations))}
                
                registeredBacklogs = []
                for regn in studentRegistrations:
                    regEvent = MTRegistrationStatus.objects.get(id=regn.RegEventId)
        
                    if regEvent.Mode == 'B':
                        registeredBacklogs.append(regn)
               
                studentBacklogs = list(MTStudentBacklogs.objects.filter(RegNo=self.data['RegNo']))
                if len(studentRegistrations_1) != 0:
                    finalStudentBacklogs = []
                    for row in studentBacklogs:
                        if row.sub_id not in studentRegistrations_1:
                            finalStudentBacklogs.append(row)
                    studentBacklogs = finalStudentBacklogs
                self.addBacklogSubjects(studentBacklogs,registeredBacklogs,Selection)
               
        else:
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=[], \
                attrs={'onchange':'submit();'}))
    def addBacklogSubjects(self, queryset, registeredBacklogs, Selection):
        validBacklogs = [row.sub_id for row in queryset]
        regBacklogsdict = {row.sub_id:row.id for row in registeredBacklogs}
        for bRow in queryset:
            existingSubjects = MTSubjects.objects.filter(id=bRow.sub_id)
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
                bRow = MTStudentBacklogs.objects.filter(RegNo=self.data['RegNo'], sub_id=row.sub_id)
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

 
class OpenElectiveRegistrationsForm(forms.Form):
    def __init__(self,regIDs, subjects=None, *args,**kwargs):
        super(OpenElectiveRegistrationsForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs = []
        if regIDs:
            self.regIDs =regIDs
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices, attrs={'onchange': 'submit()'}))
        subChoices = [('--Select Subject--','--Select Subject--')]
        self.fields['subId'] = forms.CharField(label='Subject', widget=forms.Select(choices=subChoices))
        self.fields['file'] = forms.FileField(label='Select File', required=False,validators=[validate_file_extension])
        if 'regID' in self.data and self.data['regID'] != '--Choose Event--':
            subChoices += subjects
            self.fields['subId'] = forms.CharField(label='Subject', widget=forms.Select(choices=subChoices))

class DeptElectiveRegsForm(forms.Form):
    def __init__(self,regIDs, subjects=None, *args,**kwargs):
        super(DeptElectiveRegsForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs =regIDs
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

       
class MakeupRegistrationsForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(MakeupRegistrationsForm,self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
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
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
            years = {1:'I',2:'II'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2}
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            myear = rom2int[strs[1]]
            msem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            currentRegEventId = MTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,MYear=myear,MSem=msem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            studentMakeupRolls = list(MTRollLists.objects.filter(RegEventId_id=currentRegEventId).values_list('student__RegNo', flat=True))
            studentMakeupRolls.sort()
            studentMakeupRolls = [(roll,roll) for roll in studentMakeupRolls]
            studentMakeupRolls = [(0,'--Select Reg Number--')] + studentMakeupRolls
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=studentMakeupRolls,\
                 attrs={'onchange':'submit();'}))  
            if('RegNo' in self.data and self.data['RegNo']!='--Select Reg Number--'):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                studentMakeups = MTStudentMakeups.objects.filter(RegNo=self.data['RegNo'], MYear=myear, MSem=msem)
                for mk in studentMakeups:
                    already_registered = MTStudentRegistrations_Staging.objects.filter(RegNo=self.data['RegNo'], sub_id=mk.sub_id, \
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



class RegularRegistrationsStatusForm(forms.Form):
    def __init__(self, regIDs, *args, **kwargs):
        super(RegularRegistrationsStatusForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs=[]
        if regIDs:
            self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
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
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
            years = {1:'I', 2:'II'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2}
            strs = self.data['regId'].split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            myear = rom2int[strs[1]]
            msem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            regNoChoices = MTRegularRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, MYear=myear, MSem=msem, Dept=dept).values('RegNo').distinct()
            regNoChoices = [(i['RegNo'], i['RegNo']) for i in regNoChoices]
            regNoChoices = [(0,'--Choose RegNo--')] + regNoChoices
            self.fields['RegNo'] = forms.IntegerField(label='Choose RegNo', widget=forms.Select(choices=regNoChoices, \
            attrs={'onchange':"submit()"}), required=False)



class BacklogRegistrationSummaryForm(forms.Form):
    def __init__(self,regIDs, *args,**kwargs):
        super(BacklogRegistrationSummaryForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II'}
        self.regIDs = []
        if regIDs:
            self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
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
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
            years = {1:'I', 2:'II'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2}
            strs = self.data['regId'].split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            myear = rom2int[strs[1]]
            msem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            regNoChoices = MTBacklogRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, MYear=myear, MSem=msem, Dept=dept).values('RegNo').distinct()
            regNoChoices = [(i['RegNo'], i['RegNo']) for i in regNoChoices]
            regNoChoices = [(0,'--Choose RegNo--')] + regNoChoices
            self.fields['RegNo'] = forms.IntegerField(label='Choose RegNo', widget=forms.Select(choices=regNoChoices, \
            attrs={'onchange':"submit()"}), required=False)



class MakeupRegistrationSummaryForm(forms.Form):
    def __init__(self,regIDs, *args,**kwargs):
        super(MakeupRegistrationSummaryForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        sems = {1:'I',2:'II', 3:'III'}
        self.regIDs = []
        if regIDs:
            self.regIDs = [(row.AYear, row.ASem, row.MYear, row.Dept, row.Mode, row.Regulation) for row in regIDs]
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
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
            years = {1:'I', 2:'II'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2}
            strs = self.data['regId'].split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[2])
            asem = int(strs[3])
            myear = rom2int[strs[1]]
            # msem = rom2int[strs[2]]
            regulation = int(strs[4])
            mode = strs[5]
            regNoChoices = MTMakeupRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, MYear=myear, Dept=dept).values('RegNo').distinct()
            regNoChoices = [(i['RegNo'], i['RegNo']) for i in regNoChoices]
            regNoChoices = [(0,'--Choose RegNo--')] + regNoChoices
            self.fields['RegNo'] = forms.IntegerField(label='Choose RegNo', widget=forms.Select(choices=regNoChoices, \
            attrs={'onchange':"submit()"}), required=False)


class FacultySubjectAssignmentForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(FacultySubjectAssignmentForm, self).__init__(*args, **kwargs)
        self.regIDs = []
        if regIDs:
            self.regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
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
            regEvent = MTRegistrationStatus.objects.get(id=self.data.get('regEvent'))
            not_registered_objs = MTNotRegistered.objects.filter(RegEventId__Dept=regEvent.Dept, RegEventId__MYear=regEvent.MYear, Registered=False).exclude(RegEventId=regEvent).order_by('Student__RegNo', '-RegEventId_id').distinct('Student__RegNo')
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
                if selected_nr_object:
                    regNo = selected_nr_object.Student.RegNo
                not_registered_courses = MTSubjects.objects.filter(RegEventId=selected_nr_object.RegEventId).exclude(Q(Category='OEC')|Q(Category='DEC'))
                reg_status_objs = MTRegistrationStatus.objects.filter(AYear=regEvent.AYear, ASem=regEvent.ASem, Regulation=regEvent.Regulation)
                student_registrations = MTStudentRegistrations_Staging.objects.filter(RegEventId__in=reg_status_objs.values_list('id', flat=True), RegNo=regNo)
                Selection={student_registrations[i].sub_id:student_registrations[i].Mode for i in range(len(student_registrations))}
                # student_regular_regs = student_registrations.filter(RegEventId__in=reg_status_objs.filter(Mode='R').values_list('id', flat=True))
                # student_backlog_regs = student_registrations.filter(RegEventId__in=reg_status_objs.filter(Mode='B').values_list('id', flat=True))
                # student_dropped_regs = student_registrations.filter(RegEventId__in=reg_status_objs.filter(Mode='D').values_list('id', flat=True))
                registered_courses = MTStudentRegistrations_Staging.objects.filter(RegNo=regNo, sub_id__in=not_registered_courses.values_list('id', flat=True))
                # self.addBacklogSubjects(student_backlog_regs, Selection)
                # self.addRegularSubjects(student_regular_regs)
                # self.addDroppedRegularSubjects(student_dropped_regs)
                self.addNotregisteredCourses(not_registered_courses, registered_courses, Selection)
        
   
    def addNotregisteredCourses(self, queryset, registered_courses, Selection):
        for row in queryset:
            if not registered_courses.filter(sub_id=row.id).exists():
                self.fields['Check' + str(row.id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
                self.fields['RadioMode' + str(row.id)] = forms.ChoiceField(required=False, \
                        widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                self.myFields.append((row.SubCode, row.SubName, row.Credits, self['Check' + str(row.id)], 
                                self['RadioMode' + str(row.id)],row.id in Selection.keys(),'NR', row.RegEventId.AYear, \
                                    row.RegEventId.Regulation, row.id, ''))
            
