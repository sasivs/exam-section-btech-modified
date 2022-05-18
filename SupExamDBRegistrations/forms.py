from email.policy import default
from operator import itemgetter
from random import choices
from shutil import SpecialFileError
from .models import NotPromoted, ProgrammeModel, RegistrationStatus, StudentRegistrations, StudentInfo, Subjects, Subjects_Staging
from django import forms 
from django.forms import CheckboxInput, RadioSelect, ValidationError
from .models import StudentBacklogs
from django.db.models import F, Q 
from django.utils.translation import gettext_lazy as _

class TestForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(TestForm, self).__init__(*args, **kwargs)
        self.myFields = []
        aYearChoices= [(i,i) for i in range(2020,2023)]
        aMonthChoices = {2020:[(i,i) for i in range(1,5)],2021:[(i,i) for i in range(5,8)], 2022:[(i,i) for i in range(8,13)]}

        self.fields['YrSelect'] = forms.IntegerField(label='Test Field',widget=forms.Select(choices=aYearChoices,attrs={'onchange':"applySelection(this.value);"}))
        myChoices = []
        if('YrSelect' in self.data):
            myChoices = aMonthChoices[int(self.data['YrSelect'])]
        self.fields['MonthSelect'] = forms.IntegerField(label='TestMonth',widget=forms.Select(choices=myChoices))

class FirstYearBacklogRegistrationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(FirstYearBacklogRegistrationForm, self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='B',BYear=1)
        num2Roman={1:'I',2:'II',3:'III',4:'IV',5:'V'}
        regEventIDKVs = [('First Year'+'-'+str(rec.AYear) + '-' + num2Roman[rec.ASem] + '-'+num2Roman[rec.BYear] + '-'+ num2Roman[rec.BSem],'First Year'+'-'+str(rec.AYear) + '-' + num2Roman[rec.ASem] + '-'+num2Roman[rec.BYear] + '-'+ num2Roman[rec.BSem]) for rec in regIDs]
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['RegEvent'] = forms.CharField(label='Registration Evernt', widget = forms.Select(choices=regEventIDKVs,attrs={'onchange':"submit();"}))
        if 'RegEvent' in self.data and self.data['RegEvent']!= '-- Select Registration Event --':
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
                studentRegistrations = studentRegistrations.filter(AYear=F('OfferedYear'))
                Selection={studentRegistrations[i].SubCode:studentRegistrations[i].Mode for i in range(len(studentRegistrations))}
                self.addRegularSubjects(studentRegistrations)
                self.addBacklogSubjects(studentBacklogs,Selection)

    def addBacklogSubjects(self, queryset,Selection):
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

class BacklogRegistrationForm(forms.Form):
    choices = [('KG', 'kg'),
        ('TN', 't'),]
    #mytest = forms.CharField(label='Sample',widget=RadioSelect(choices=choices),initial='KG',required=False)

    def __init__(self, *args,**kwargs):
        super(BacklogRegistrationForm, self).__init__(*args, **kwargs)
        print(*args)
        print(**kwargs)
        regIDs = RegistrationStatus.objects.filter(~Q(BYear=1),Status=1,Mode='B')
        deptStrs = {1:'BTE',2:'CHE',3:'CE', 4:'CSE',5:'EEE',6:'ECE',7:'ME',8:'MME',9:'Chemistry',10:'Physics'}
        num2Roman={1:'I',2:'II',3:'III',4:'IV',5:'V'}
        regEventIDKVs = [(deptStrs[rec.Dept] + '-' + str(rec.AYear) + '-' + num2Roman[rec.ASem] + '-'+num2Roman[rec.BYear] + '-'+ num2Roman[rec.BSem], deptStrs[rec.Dept] + '-' + str(rec.AYear) + '-' + num2Roman[rec.ASem] + '-'+num2Roman[rec.BYear] + '-'+ num2Roman[rec.BSem]) for rec in regIDs]
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['RegEvent'] = forms.CharField(label='Registration Evernt', widget = forms.Select(choices=regEventIDKVs,attrs={'onchange':"submit();"}))
        if 'RegEvent' in self.data and self.data['RegEvent']!= '-- Select Registration Event --':
            event = self.data.get('RegEvent')
            eventDetails = event.split('-')
            depts = {"BTE":1,"CHE":2,"CE":3,"CSE":4,"EEE":5,"ECE":6,"ME":7,"MME":8,"Chemistry":9,"Physics":10}
            romans2int = {"I":1,"II":2,"III":3,"IV":4}
            dept = depts[eventDetails[0]]
            byear = romans2int[eventDetails[3]]
            ayear = int(eventDetails[1])
            asem = romans2int[eventDetails[2]]
            bsem = romans2int[eventDetails[4]]
            studentBacklogs = StudentBacklogs.objects.filter(BYear=byear,Dept=dept).values('RegNo','RollNo').distinct()
            print(studentBacklogs)
            studentBacklogs = [(rec['RegNo'], rec['RollNo']) for rec in studentBacklogs]  
            studentBacklogs = [(0,'--Select Roll Number --')] + studentBacklogs
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=studentBacklogs, attrs={'onchange':'submit();'}))  
            if('RegNo' in self.data and self.data['RegNo']!='--Select Roll Number --'):
                #if('RollList' in self.data):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                self.selectFields= [self.fields['RegEvent'], self.fields['RegNo']]
                backlogSubjects = StudentBacklogs.objects.filter(RegNo=self.data['RegNo'])
                studentBacklogs = StudentBacklogs.objects.filter(RegNo=self.data['RegNo']).filter(BYear = byear)
                choices = [(studentBacklogs[i].SubCode, studentBacklogs[i].Grade ) for i in range(len(studentBacklogs))]
                studentRegistrations = StudentRegistrations.objects.filter(RegNo=self.data['RegNo'],AYear=ayear,ASem=asem)
                Selection={studentRegistrations[i].SubCode:studentRegistrations[i].Mode for i in range(len(studentRegistrations))}
                studentRegularRegistrations = studentRegistrations.filter(AYear= F('OfferedYear'))
                #totalSubjects = backlogSubjects|studentRegularRegistrations
                self.addRegularSubjects(studentRegularRegistrations)
                self.addBacklogSubjects(backlogSubjects,Selection,ayear)
                print(self.data)
        else:
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=[], attrs={'onchange':'submit();'}))
    def addBacklogSubjects(self, queryset,Selection,ayear):
        for bRow in queryset:
            #existingSubjects = Subjects_Staging.objects.filter(SubCode=bRow.SubCode,OfferedYear=ayear, Regulation = bRow.Regulation).values()
            existingSubjects = Subjects.objects.filter(SubCode=bRow.SubCode,OfferedYear=bRow.OfferedYear, Regulation = bRow.Regulation)
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
            self.fields['Check' + SubjectDetails[0].SubCode] = forms.BooleanField(required=False, widget=CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + SubjectDetails[0].SubCode] = forms.ChoiceField(required=False, widget=RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            self.fields['RadioMode' + SubjectDetails[0].SubCode].initial = 0
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
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3],Options[fi][4],Options[fi][5],Options[fi][6],Options[fi][7],Options[fi][8],Options[fi][9], self['Check' + str(Options[fi][0])]))

class RegistrationsUploadForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(RegistrationsUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField()
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        print(str(Options[0][4])+str(Options[0][3])+str(Options[0][2]))
        myChoices = [(oIndex, depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[5])) for oIndex, option in enumerate(Options)]
        print(myChoices)
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=20, widget=forms.Select(choices=myChoices))

class RegistrationsEventForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(RegistrationsEventForm, self).__init__(*args, **kwargs)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        sems = {1:'I',2:'II'}
        self.regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        #attrs={'onchange':"submit();"}
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, widget=forms.Select(choices=myChoices,attrs={'onchange':"submit();"}))

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

class DBYBSAYASSelectionForm(forms.Form):
    departments = ProgrammeModel.objects.filter(ProgrammeType='UG')
    deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
    deptChoices = [(0,'--Select Dept--')] + deptChoices
    bYearChoices = [(0,'--Select BYear--'),(1,1), (2, 2),(3, 3),(4, 4)]
    bSemChoices = [(0,'--Select BSem--'),(1,1),(2,2)]
    aYearChoices = [(0,'--Select AYear')] + [(i,i) for i in range(2020,2100)]
    aSemChoices = [(0,'--Select ASem')] + [(1,1),(2,2)]
    deptBox = forms.CharField(label='Select Department', widget=forms.Select(choices=deptChoices),required=False)
    bYearBox = forms.IntegerField(label='Select BYear', widget=forms.Select(choices=bYearChoices))
    bSemBox = forms.IntegerField(label='Select BSem', widget=forms.Select(choices=bSemChoices))
    aYearBox = forms.IntegerField(label='Select AYear', widget=forms.Select(choices=aYearChoices))
    aSemBox = forms.IntegerField(label='Select ASem', widget=forms.Select(choices=aSemChoices))
    statusBox = forms.ChoiceField(label='Enable/Disable', widget=RadioSelect(), choices=[(0, 'Disable'), (1, 'Enable')])
    modeBox = forms.ChoiceField(label='Regular/Backlog',widget=RadioSelect(),choices = [('R', 'Regular'),('B','Backlog')] )

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
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode) for row in self.regIDs]
        myChoices = [(depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[5]), depts[option[4]-1]+':'+ years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        #attrs={'onchange':"submit();"}
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=20, widget=forms.Select(choices=myChoices,attrs={'onchange':'submit();'}))
        self.eventBox = self['regID']
            
        if('regID' in self.data and self.data['regID']!='--Choose Event--'):
            self.fields['regID'].initial = self.data['regID']

            eventDetails = self.data['regID'].split(':')
            print(self.data['regID'])
            depts = {"BTE":1,"CHE":2,"CE":3,"CSE":4,"EEE":5,"ECE":6,"ME":7,"MME":8,"Chemistry":9,"Physics":10}
            romans2int = {"I":1,"II":2,"III":3,"IV":4}
            dept = depts[eventDetails[0]]
            byear = romans2int[eventDetails[1]]
            bsem = romans2int[eventDetails[2]]
            ayear = int(eventDetails[3])
            asem = int(eventDetails[4])
            mode = eventDetails[5]
            self.myFields = []
            self.deptSubjects = Subjects_Staging.objects.filter(OfferedYear=ayear,BYear=byear,BSem=bsem,Dept=dept)
            for sub in self.deptSubjects:
                self.fields['Check' + sub.SubCode] = forms.BooleanField(required=False, widget=CheckboxInput())
                if('Check'+sub.SubCode in self.data.keys() and self.data['Check'+sub.SubCode]==True):
                    self.fields['Check' + sub.SubCode].initial = True
                self.myFields.append((sub.SubCode,sub.SubName,sub.Creditable,sub.Credits,sub.Regulation, sub.Type,sub.Category,self['Check'+sub.SubCode]))
 
class BranchChangeForm(forms.Form):
    def __init__(self,  *args,**kwargs):
        super(BranchChangeForm, self).__init__(*args, **kwargs)
        self.fields['RegNo'] = forms.CharField(label='Registration Number',max_length=7,min_length=6)
        departments = ProgrammeModel.objects.filter(ProgrammeType='UG').filter(Q(Dept__lte=8) & Q(Dept__gte=1))
        deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        deptChoices = [(0,'--Select Dept--')] + deptChoices
        self.fields['CurrentDept'] = forms.CharField(label='CurrentDept',widget=forms.Select(choices=deptChoices))
        aYearChoices = [(0,'--Select AYear')] + [(i,i) for i in range(2020,2100)]
        self.fields['AYear'] = forms.CharField(label='AYear',widget = forms.Select(choices=aYearChoices))
        self.fields['NewDept'] = forms.CharField(label='NewDept',widget = forms.Select(choices=deptChoices))

class BranchChangeStausForm(forms.Form):
    def __init__(self,  *args,**kwargs):
        super(BranchChangeStausForm, self).__init__(*args, **kwargs)
        self.aYearChoices = [(0,'--Select AYear')] + [(i,i) for i in range(2020,2100)]
        self.fields['AYear'] = forms.CharField(label='AYear',widget = forms.Select(choices=self.aYearChoices, attrs={'onchange':'submit();'}))

#class RollNo