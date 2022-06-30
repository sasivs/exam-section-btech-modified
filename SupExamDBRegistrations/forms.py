from email.policy import default
from operator import itemgetter
from random import choices
from shutil import SpecialFileError
from .models import NotPromoted, ProgrammeModel, RegistrationStatus, RegularRegistrationSummary, StudentMakeups, StudentRegistrations, StudentInfo, Subjects,\
     Subjects_Staging, Regulation, DroppedRegularCourses, StudentRegistrations_Staging, BacklogRegistrationSummary,\
         MakeupRegistrationSummary, RollLists, FacultyInfo
from django import forms 
from django.forms import CheckboxInput, RadioSelect, ValidationError
from .models import StudentBacklogs
from django.db.models import F, Q 
from django.utils.translation import gettext_lazy as _
import datetime

class TestForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(TestForm, self).__init__(*args, **kwargs)
        self.myFields = []
        aYearChoices= [(i,i) for i in range(2020,2023)]
        aMonthChoices = {2020:[(i,i) for i in range(1,5)],2021:[(i,i) for i in range(5,8)], 2022:[(i,i) for i in range(8,13)]}

        self.fields['YrSelect'] = forms.IntegerField(label='Test Field',widget=forms.Select(choices=aYearChoices,\
            attrs={'onchange':"applySelection(this.value);"}))
        myChoices = []
        if('YrSelect' in self.data):
            myChoices = aMonthChoices[int(self.data['YrSelect'])]
        self.fields['MonthSelect'] = forms.IntegerField(label='TestMonth',widget=forms.Select(choices=myChoices))

class FirstYearBacklogRegistrationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FirstYearBacklogRegistrationForm, self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='B',BYear=1)
        num2Roman={1:'I',2:'II',3:'III',4:'IV',5:'V'}
        regEventIDKVs = [('First Year'+'-'+str(rec.AYear) + '-' + num2Roman[rec.ASem] + '-'+num2Roman[rec.BYear] + '-'\
            + num2Roman[rec.BSem],'First Year'+'-'+str(rec.AYear) + '-' + num2Roman[rec.ASem] + '-'+num2Roman[rec.BYear] +\
                 '-'+ num2Roman[rec.BSem]) for rec in regIDs]
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['RegEvent'] = forms.CharField(label='Registration Event', \
            widget = forms.Select(choices=regEventIDKVs,attrs={'onchange':"submit();"}))
        if 'RegEvent' in self.data and self.data['RegEvent'] != '-- Select Registration Event --':
            event = self.data.get('RegEvent')
            eventDetails = event.split('-')
            romans2int = {"I":1,"II":2,"III":3,"IV":4}
            byear = romans2int[eventDetails[3]]
            ayear = int(eventDetails[1])
            asem = romans2int[eventDetails[2]]
            bsem = romans2int[eventDetails[4]]
            regIds1 = list(StudentBacklogs.objects.filter(Dept=9,BYear = byear).values('RegNo', 'RollNo').distinct())
            regIds2 = list(StudentBacklogs.objects.filter(Dept=10,BYear = byear).values('RegNo', 'RollNo').distinct())
            #[regIds1.append(regIds2[i]) for i in range(len(regIds2))]
            regIds1 = regIds1 + regIds2 
            #print(regIds1)
            regIds = []
            for row in regIds1:
                if row['RollNo']:
                    regIds.append((row['RegNo'], row['RollNo']))
                else:
                    regIds.append((row['RegNo'], row['RegNo']))
            regIds.sort(key=itemgetter(1))
            regIds = [('-- Select RegNo/RollNo --','-- Select RegNo/RollNo --')]+regIds
            #print(regIds)
            self.fields['RegNo'] = forms.CharField(label = 'RegNo/RollNo', widget = forms.Select(choices =regIds ,attrs={'onchange':"submit();"}))
            if 'RegNo' in self.data and self.data['RegNo']!= '-- Select Registration/Roll Number --':
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                self.selectFields= [self.fields['RegNo']]
                studentBacklogs = StudentBacklogs.objects.filter(RegNo=self.data['RegNo'],BYear = byear).order_by('BYear','SubCode')
                studentRegistrations = StudentRegistrations.objects.filter(RegNo=self.data['RegNo'],AYear = ayear, ASem = asem).order_by('SubCode')
                Selection={studentRegistrations[i].SubCode:studentRegistrations[i].Mode for i in range(len(studentRegistrations))}
                studentRegistrations = studentRegistrations.filter(AYear=F('OfferedYear'))
                self.addRegularSubjects(studentRegistrations)
                self.addBacklogSubjects(studentBacklogs,Selection)

    def addBacklogSubjects(self, queryset, Selection):
        for bRow in queryset:
            existingSubjects = Subjects.objects.filter(SubCode=bRow.SubCode, OfferedYear=bRow.OfferedYear, Regulation = bRow.Regulation).values()
            if(len(existingSubjects)!=0):
                print(bRow.SubCode)
                if(bRow.SubCode in Selection.keys()):
                    self.fields['Check' + bRow.SubCode] = forms.BooleanField(required=False, widget=CheckboxInput(attrs={'checked':True}))
                    print(bRow.SubCode)
                    #self.fields['Check'+bRow.SubCode].initial = True 
                    if(bRow.Grade == 'R'):
                        
                        self.fields['RadioMode' + bRow.SubCode] = forms.ChoiceField(required=False, widget=RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                    else:
                        
                        mode = Selection[bRow.SubCode] 
                        print(Selection[bRow.SubCode])
                        self.fields['RadioMode' + bRow.SubCode] = forms.ChoiceField(required=False, widget=RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
                        #self.fields['RadioMode' + bRow.SubCode].initial = '1'
                    
                        #self.fields['RadioMode' + Options[fi][0]].widget.attrs['disabled'] = True  
                else:
                    self.fields['Check' + bRow.SubCode] = forms.BooleanField(required=False, widget=CheckboxInput())
                    if(bRow.Grade == 'R'):
                        self.fields['RadioMode' + bRow.SubCode] = forms.ChoiceField(required=False, widget=RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])     
                        #self.fields['RadioMode' + bRow.SubCode].initial = 0
                        #self.fields['RadioMode' +bRow.SubCode].widget.attrs['disabled'] = True  
                    else:
                        self.fields['RadioMode' + bRow.SubCode] = forms.ChoiceField(required=False, widget=RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
                        #self.fields['RadioMode' + bRow.SubCode].initial = '1'
                        
                
                self.checkFields.append(self['Check' + bRow.SubCode])
                self.radioFields.append(self['RadioMode' + bRow.SubCode])
                self.myFields.append((bRow.SubCode, bRow.SubName, bRow.Credits, self['Check' + bRow.SubCode], 
                                    self['RadioMode' + bRow.SubCode],bRow.SubCode in Selection.keys(),'B',bRow.OfferedYear,bRow.Regulation))

    def addRegularSubjects(self, queryset):
        for bRow in queryset:
            SubjectDetails = Subjects_Staging.objects.filter(SubCode=bRow.SubCode)
            print(bRow.SubCode)
            print(SubjectDetails)
            self.fields['Check' + SubjectDetails[0].SubCode] = forms.BooleanField(required=False, widget=CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode'+SubjectDetails[0].SubCode] = forms.ChoiceField(required=False, widget=RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            self.fields['RadioMode'+SubjectDetails[0].SubCode].initial = 0
            self.checkFields.append(self['Check' + SubjectDetails[0].SubCode])
            self.radioFields.append(self['RadioMode' + SubjectDetails[0].SubCode])
            self.myFields.append((SubjectDetails[0].SubCode, SubjectDetails[0].SubName, SubjectDetails[0].Credits, self['Check' + SubjectDetails[0].SubCode], 
                                self['RadioMode' + SubjectDetails[0].SubCode],True,'R',bRow.OfferedYear, bRow.Regulation))


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
                Options[fi][6],Options[fi][7],Options[fi][8],Options[fi][9],Options[fi][10], self['Check' + str(Options[fi][0])]))
class StudentInfoUpdateForm(forms.Form):
    def __init__(self, Options = None, *args, **kwargs):
        super(StudentInfoUpdateForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for row in range(len(Options)):
            self.fields['Check' + str(Options[row][0])] = forms.BooleanField(required = False, widget = forms.CheckboxInput())
            self.fields['Check'+str(Options[row][0])].initial = False 
            self.checkFields.append(self['Check' + str(Options[row][0])])
            self.myFields.append((Options[row][0], Options[row][1], Options[row][2],Options[row][3],Options[row][4],Options[row][5],\
                Options[row][6],Options[row][7],Options[row][8],Options[row][9],Options[row][10],Options[row][11],Options[row][12],Options[row][13],\
                     self['Check' + str(Options[row][0])]))
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
            


class SubjectsUploadForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(SubjectsUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField()
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        print(str(Options[0][4])+str(Options[0][3])+str(Options[0][2]))
        myChoices = [(oIndex, depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ \
            ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) for oIndex, option in enumerate(Options)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        print(myChoices)
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=26, widget=forms.Select(choices=myChoices))

class RegistrationsUploadForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(RegistrationsUploadForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        print(str(Options[0][4])+str(Options[0][3])+str(Options[0][2]))
        myChoices = [(oIndex, depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) for oIndex, option in enumerate(Options)]
        print(myChoices)
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=26, widget=forms.Select(choices=myChoices))

class RegistrationsEventForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(RegistrationsEventForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+\
                 sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                     for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        #attrs={'onchange':"submit();"}
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, \
            widget=forms.Select(choices=myChoices,attrs={'onchange':"submit();"}))

class BRegistrationsEventForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(BRegistrationsEventForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        statuses = {1:'Study',0:'Exam'}
        self.regIDs = RegistrationStatus.objects.filter(Mode='B')
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Status, row.Mode) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6] + ':' + statuses[option[5]])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        #attrs={'onchange':"submit();"}
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=40, widget=forms.Select(choices=myChoices,attrs={'onchange':"submit();"}))


class SampleForm(forms.Form):
    choices = [('KG', 'kg'),
        ('TN', 't'),]
    mytest = forms.CharField(label='Sample',widget=RadioSelect(choices=choices),initial='TN',required=False)

class StudentInfoFileUpload(forms.Form):
    file = forms.FileField()


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
        statusBox = forms.ChoiceField(label='Enable/Disable', widget=RadioSelect(), choices=[(0, 'Disable'), (1, 'Enable')])
        modeBox = forms.ChoiceField(label='Select Mode',widget=RadioSelect(),choices = [('R', 'Regular'),('B','Backlog'),('D','DroppedRegular'),('M','Makeup')])
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
            print(self.data)
            regulations = Regulation.objects.filter(AYear=self.data.get('aYear')).filter(BYear = self.data.get('bYear'))
            dropped_course_regulations = Regulation.objects.filter(AYear=str(int(self.data.get('aYear'))-1),BYear=self.data.get('bYear'))
            backlog_course_regulations = StudentBacklogs.objects.filter(BYear=self.data.get('bYear'))
            backlog_course_regulations = [(regu.Regulation,regu.Regulation) for regu in backlog_course_regulations]
            dropped_course_regulations = [(regu.Regulation,regu.Regulation) for regu in dropped_course_regulations]
            regulations = [(regu.Regulation,regu.Regulation) for regu in regulations]
            regulations +=  dropped_course_regulations + backlog_course_regulations
            regulations = list(set(regulations))
            rChoices += regulations
            print(rChoices)
            self.fields['regulation'] = forms.IntegerField(label='Select Regulation', widget=forms.Select(choices=rChoices))
        





class RegistrationForm1(forms.Form):
    def __init__(self, RegNo=None, Options=None, Selection=None, *args,**kwargs):
        super(RegistrationForm1, self).__init__(*args, **kwargs)
        self.fields['RegNo'] = forms.IntegerField(required=False, widget=forms.HiddenInput())
        self.fields['RegNo'].initial = RegNo 
        self.myFields = []
        self.checkFields = []
        self.radioFields = []
        for fi in range(len(Options)):
            self.fields['Check' + Options[fi][0]] = forms.BooleanField(required=False, widget=CheckboxInput())
            
            if(Options[fi][0] in Selection.keys()):
                self.fields['Check'+Options[fi][0]].initial = True 
                if(Options[fi][3] == 'R'):     
                    self.fields['RadioMode' + Options[fi][0]] = forms.ChoiceField(required=False, widget=RadioSelect(), choices=[(1, 'Study Mode')])
                    self.fields['RadioMode' + Options[fi][0]].initial = 1
                else:
                    self.fields['RadioMode' + Options[fi][0]] = forms.ChoiceField(required=False, widget=RadioSelect(), choices=[(0, 'Exam Mode'), (1, 'Study Mode')])
                    self.fields['RadioMode' + Options[fi][0]].initial = Selection[Options[fi][0]]
                
                    #self.fields['RadioMode' + Options[fi][0]].widget.attrs['disabled'] = True  
            else:
                if(Options[fi][3] == 'R'):
                    self.fields['RadioMode' + Options[fi][0]] = forms.ChoiceField(required=False, widget=RadioSelect(), choices=[(1, 'Study Mode')])     
                    self.fields['RadioMode' + Options[fi][0]].initial = 1
                    #self.fields['RadioMode' + Options[fi][0]].widget.attrs['disabled'] = True  
                else:
                    self.fields['RadioMode' + Options[fi][0]] = forms.ChoiceField(required=False, widget=RadioSelect(), choices=[(0, 'Exam Mode'), (1, 'Study Mode')])
                    self.fields['RadioMode' + Options[fi][0]].initial = 0
                     
            
            self.checkFields.append(self['Check' + Options[fi][0]])
            self.radioFields.append(self['RadioMode' + Options[fi][0]])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2], self['Check' + Options[fi][0]], 
                                self['RadioMode' + Options[fi][0]]))

class StudentCancellationForm(forms.Form):
    def __init__ (self,*args, **kwargs):
        super(StudentCancellationForm, self).__init__(*args, **kwargs)
        self.fields['RegNo'] = forms.CharField(label='Registration Number',max_length=7,min_length=6)

class StudentSemesterCancellationForm(forms.Form):
    def __init__ (self,*args, **kwargs):
        super(StudentSemesterCancellationForm, self).__init__(*args, **kwargs)
        choice = NotPromoted.objects.all().values()
        ch = [(each['RegNo'],each['RegNo']) for each in choice]
        ch.sort(key=itemgetter(1))
        ch = [('--Choose RegNO--','--Choose RegNO--')]+ch
        #print(ch)
        self.fields['RegNo'] = forms.IntegerField(required=False,label='Registration Number',widget = forms.Select(choices=ch,attrs={'onchange':'submit();'}))
        if 'RegNo' in self.data and self.data['RegNo'] != '--Choose RegNo--':
            BYch = list(NotPromoted.objects.filter(RegNo = int(self.data.get('RegNo'))).values('BYear'))
            BYch = [(BYch[0]['BYear'],BYch[0]['BYear'])]
            BYch = [('--Choose Byear--','--Choose Byear--')]+BYch
            self.fields['BYear']=forms.IntegerField(required=False,label='BYear',widget=forms.Select(choices=BYch, attrs={'onchange':'submit();'}))
            if 'BYear' in self.data and self.data['BYear'] != '1':
                BSch = [(0,'Choose BSem'),(1,1),(2,2)]
                self.fields['BSem'] = forms.IntegerField(required=False, label='BSem', widget=forms.Select(choices=BSch, attrs={'onchange':'submit();'}))
            if 'BYear' in self.data and self.data['BYear'] == '1':
                BSch = [(0,'Choose Cycle'),(9,9),(10,10)]
                self.fields['Cycle'] = forms.IntegerField(required=False, label='Cycle', widget=forms.Select(choices=BSch, attrs={'onchange':'submit();'}))
           
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
        #attrs={'onchange':"submit();"}
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=26, widget=forms.Select(choices=myChoices,attrs={'onchange':'submit();'}))
        self.eventBox = self['regID']
            
        if('regID' in self.data and self.data['regID']!='--Choose Event--'):
            self.fields['regID'].initial = self.data['regID']

            eventDetails = self.data['regID'].split(':')
            print(self.data['regID'])
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
                self.fields['Check' + sub.SubCode] = forms.BooleanField(required=False, widget=CheckboxInput())
                if('Check'+sub.SubCode in self.data.keys() and self.data['Check'+sub.SubCode]==True):
                    self.fields['Check' + sub.SubCode].initial = True
                self.myFields.append((sub.SubCode,sub.SubName,sub.Creditable,sub.Credits,regulation,sub.Type,sub.Category,self['Check'+sub.SubCode]))
 
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

#class RollNo
class GenerateRollListForm(forms.Form):
    def __init__(self,  *args,**kwargs):
        super(GenerateRollListForm, self).__init__(*args, **kwargs)
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
        #attrs={'onchange':"submit();"}
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))



class RollListErrorHandlerForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(RollListErrorHandlerForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + str(Options[fi])] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+str(Options[fi])].initial = False  
            self.checkFields.append(self['Check' + str(Options[fi][0])])
            self.myFields.append((Options[fi],self['Check' + str(Options[fi])]))

class SubjectFinalizeEventForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(SubjectFinalizeEventForm, self).__init__(*args, **kwargs)
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
            max_length=30, widget=forms.Select(choices=myChoices))

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
            dropped_courses = DroppedRegularCourses.objects.all()
            dropped_regno=[]
            for row in dropped_courses:
                sub_reg = StudentRegistrations_Staging.objects.filter(RegNo=row.RegNo, sub_id=row.sub_id)
                if(len(sub_reg) == 0):
                    sub = Subjects.objects.get(id=row.sub_id)
                    regEvent = RegistrationStatus.objects.get(id=sub.RegEventId)
                    if(regEvent.BYear == byear and regEvent.Regulation == regulation):
                        dropped_regno.append(row.RegNo)
            dropped_regno = list(set(dropped_regno))
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
                    self.fields['Check' + str(bRow.sub_id)] = forms.BooleanField(required=False, widget=CheckboxInput(attrs={'checked':True}))
                    if(bRow.Grade == 'R'):
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                    else:
                        mode = Selection[bRow.sub_id] 
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
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
                widget=CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails[0].id)] = forms.ChoiceField(required=False, \
                widget=RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
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
                widget=CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails.id)] = forms.ChoiceField(required=False, \
                widget=RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            self.checkFields.append(self['Check' + str(SubjectDetails.id)])
            self.radioFields.append(self['RadioMode' + str(SubjectDetails.id)])
            if SubjectDetails.id in Selection.keys():
                dropped_reg = registeredDroppedCourses.objects.filter(RegNo=self.data['RegNo'], sub_id=SubjectDetails.id)
                self.myFields.append((SubjectDetails.SubCode, SubjectDetails.SubName, SubjectDetails.Credits, self['Check' + str(SubjectDetails.id)], 
                                self['RadioMode' + str(SubjectDetails.id)],True,'D',regEvent.AYear, regEvent.Regulation,\
                                     SubjectDetails.id, dropped_reg[0].id))
            else:
                self.myFields.append((SubjectDetails.SubCode, SubjectDetails.SubName, SubjectDetails.Credits, self['Check' + str(SubjectDetails.id)], 
                                self['RadioMode' + str(SubjectDetails.id)],True,'D',regEvent.AYear, regEvent.Regulation, \
                                    SubjectDetails.id, ''))
 

            
class GradesUploadForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(GradesUploadForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1)
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+\
                 sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                     for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, \
            widget=forms.Select(choices=myChoices))
        self.fields['file'] = forms.FileField(label="Select file") 

class GradesUpdateForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(GradesUpdateForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + str(Options[fi][0])] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+str(Options[fi][0])].initial = False  
            self.checkFields.append(self['Check' + str(Options[fi][0])])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3],Options[fi][4],Options[fi][5],\
                Options[fi][6],Options[fi][7], self['Check' + str(Options[fi][0])]))

class GradesFinalizeForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(GradesFinalizeForm, self).__init__(*args, **kwargs)
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
            if byear == 1:
                studentBacklogs = list(StudentBacklogs.objects.filter(BYear=byear, Dept=dept, BSem=bsem).\
                    values('RegNo','RollNo').distinct())
                studentBacklogs += list(StudentBacklogs.objects.filter(BYear=byear).filter(~Q(Dept=dept)).\
                    filter(~Q(BSem=bsem)).values('RegNo','RollNo').distinct())
            else:
                studentBacklogs = StudentBacklogs.objects.filter(BYear=byear,Dept=dept).values('RegNo','RollNo').distinct()
            studentBacklogs = [(rec['RegNo'], rec['RegNo']) for rec in studentBacklogs]
            studentBacklogs = list(set(studentBacklogs))
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
                        widget=CheckboxInput(attrs={'checked':True}))
                    if(bRow.Grade == 'R'):
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                    else:
                        mode = Selection[bRow.sub_id] 
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
                        self.fields['RadioMode' + str(bRow.sub_id)].initial = str(mode)
                        print("here")
                    self.myFields.append((bRow.SubCode, bRow.SubName, bRow.Credits, self['Check' + str(bRow.sub_id)], 
                                    self['RadioMode' + str(bRow.sub_id)],bRow.sub_id in Selection.keys(),'B', bRow.OfferedYear, \
                                        bRow.Regulation, bRow.sub_id, regBacklogsdict[bRow.sub_id]))
                else:
                    self.fields['Check' + str(bRow.sub_id)] = forms.BooleanField(required=False, widget=CheckboxInput())
                    if(bRow.Grade == 'R'):
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])     
                    else:
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
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
                    widget=CheckboxInput(attrs={'checked':True}))
                if(bRow.Grade == 'R'):
                    self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                else:
                    mode = Selection[bRow.sub_id] 
                    print(Selection[bRow.sub_id])
                    self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                        widget=RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')], initial=str(mode))
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
                widget=CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails[0].id)] = forms.ChoiceField(required=False, \
                widget=RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
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
                widget=CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails[0].id)] = forms.ChoiceField(required=False, \
                widget=RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            # self.fields['RadioMode' + str(SubjectDetails[0].id)].initial = 0
            self.checkFields.append(self['Check' + str(SubjectDetails[0].id)])
            self.radioFields.append(self['RadioMode' + str(SubjectDetails[0].id)])
            self.myFields.append((SubjectDetails[0].SubCode, SubjectDetails[0].SubName, SubjectDetails[0].Credits, \
                self['Check' + str(SubjectDetails[0].id)], self['RadioMode' + str(SubjectDetails[0].id)],True,\
                    'D',regEvent.AYear, regEvent.Regulation, SubjectDetails[0].id, bRow.id))
 
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
            studentMakeupRolls = StudentMakeups.objects.filter(Dept=dept, BYear=byear, BSem=bsem).values('RegNo').distinct()
            studentMakeupRolls = [(roll['RegNo'],roll['RegNo']) for roll in studentMakeupRolls]
            studentMakeupRolls = [(0,'--Select Reg Number--')] + studentMakeupRolls
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=studentMakeupRolls,\
                 attrs={'onchange':'submit();'}))  
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
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
                        widget=CheckboxInput(attrs={'checked':True}))
                    else:
                        self.fields['Check' + str(mk.sub_id)] = forms.BooleanField(required=False, \
                        widget=CheckboxInput())
                    if(mk.Grade == 'I'):
                        self.fields['RadioMode' + str(mk.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                    elif mk.Grade == 'F':
                        self.fields['RadioMode' + str(mk.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(attrs={'checked': True}), choices=[('0', 'Exam Mode')])
                    elif mk.Grade == 'X':
                        self.fields['RadioMode' + str(mk.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode'),('0', 'Exam Mode')])
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
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3], self['Check' + str(Options[fi][0])])) 

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

class GradeChallengeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(GradeChallengeForm, self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Status=1)
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        regEventIDKVs = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(regIDs)]
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['regEvent'] = forms.CharField(label='Registration Event', widget = forms.Select(choices=regEventIDKVs))
        self.fields['file'] = forms.FileField(label='Upload File')

class UpdateRollNumberForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UpdateRollNumberForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField(label='Upload File')
class UpdateNonFirstYearSectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UpdateNonFirstYearSectionForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField(label='Upload File')

class RegularRegistrationsStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(RegularRegistrationsStatusForm, self).__init__(*args, **kwargs)
        aYearChoices = [(0,'--Select AYear--')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        aSemChoices = [(0,'--Select ASem--')] + [(1,1),(2,2)]
        regNoChoices = [(0,'--Select RegNo--')]
        departments = ProgrammeModel.objects.filter(ProgrammeType='UG')
        deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
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


class NotPromotedBacklogRegistrationForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(NotPromotedBacklogRegistrationForm,self).__init__(*args, **kwargs)
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
            if byear == 1:
                studentBacklogs = list(StudentBacklogs.objects.filter(BYear=byear, Dept=dept, BSem=bsem).\
                    values('RegNo','RollNo').distinct())
                studentBacklogs += list(StudentBacklogs.objects.filter(BYear=byear).filter(~Q(Dept=dept)).\
                    filter(~Q(BSem=bsem)).values('RegNo','RollNo').distinct())
            else:
                studentBacklogs = StudentBacklogs.objects.filter(BYear=byear,Dept=dept).values('RegNo','RollNo').distinct()
            notPromotedRegNos = NotPromoted.objects.filter(AYear=ayear, PoA='B').values('RegNo')
            notPromotedRegNos = [(rec['RegNo'], rec['RegNo']) for rec in notPromotedRegNos]
            notPromotedRegNos = set(notPromotedRegNos)
            studentBacklogs = [(rec['RegNo'], rec['RegNo']) for rec in studentBacklogs]
            studentBacklogs = set(studentBacklogs)
            studentBacklogs = list(studentBacklogs.intersection(notPromotedRegNos))
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
                    # print(regEvent.id,regEvent.Mode)
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
                # self.addRegularSubjects(studentRegularRegistrations)
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
                        widget=CheckboxInput(attrs={'checked':True}))
                    if(bRow.Grade == 'R'):
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                    else:
                        mode = Selection[bRow.sub_id] 
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
                        self.fields['RadioMode' + str(bRow.sub_id)].initial = str(mode)
                        print("here")
                    self.myFields.append((bRow.SubCode, bRow.SubName, bRow.Credits, self['Check' + str(bRow.sub_id)], 
                                    self['RadioMode' + str(bRow.sub_id)],bRow.sub_id in Selection.keys(),'B', bRow.OfferedYear, \
                                        bRow.Regulation, bRow.sub_id, regBacklogsdict[bRow.sub_id]))
                else:
                    self.fields['Check' + str(bRow.sub_id)] = forms.BooleanField(required=False, widget=CheckboxInput())
                    if(bRow.Grade == 'R'):
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])     
                    else:
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
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
                    widget=CheckboxInput(attrs={'checked':True}))
                if(bRow.Grade == 'R'):
                    self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                else:
                    mode = Selection[bRow.sub_id] 
                    print(Selection[bRow.sub_id])
                    self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                        widget=RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')], initial=str(mode))
                self.myFields.append((bRow.SubCode, bRow.SubName, bRow.Credits, self['Check' + str(bRow.sub_id)], 
                                    self['RadioMode' + str(bRow.sub_id)],bRow.sub_id in Selection.keys(),'B', bRow.OfferedYear, \
                                        bRow.Regulation, bRow.sub_id, row.id))
                self.checkFields.append(self['Check' + str(bRow.sub_id)])
                self.radioFields.append(self['RadioMode' + str(bRow.sub_id)])

    # def addRegularSubjects(self, queryset):
    #     for bRow in queryset:
    #         SubjectDetails = Subjects.objects.filter(id=bRow.sub_id)
    #         regEvent = RegistrationStatus.objects.get(id=SubjectDetails[0].RegEventId)
    #         self.fields['Check' + str(SubjectDetails[0].id)] = forms.BooleanField(required=False, \
    #             widget=CheckboxInput(attrs={'checked': True}))
    #         self.fields['RadioMode' + str(SubjectDetails[0].id)] = forms.ChoiceField(required=False, \
    #             widget=RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
    #         # self.fields['RadioMode' + str(SubjectDetails[0].id)].initial = 0
    #         self.checkFields.append(self['Check' + str(SubjectDetails[0].id)])
    #         self.radioFields.append(self['RadioMode' + str(SubjectDetails[0].id)])
    #         self.myFields.append((SubjectDetails[0].SubCode, SubjectDetails[0].SubName, SubjectDetails[0].Credits, \
    #             self['Check' + str(SubjectDetails[0].id)], self['RadioMode' + str(SubjectDetails[0].id)],True,\
    #                 'R',regEvent.AYear, regEvent.Regulation, SubjectDetails[0].id, bRow.id))
 
    def addDroppedRegularSubjects(self, queryset):
        for bRow in queryset:
            SubjectDetails = Subjects.objects.filter(id=bRow.sub_id)
            regEvent = RegistrationStatus.objects.get(id=SubjectDetails[0].RegEventId)
            self.fields['Check' + str(SubjectDetails[0].id)] = forms.BooleanField(required=False, \
                widget=CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails[0].id)] = forms.ChoiceField(required=False, \
                widget=RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            # self.fields['RadioMode' + str(SubjectDetails[0].id)].initial = 0
            self.checkFields.append(self['Check' + str(SubjectDetails[0].id)])
            self.radioFields.append(self['RadioMode' + str(SubjectDetails[0].id)])
            self.myFields.append((SubjectDetails[0].SubCode, SubjectDetails[0].SubName, SubjectDetails[0].Credits, \
                self['Check' + str(SubjectDetails[0].id)], self['RadioMode' + str(SubjectDetails[0].id)],True,\
                    'D',regEvent.AYear, regEvent.Regulation, SubjectDetails[0].id, bRow.id))

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



class RollListStatusForm(forms.Form):
    def __init__(self, Options = None, *args,**kwargs):
        super(RollListStatusForm,self).__init__(*args, **kwargs)
        self.myFields=[]
        aYearChoices = [(0,'--Select AYear--')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        departments = ProgrammeModel.objects.filter(ProgrammeType='UG')
        deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        deptChoices = [(0,'--Select Dept--')] + deptChoices
        bYearChoices = [(0,'--Select BYear--'),(1,1), (2, 2),(3, 3),(4, 4)]
        self.fields['aYear'] =  forms.IntegerField(label='Select AYear', widget=forms.Select(choices=aYearChoices))
        self.fields['bYear'] = forms.IntegerField(label='Select BYear', widget=forms.Select(choices=bYearChoices))
        self.fields['dept'] = forms.CharField(label='Select Department', widget=forms.Select(choices=deptChoices))
        for row in range(len(Options)):
            self.myFields.append((Options[row][0],Options[row][1],Options[row][2],Options[row][3]))


class FacultyUploadForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(FacultyUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField()


class FacultyInfoUpdateForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(FacultyInfoUpdateForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + str(Options[fi][0])] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+str(Options[fi][0])].initial = False  
            self.checkFields.append(self['Check' + str(Options[fi][0])])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3], self['Check' + str(Options[fi][0])]))

  


class FacultyDeletionForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(FacultyDeletionForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + str(Options[fi][0])] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+str(Options[fi][0])].initial = False  
            self.checkFields.append(self['Check' + str(Options[fi][0])])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3], self['Check' + str(Options[fi][0])]))


  
class FacultyAssignmentForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(FacultyAssignmentForm,self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Status=1)
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
            subjects = Subjects.objects.filter(RegEventId=currentRegEventId)
            subjects = [(sub['id'],sub['SubCode']) for sub in subjects]
            subjects.sort(itemgetter(0))
            subjects = [(0,'--Select Subjects--')] + subjects
            self.fields['Subjects'] = forms.CharField(label='Subjects', widget = forms.Select(choices=subjects,\
                 attrs={'onchange':'submit();'}))  
            if('Subjects' in self.data and self.data['Subjects']!='--Select Subjects--'):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                studentMakeups = StudentMakeups.objects.filter(RegNo=self.data['RegNo'], BYear=byear, BSem=bsem)
                for mk in studentMakeups:
                    already_registered = StudentRegistrations_Staging.objects.filter(RegNo=self.data['RegNo'], sub_id=mk.sub_id, \
                        RegEventId=currentRegEventId)
                    if len(already_registered) != 0:
                        self.fields['Check' + str(mk.sub_id)] = forms.BooleanField(required=False, \
                        widget=CheckboxInput(attrs={'checked':True}))
                    else:
                        self.fields['Check' + str(mk.sub_id)] = forms.BooleanField(required=False, \
                        widget=CheckboxInput())
                    if(mk.Grade == 'I'):
                        self.fields['RadioMode' + str(mk.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                    elif mk.Grade == 'F':
                        self.fields['RadioMode' + str(mk.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(attrs={'checked': True}), choices=[('0', 'Exam Mode')])
                    elif mk.Grade == 'X':
                        self.fields['RadioMode' + str(mk.sub_id)] = forms.ChoiceField(required=False, \
                            widget=RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode'),('0', 'Exam Mode')])
                    self.checkFields.append(self['Check' + str(mk.sub_id)])
                    self.radioFields.append(self['RadioMode' + str(mk.sub_id)])
                    self.myFields.append((mk.SubCode, mk.SubName, mk.Credits, self['Check' + str(mk.sub_id)],\
                        self['RadioMode' + str(mk.sub_id)],'M', mk.OfferedYear,mk.Regulation, mk.sub_id))

class UploadSectionInfoForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(UploadSectionInfoForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField()
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ \
            str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]), depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        #attrs={'onchange':"submit();"}
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

class RollListFeeUploadForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(RollListFeeUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField()
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation, row.id) for row in self.regIDs]
        myChoices = [(option[7], depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        #attrs={'onchange':"submit();"}
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))

class RollListFinalizeForm(forms.Form):
    def __init__(self,  *args,**kwargs):
        super(RollListFinalizeForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1)
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation, row.id) for row in self.regIDs]
        myChoices = [(option[7], depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))

class NotRegisteredStatusForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(NotRegisteredStatusForm,self).__init__(*args, **kwargs)
        self.myFields=[]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1)
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation, row.id) for row in self.regIDs]
        myChoices = [(option[7], depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=26, widget=forms.Select(choices=myChoices))

class FacultyAssignmentForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(FacultyAssignmentForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation, row.id) for row in self.regIDs]
        myChoices = [(option[7], depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        #attrs={'onchange':"submit();"}
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, \
        widget=forms.Select(choices=myChoices))


class FacultyAssignmentStatusForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(FacultyAssignmentStatusForm,self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation, row.id) for row in regIDs]
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        regEventIDKVs = [(option[7], depts[option[4]-1]+':'+ \
                years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
                    for oIndex, option in enumerate(regIDs)]
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['regID'] = forms.CharField(label='Registration Evernt', widget = forms.Select(choices=regEventIDKVs))
      






