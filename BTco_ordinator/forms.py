from django import forms 
from django.db.models import Q 
from BTco_ordinator.models import  BTStudentRegistrations_Staging
from ADAUGDB.constants import DEPARTMENTS, YEARS, SEMS
from BTco_ordinator.models import BTNotRegistered, BTSubjects_Staging, BTSubjects, BTStudentBacklogs, BTRollLists,\
    BTDroppedRegularCourses, BTStudentMakeups, BTRegularRegistrationSummary, BTBacklogRegistrationSummary, BTMakeupRegistrationSummary,\
    BTRollLists_Staging
from ADAUGDB.models import BTRegistrationStatus
from BTExamStaffDB.models import BTStudentInfo

from ADAUGDB.validators import validate_file_extension
from BTco_ordinator.models import BTStudentRegistrations
#Create your forms here


class RegistrationsEventForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(RegistrationsEventForm, self).__init__(*args, **kwargs)
        if regIDs:
            myChoices = [('','--Choose Event--')]+regIDs
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, \
            widget=forms.Select(choices=myChoices,attrs={'onchange':"submit();"}))

class SubjectsUploadForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(SubjectsUploadForm, self).__init__(*args, **kwargs)
        myChoices = [('','--Choose Event--')]
        if Options:
            myChoices +=Options
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', required=False, max_length=26, widget=forms.Select(choices=myChoices, attrs={'required':'True'}))
        self.fields['name'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['name'].initial = 'SubjectsUploadForm'


class SubjectDeletionForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(SubjectDeletionForm, self).__init__(*args, **kwargs)
        if regIDs:
            myChoices = [(row.id, row.__str__()) for row in regIDs]
        myChoices = [('','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=26, widget=forms.Select(choices=myChoices,attrs={'onchange':'submit();'}))
        self.eventBox = self['regID']
            
        if('regID' in self.data and self.data['regID']!=''):
            self.fields['regID'].initial = self.data['regID']
            currentRegEventId = BTRegistrationStatus.objects.get(id=self.data.get('regID'))
            self.myFields = []
            self.deptSubjects = BTSubjects_Staging.objects.filter(RegEventId=currentRegEventId)
            print(self.deptSubjects)
            for sub in self.deptSubjects:
                self.fields['Check' + str(sub.id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
                if('Check'+str(sub.id) in self.data.keys() and self.data['Check'+str(sub.id)]==True):
                    self.fields['Check' + str(sub.id)].initial = True
                self.myFields.append((sub.course.SubCode,sub.course.SubName,sub.course.CourseStructure.Creditable,sub.course.CourseStructure.Credits,\
                    sub.course.CourseStructure.Type,sub.course.CourseStructure.Category,sub.course.OfferedBy, sub.course.DistributionRatio, \
                        sub.course.MarkDistribution.__str__(),self['Check'+str(sub.id)], sub.id))
 

class SubjectFinalizeEventForm(forms.Form):
    def __init__(self, options, *args,**kwargs):
        super(SubjectFinalizeEventForm, self).__init__(*args, **kwargs)
        myChoices = [(row.id, row.__str__()) for row in options]
        myChoices = [('','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices))

class StudentRegistrationUpdateForm(forms.Form): 
    def __init__(self, Options=None, *args,**kwargs): 
        super(StudentRegistrationUpdateForm, self).__init__(*args, **kwargs) 
        self.myFields = [] 
        self.checkFields = [] 
        for fi in range(len(Options)): 
            subject = BTSubjects_Staging.objects.filter(SubCode=Options[fi][0], RegEventId_id=Options[fi][6]).first() 
            self.fields['Check' + str(Options[fi][0])] = forms.BooleanField(required=False, widget=forms.CheckboxInput()) 
            self.fields['Check'+str(Options[fi][0])].initial = False 
            self.checkFields.append(self['Check' + str(Options[fi][0])]) 
            self.myFields.append(Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3],Options[fi][4],Options[fi][5],
            Options[fi][6],Options[fi][7],Options[fi][8],Options[fi][9], self['Check' + str(Options[fi][0])], subject.MarkDistribution.Distribution,
            subject.RegEventId.__str__())


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
        REGID_CHOICES = [('','--Choose Event')]
        REGID_CHOICES += [(reg.id, reg.__str__()) for reg in regIDs]
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', required=False, \
            max_length=26, widget=forms.Select(choices=REGID_CHOICES, attrs={'required':'True'}))


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
        myChoices = []
        if regIDs:
            myChoices = [(reg.id, reg.__str__()) for reg in regIDs]
        myChoices = [('','--Choose Event--')]+myChoices
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
        self.regIDs = []
        if regIDs:
            self.regIDs = [(row.id, row.__str__()) for row in regIDs]
        myChoices = [('','--Choose Event--')]+self.regIDs
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, widget=forms.Select(choices=myChoices))


class BacklogRegistrationForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(BacklogRegistrationForm,self).__init__(*args, **kwargs)
        regEventIDKVs = [(row.id, row.__str__()) for row in regIDs]
        regEventIDKVs = [('','-- Select Registration Event --')] + regEventIDKVs
        self.fields['RegEvent'] = forms.CharField(label='Registration Event', widget = forms.Select(choices=regEventIDKVs,\
            attrs={'onchange':"submit();"}))
        if self.data.get('RegEvent'):
            event = BTRegistrationStatus.objects.filter(id=self.data.get('RegEvent')).first()
            
            studentBacklogs_rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id).order_by('student__RegNo')
            studentBacklogs_regnos = [(row.id, row.student.RegNo) for row in studentBacklogs_rolls]
            studentBacklogs_regnos = [('','--Select Reg Number--')] + studentBacklogs_regnos
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=studentBacklogs_regnos,\
                 attrs={'onchange':'submit();'}))  
            if self.data.get('RegNo'):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                self.selectFields = [self.fields['RegEvent'], self.fields['RegNo']]
                roll = studentBacklogs_rolls.filter(id=self.data['RegNo']).first()
                studentRegistrations = BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=roll.student.RegNo,\
                    RegEventId__AYear=event.AYear, RegEventId__Regulation=event.Regulation)
                Selection={reg.sub_id.id:reg.Mode for reg in studentRegistrations.filter(RegEventId__ASem=event.ASem)}
                studentRegularRegistrations = studentRegistrations.filter(RegEventId__ASem=event.ASem, RegEventId__Mode='R')
                dropped_subjects = studentRegistrations.filter(RegEventId__ASem=event.ASem, RegEventId__Mode='D')
                registeredBacklogs = studentRegistrations.filter(RegEventId__ASem=event.ASem, RegEventId__Mode='B')
                if event.BYear == 1:
                    studentBacklogs = BTStudentBacklogs.objects.filter(RegNo=roll.student.RegNo, BYear=event.BYear, BSem=event.BSem).\
                        exclude(AYASBYBS__startswith=event.AYear)
                    subjects = BTSubjects.objects.filter(id__in=studentBacklogs.values_list('sub_id', flat=True))
                    studentBacklogs = studentBacklogs.exclude(sub_id__in=subjects.filter(course__CourseStructure__Category__in=['OEC', 'OPC', 'DEC']))
                else:
                    studentBacklogs = BTStudentBacklogs.objects.filter(RegNo=roll.student.RegNo, BYear=event.BYear, BSem=event.BSem, Dept=event.Dept).\
                        exclude(AYASBYBS__startswith=event.AYear)
                    subjects = BTSubjects.objects.filter(id__in=studentBacklogs.values_list('sub_id', flat=True))
                    studentBacklogs = studentBacklogs.exclude(sub_id__in=subjects.filter(course__CourseStructure__Category__in=['OEC', 'OPC', 'DEC']))
                if event.ASem == 2:
                    studentBacklogs = studentBacklogs.exclude(sub_id__in=studentRegistrations.filter(RegEventId__ASem=1).values_list('sub_id_id', flat=True))
                self.addBacklogSubjects(studentBacklogs,registeredBacklogs,Selection)
                self.addRegularSubjects(studentRegularRegistrations)
                self.addDroppedRegularSubjects(dropped_subjects)
        else:
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=[], \
                attrs={'onchange':'submit();'}))
    def addBacklogSubjects(self, studentBacklogs, registeredBacklogs, Selection):
        # validBacklogs = [row.sub_id for row in queryset]
        # regBacklogsdict = {row.sub_id.id:row.id for row in registeredBacklogs}
        for bRow in studentBacklogs:
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
                self.myFields.append((bRow.SubCode, bRow.SubName, bRow.Credits, self['Check' + str(bRow.sub_id)], 
                                self['RadioMode' + str(bRow.sub_id)],bRow.sub_id in Selection.keys(),'B', bRow.OfferedYear, \
                                    bRow.Regulation, bRow.sub_id, registeredBacklogs.filter(sub_id_id=bRow.sub_id).first().id))
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
            # if row.sub_id.id not in validBacklogs:
            if not studentBacklogs.filter(sub_id=row.sub_id_id).exists():
                bRow = BTStudentBacklogs.objects.filter(RegNo=row.student.student.RegNo, sub_id=row.sub_id.id)
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

    def addRegularSubjects(self, regular_regs):
        for bRow in regular_regs:
            self.fields['Check' + str(bRow.sub_id_id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(bRow.sub_id_id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            self.checkFields.append(self['Check' + str(bRow.sub_id_id)])
            self.radioFields.append(self['RadioMode' + str(bRow.sub_id_id)])
            self.myFields.append((bRow.sub_id.course.SubCode, bRow.sub_id.course.SubName, bRow.sub_id.course.CourseStructure.Credits, \
                self['Check' + str(bRow.sub_id_id)], self['RadioMode' + str(bRow.sub_id_id)],True,\
                    'R',bRow.RegEventId.AYear, bRow.RegEventId.Regulation, bRow.sub_id_id, bRow.id))
 
    def addDroppedRegularSubjects(self, dropped_regs):
        for bRow in dropped_regs:
            self.fields['Check' + str(bRow.sub_id_id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(bRow.sub_id_id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            self.checkFields.append(self['Check' + str(bRow.sub_id_id)])
            self.radioFields.append(self['RadioMode' + str(bRow.sub_id_id)])
            self.myFields.append((bRow.sub_id.course.SubCode, bRow.sub_id.course.SubName, bRow.sub_id.course.CourseStructure.Credits, \
                self['Check' + str(bRow.sub_id_id)], self['RadioMode' + str(bRow.sub_id_id)],True,\
                    'D',bRow.RegEventId.AYear, bRow.RegEventId.Regulation, bRow.sub_id_id, bRow.id))
 

class OpenElectiveRegistrationsForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(OpenElectiveRegistrationsForm, self).__init__(*args, **kwargs)
        subjects = BTSubjects.objects.filter(RegEventId__Status=1, RegEventId__OERollListStatus=1, course__CourseStructure__Category__in=['OEC', 'OPC'])

        myChoices = [(event.RegEventId.__open_str__(), event.RegEventId.__open_str__()) for event in subjects.distinct('RegEventId')]

        # myChoices = [( 'OE'+':'+years[option[2]]+':'+ sems[option[3]]+':'+ \
        #     str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5]),'OE'+':'+\
        #         years[option[2]]+':'+ sems[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+':'+str(option[5])) \
        #             for oIndex, option in enumerate(self.regIDs)]

        myChoices = [('','--Choose Event--')]+list(set(myChoices))
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', required=False,\
            max_length=30, widget=forms.Select(choices=myChoices, attrs={'onchange': 'submit()', 'required':'True'}))
        if self.data.get('regID'):
            regid = self.data.get('regID')
            strs = regid.split(':')
            ayear = int(strs[2])
            asem = int(strs[3])
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            byear = rom2int[strs[0]]
            bsem = rom2int[strs[1]]
            regulation = float(strs[4])
            mode = strs[5]

            subjects = subjects.filter(RegEventId__AYear=ayear,RegEventId__ASem=asem,\
            RegEventId__BYear=byear,RegEventId__BSem=asem,RegEventId__Regulation=regulation,RegEventId__Mode='R',\
                RegEventId__Status=1, RegEventId__OERollListStatus=1, course__CourseStructure__Category__in=['OEC', 'OPC'])
            oe_subjects = {}
            for sub in subjects.distinct('course__SubCode'):
                oe_subjects[(sub.course.SubCode, sub.course.SubName)] = list(map(str, subjects.filter(course__SubCode=sub.course.SubCode).values_list('id', flat=True)))
            SUBJECT_CHOICES = [('', 'Choose Subject')]
            SUBJECT_CHOICES += [(','.join(value), str(key[0])+', '+str(key[1]))for key, value in oe_subjects.items()]
            self.fields['sub'] = forms.CharField(label='Subject', required=False, widget=forms.Select(choices=SUBJECT_CHOICES, attrs={'required':'True'}))

class DeptElectiveRegistrationsForm(forms.Form):
    def __init__(self,regIDs, *args,**kwargs):
        super(DeptElectiveRegistrationsForm, self).__init__(*args, **kwargs)
        myChoices=[]
        if regIDs:
            myChoices = [(row.id, row.__str__()) for row in regIDs]
        myChoices = [('','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, required=False, widget=forms.Select(choices=myChoices, attrs={'onchange': 'submit()', 'required':'True'}))
        subChoices = [('','--Select Subject--')]
        self.fields['subId'] = forms.CharField(label='Subject', required=False, widget=forms.Select(choices=subChoices, attrs={'required':'True'}))
        self.fields['file'] = forms.FileField(label='Select File', required=False, validators=[validate_file_extension])
        self.fields['file'].widget.attrs['required']='True'
        if self.data.get('regID'):
            event = regIDs.filter(id=self.data.get('regID')).first()
            if event.Mode == 'R':
                subjects = BTSubjects.objects.filter(RegEventId=event, course__CourseStructure__Category__in=['DEC'])
            elif event.Mode == 'B':
                subjects = BTSubjects.objects.filter(course__CourseStructure__Category__in=['DEC'], RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                    RegEventId__AYear=event.AYear, RegEventId__ASem=event.ASem, RegEventId__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
            elif event.Mode == 'D':
                subjects = BTSubjects.objects.filter(subject__course__CourseStructure__Category__in=['DEC'], RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                    RegEventId__AYear=event.AYear, RegEventId__ASem=event.ASem, RegEventId__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
            subjects = [(sub.id,str(sub.course.SubCode)+" "+str(sub.course.SubName)) for sub in subjects]
            subChoices += subjects
            self.fields['subId'] = forms.CharField(label='Subject', required=False, widget=forms.Select(choices=subChoices, attrs={'required':'True'}))


class DeptElectiveRegsForm(forms.Form):
    def __init__(self, regIDs,subjects=None, *args,**kwargs):
        super(DeptElectiveRegsForm, self).__init__(*args, **kwargs)
        myChoices = []
        if regIDs:
            myChoices = [(row.id, row.__str__()) for row in regIDs]
        myChoices = [('','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Registration ID', \
            max_length=30, required=False, widget=forms.Select(choices=myChoices, attrs={'onchange': 'submit()','required':'True'}))
        subChoices = [('','--Select Subject--')]
        self.fields['subId'] = forms.CharField(label='Subject', required=False, widget=forms.Select(choices=subChoices, attrs={'required':'True'}))
        if self.data.get('regID'):
            subChoices += subjects
            self.fields['subId'] = forms.CharField(label='Subject', required=False, widget=forms.Select(choices=subChoices, attrs={'required':'True'}))


class DroppedRegularRegistrationsForm(forms.Form):
    def __init__(self,regIDs, *args,**kwargs):
        super(DroppedRegularRegistrationsForm, self).__init__(*args, **kwargs)
        regEventIDKVs = []
        if regIDs:
            regEventIDKVs = [(row.id, row.__str__()) for row in regIDs]
        regEventIDKVs = [('','-- Select Registration Event --')] + regEventIDKVs
        self.fields['RegEvent'] = forms.CharField(label='Registration Evernt', widget = forms.Select(choices=regEventIDKVs,\
            attrs={'onchange':"submit();"}))
        if self.data.get('RegEvent'):
            event = BTRegistrationStatus.objects.filter(id=self.data.get('RegEvent').first())
            dropped_regno = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
            dropped_regno = [(reg.id, reg.student.RegNo) for reg in dropped_regno]  
            dropped_regno = [('','--Select Roll Number --')] + dropped_regno
            self.fields['RegNo'] = forms.CharField(label='RegNo/RollNo', widget = forms.Select(choices=dropped_regno, \
                attrs={'onchange':'submit();'}))  
            if self.data.get('RegNo'):
                #if('RollList' in self.data):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                self.selectFields = [self.fields['RegEvent'], self.fields['RegNo']]
                roll = BTRollLists_Staging.objects.filter(id=self.data['RegNo']).first()
                droppedCourses = BTDroppedRegularCourses.objects.filter(student=roll.student, RegEventId__BYear=event.BYear, RegEventId__regulation=event.Regualtion)

                studentRegistrations = BTStudentRegistrations_Staging.objects.filter(student=roll,\
                    RegEventId__AYear=event.AYear, RegEventId__ASem=event.ASem, RegEventId__Regulation=event.Regulation)

                Selection={reg.sub_id_id:reg.Mode for reg in studentRegistrations}
                studentRegularRegistrations = studentRegistrations.filter(RegEventId__Mode='R')
                studentBacklogs = studentRegistrations.filter(RegEventId__Mode='B')
                registeredDroppedCourses = studentRegistrations.filter(RegEventId__Mode='D')
                
                self.addBacklogSubjects(studentBacklogs,Selection)
                self.addRegularSubjects(studentRegularRegistrations)
                self.addDroppedRegularSubjects(droppedCourses,registeredDroppedCourses,Selection)
        else:
            self.fields['RegNo'] = forms.IntegerField(label='RegNo/RollNo', widget = forms.Select(choices=[], attrs={'onchange':'submit();'}))
    
    def addBacklogSubjects(self, backlog_regs ,Selection):
        for bRow in backlog_regs:
            if(bRow.sub_id_id in Selection.keys()):
                self.fields['Check' + str(bRow.sub_id.id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':True}))
                if(bRow.Grade == 'R'):
                    self.fields['RadioMode' + str(bRow.sub_id.id)] = forms.ChoiceField(required=False, \
                        widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                else:
                    self.fields['RadioMode' + str(bRow.sub_id.id)] = forms.ChoiceField(required=False, \
                        widget=forms.RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
                self.checkFields.append(self['Check' + str(bRow.sub_id.id)])
                self.radioFields.append(self['RadioMode' + str(bRow.sub_id.id)])
                self.myFields.append((bRow.sub_id.course.SubCode, bRow.sub_id.course.SubName, bRow.sub_id.course.CourseStructure.Credits, self['Check' + str(bRow.sub_id.id)], 
                                self['RadioMode' + str(bRow.sub_id)],bRow.sub_id_id in Selection.keys(),'B', \
                                    bRow.sub_id.RegEventId.AYear, bRow.sub_id.RegEventId.Regulation, bRow.sub_id.id, bRow.id))

    def addRegularSubjects(self, regular_regs):
        for bRow in regular_regs:
            self.fields['Check' + str(bRow.sub_id.id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(bRow.sub_id.id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            self.checkFields.append(self['Check' + str(bRow.sub_id.id)])
            self.radioFields.append(self['RadioMode' + str(bRow.sub_id.id)])
            self.myFields.append((bRow.sub_id.course.SubCode, bRow.sub_id.course.SubName, bRow.sub_id.course.CourseStructure.Credits, self['Check' + str(bRow.sub_id.id)], 
                                self['RadioMode' + str(bRow.sub_id.id)],True,'R',bRow.RegEventId.AYear, \
                                    bRow.RegEventId.Regulation, bRow.sub_id.id, bRow.id))
 
    def addDroppedRegularSubjects(self, dropped_courses, registeredDroppedCourses,Selection):
        for bRow in dropped_courses:
            self.fields['Check' + str(bRow.subject.id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(bRow.subject.id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            self.checkFields.append(self['Check' + str(bRow.subject.id)])
            self.radioFields.append(self['RadioMode' + str(bRow.subject.id)])
            if bRow.subject.id in Selection.keys():
                self.myFields.append((bRow.subject.course.SubCode, bRow.subject.course.SubName, bRow.subject.course.CourseStructure.Credits, self['Check' + str(bRow.subject.id)], 
                                self['RadioMode' + str(bRow.subject.id)],True,'D',bRow.subject.RegEventId.AYear, bRow.subject.RegEventId.Regulation,\
                                     bRow.subject.id, registeredDroppedCourses.filter(sub_id_id=bRow.subject.id).first().id))
            else:
                self.myFields.append((bRow.subject.course.SubCode, bRow.subject.course.SubName, bRow.subject.course.CourseStructure.Credits, self['Check' + str(bRow.subject.id)], 
                                self['RadioMode' + str(bRow.subject.id)],False,'D',bRow.subject.RegEventId.AYear, bRow.subject.RegEventId.Regulation, \
                                    bRow.subject.id, ''))
 

class MakeupRegistrationsForm(forms.Form):
    def __init__(self, regIDs, *args,**kwargs):
        super(MakeupRegistrationsForm,self).__init__(*args, **kwargs)
        regEventIDKVs = []
        if regIDs:
            regEventIDKVs = [(row.id, row.__str__()) for row in regIDs]
        regEventIDKVs = [('','-- Select Registration Event --')] + regEventIDKVs
        self.fields['RegEvent'] = forms.CharField(label='Registration Evernt', widget = forms.Select(choices=regEventIDKVs,\
            attrs={'onchange':"submit();"}))
        if self.data.get('RegEvent'):
            event = BTRegistrationStatus.objects.filter(id=self.data.get('RegEvent'))
            studentMakeupRolls = BTRollLists.objects.filter(RegEventId_id=event.id).values_list('student__RegNo', flat=True)
            studentMakeupRolls.sort()
            studentMakeupRolls = [(row, row) for row in studentMakeupRolls]
            studentMakeupRolls = [('','--Select Reg Number--')] + studentMakeupRolls
            self.fields['RegNo'] = forms.CharField(label='RegNo/RollNo', widget = forms.Select(choices=studentMakeupRolls,\
                 attrs={'onchange':'submit();'}))  
            if self.data.get('RegNo'):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                roll = BTRollLists_Staging.objects.filter(id=self.data.get('RegNo')).first()
                studentMakeups = BTStudentMakeups.objects.filter(RegNo=roll.student.RegNo, BYear=event.BYear, BSem=event.BSem)
                already_registered = BTStudentRegistrations_Staging.objects.filter(RegEventId_id=event.id)
                for mk in studentMakeups:
                    if already_registered.filter(student=roll, sub_id_id=mk.sub_id):
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
            regulation = float(strs[5])
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
            regulation = float(strs[5])
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
            regulation = float(strs[4])
            mode = strs[5]
            regNoChoices = BTMakeupRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, BYear=byear, Dept=dept).values('RegNo').distinct()
            regNoChoices = [(i['RegNo'], i['RegNo']) for i in regNoChoices]
            regNoChoices = [(0,'--Choose RegNo--')] + regNoChoices
            self.fields['RegNo'] = forms.IntegerField(label='Choose RegNo', widget=forms.Select(choices=regNoChoices, \
            attrs={'onchange':"submit()"}), required=False)



class FacultySubjectAssignmentForm(forms.Form):
    def __init__(self, current_user, *args,**kwargs):
        super(FacultySubjectAssignmentForm, self).__init__(*args, **kwargs)
        
        if current_user.group=='Co-ordinator' :
            valid_subjects = BTSubjects.objects.filter(course__OfferedBy=current_user.Dept, RegEventId__BYear=current_user.BYear)
            valid_regular_subjects = valid_subjects.exclude(course__CourseStructure__Category__in=['OEC', 'OPC'])
            regular_regIDs = valid_regular_subjects.filter(RegEventId__Status=1).values_list('RegEventId_id', flat=True)
            valid_oe_subjects = valid_subjects.filter(course__CourseStructure__Category__in=['OEC', 'OPC'])
            oe_regIDs = valid_oe_subjects.filter(RegEventId__Status=1).values_list('RegEventId_id', flat=True)
            active_regIDs = BTRegistrationStatus.objects.filter(Status=1, BYear=current_user.BYear).exclude(Mode='R')
            other_regular_regIDs = BTStudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_regular_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
            other_oe_regIDs = BTStudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_oe_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
            regIDs = BTRegistrationStatus.objects.filter(Q(id__in=regular_regIDs)|Q(id__in=other_regular_regIDs))
            oe_regIDs = BTRegistrationStatus.objects.filter(Q(id__in=oe_regIDs)|Q(id__in=other_oe_regIDs))
        elif current_user.group=='HOD':
            valid_subjects = BTSubjects.objects.filter(course__OfferedBy=current_user.Dept, RegEventId__BYear=1)
            valid_regular_subjects = valid_subjects.exclude(course__CourseStructure__Category__in=['OEC', 'OPC'])
            regular_regIDs = valid_regular_subjects.filter(RegEventId__Status=1).values_list('RegEventId_id', flat=True)
            valid_oe_subjects = valid_subjects.filter(course__CourseStructure__Category__in=['OEC', 'OPC'])
            oe_regIDs = valid_oe_subjects.filter(RegEventId__Status=1).values_list('RegEventId_id', flat=True)
            active_regIDs = BTRegistrationStatus.objects.filter(Status=1, BYear=1).exclude(Mode='R')
            other_regular_regIDs = BTStudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_regular_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
            other_oe_regIDs = BTStudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_oe_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
            regIDs = BTRegistrationStatus.objects.filter(Q(id__in=regular_regIDs)|Q(id__in=other_regular_regIDs))
            oe_regIDs = BTRegistrationStatus.objects.filter(Q(id__in=oe_regIDs)|Q(id__in=other_oe_regIDs))
        REGEVENT_CHOICES = [(event.id, event.__str__()) for event in regIDs]
        REGEVENT_CHOICES += list(set([(','.join(list(map(str,oe_regIDs.filter(AYear=event.AYear, ASem=event.ASem, BYear=event.BYear, BSem=event.BSem, Regulation=event.Regulation, Mode=event.Mode).values_list('id', flat=True)))),\
            'OE'+':'+event.__open_str__()) for event in oe_regIDs.distinct('AYear', 'ASem', 'BYear', 'BSem', 'Regulation', 'Mode')]))

        REGEVENT_CHOICES = [('', 'Choose Event')] + REGEVENT_CHOICES
        
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=60, required=False,\
        widget=forms.Select(choices=REGEVENT_CHOICES, attrs={'required':'True'}))

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
            rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=regEvent.id)
            not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=regEvent.AYear-1, RegEventId__BYear=regEvent.BYear, RegEventId__BSem=regEvent.BSem,\
                    Student__Regulation=regEvent.Regulation, RegEventId__Dept=regEvent.Dept, Student__in=rolllist.values_list('student', flat=True))
            REGNO_CHOICES = [('','Choose RegNo')]
            REGNO_CHOICES += [(nr.id, nr.Student.RegNo) for nr in not_registered_students]
            self.fields['regd_no'] = forms.ChoiceField(label='Choose RegNo', required=False, choices=REGNO_CHOICES, widget=forms.Select(attrs={'required':'True', 'onchange':'submit();'})) 

            if self.data.get('regd_no'):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                self.selectFields = [self.fields['regEvent'], self.fields['regd_no']]
                
                '''
                Query all the courses corresponding to the registration event and display those courses which are not registered even once.
                '''
                selected_nr_object = not_registered_students.filter(id=self.data.get('regd_no')).first()
                regNo = selected_nr_object.Student.RegNo
                not_registered_courses = BTSubjects.objects.filter(RegEventId=selected_nr_object.RegEventId).exclude(course__CourseStructure__Category__in=['OEC', 'OPC', 'DEC'])
                reg_status_objs = BTRegistrationStatus.objects.filter(AYear=regEvent.AYear, ASem=regEvent.ASem, Regulation=regEvent.Regulation)
                student_registrations = BTStudentRegistrations_Staging.objects.filter(RegEventId_id__in=reg_status_objs.values_list('id', flat=True), student__student__RegNo=regNo)
                Selection={student_registrations[i].sub_id_id:student_registrations[i].Mode for i in range(len(student_registrations))}
                student_regular_regs = student_registrations.filter(RegEventId__Mode='R').values_list('id', flat=True)
                student_backlog_regs = student_registrations.filter(RegEventId__Mode='B').values_list('id', flat=True)
                student_dropped_regs = student_registrations.filter(RegEventId__Mode='D').values_list('id', flat=True)
                registered_courses = BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=regNo, sub_id_id__in=not_registered_courses.values_list('id', flat=True))
                self.addBacklogSubjects(student_backlog_regs, Selection)
                self.addRegularSubjects(student_regular_regs, not_registered_courses)
                self.addDroppedRegularSubjects(student_dropped_regs)
                self.addNotregisteredCourses(not_registered_courses, registered_courses, Selection)
        
    def addBacklogSubjects(self, backlog_regs, Selection):
        for bRow in backlog_regs:
            if(bRow.sub_id_id in Selection.keys()):
                self.fields['Check' + str(bRow.sub_id_id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':True}))
                if(bRow.Grade == 'R'):
                    self.fields['RadioMode' + str(bRow.sub_id_id)] = forms.ChoiceField(required=False, \
                        widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                else:
                    self.fields['RadioMode' + str(bRow.sub_id_id)] = forms.ChoiceField(required=False, \
                        widget=forms.RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
                self.checkFields.append(self['Check' + str(bRow.sub_id_id)])
                self.radioFields.append(self['RadioMode' + str(bRow.sub_id_id)])
                self.myFields.append((bRow.sub_id.course.SubCode, bRow.sub_id.course.SubName, bRow.sub_id.course.CourseStructure.Credits, self['Check' + str(bRow.sub_id_id)], 
                                self['RadioMode' + str(bRow.sub_id_id)],bRow.sub_id_id in Selection.keys(),'B', \
                                    bRow.sub_id.RegEventId.AYear, bRow.sub_id.RegEventId.Regulation, bRow.sub_id_id, bRow.id))

    def addRegularSubjects(self, regular_regs, not_registered_courses):
        for bRow in regular_regs:
            self.fields['Check' + str(bRow.sub_id_id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(bRow.sub_id_id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            self.checkFields.append(self['Check' + str(bRow.sub_id_id)])
            self.radioFields.append(self['RadioMode' + str(bRow.sub_id_id)])
            if not not_registered_courses.filter(id=bRow.sub_id_id).exists():
                self.myFields.append((bRow.sub_id.course.SubCode, bRow.sub_id.course.SubName, bRow.sub_id.course.CourseStructure.Credits, self['Check' + str(bRow.sub_id_id)], 
                                    self['RadioMode' + str(bRow.sub_id_id)],True,'R',bRow.sub_id.RegEventId.AYear, \
                                        bRow.sub_id.RegEventId.Regulation, bRow.sub_id_id, bRow.id))
            else:
                self.myFields.append((bRow.sub_id.course.SubCode, bRow.sub_id.course.SubName, bRow.sub_id.course.CourseStructure.Credits, self['Check' + str(bRow.sub_id_id)], 
                                    self['RadioMode' + str(bRow.sub_id_id)],True,'NR',bRow.sub_id.RegEventId.AYear, \
                                        bRow.sub_id.RegEventId.Regulation, bRow.sub_id_id, bRow.id))
 
    def addDroppedRegularSubjects(self, dropped_regs):
        for bRow in dropped_regs:
            self.fields['Check' + str(bRow.sub_id_id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(bRow.sub_id_id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            # self.fields['RadioMode' + str(SubjectDetails[0].id)].initial = 0
            self.checkFields.append(self['Check' + str(bRow.sub_id_id)])
            self.radioFields.append(self['RadioMode' + str(bRow.sub_id_id)])
            self.myFields.append((bRow.sub_id.course.SubCode, bRow.sub_id.course.SubName, bRow.sub_id.course.CourseStructure.Credits, \
                self['Check' + str(bRow.sub_id_id)], self['RadioMode' + str(bRow.sub_id_id)],True,\
                    'D',bRow.sub_id.RegEventId.AYear, bRow.sub_id.RegEventId.Regulation, bRow.sub_id_id, bRow.id))

    def addNotregisteredCourses(self, not_registered_courses, registered_courses, Selection):
        for row in not_registered_courses:
            if not registered_courses.filter(sub_id_id=row.id).exists():
                self.fields['Check' + str(row.id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
                self.fields['RadioMode' + str(row.id)] = forms.ChoiceField(required=False, \
                        widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                self.myFields.append((row.course.SubCode, row.course.SubName, row.course.CourseStructure.Credits, self['Check' + str(row.id)], 
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

class SubjectsSelectForm(forms.Form):
    def __init__(self, excessCourses=None, event=None, *args, **kwargs):
        super(SubjectsSelectForm, self).__init__(*args, **kwargs)
        self.courses=[]
        if excessCourses:
            for course_tup in excessCourses:
                for course in course_tup[1]:
                    self.fields["Check"+str(course.id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'required':'True', 'onclick':'change_checkbox(this)', \
                        'group':course_tup[0].id, 'autocomplete':'off'}))
                    course.formField = self["Check"+str(course.id)]
                self.courses.append(course_tup)
        if event:
            self.fields['event'] = forms.CharField(widget=forms.HiddenInput())
            self.fields['event'].initial = event.id
        self.fields['name'] = forms.CharField(widget=forms.HiddenInput())
        self.fields['name'].initial = 'SubjectsSelectForm'

class MDACoursesUploadForm(forms.Form):
    def __init__(self, regIds, *args, **kwargs):
        super(MDACoursesUploadForm, self).__init__(*args, **kwargs)
        REGEVENT_CHOICES = [(event.id, event.__str__()) for event in regIds]
        REGEVENT_CHOICES = [('', 'Choose Event')] + REGEVENT_CHOICES
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', required=False, max_length=26, widget=forms.Select(choices=REGEVENT_CHOICES, attrs={'required':'True'}))
        self.fields['file'] = forms.FileField(validators=validate_file_extension)

class MDARegistrationsForm(forms.Form):
    def __init__(self, regIDs, *args, **kwargs):
        super(MDARegistrationsForm, self).__init__(*args, **kwargs)
        REGEVENT_CHOICES = [(row.id, row.__str__()) for row in regIDs]
        REGEVENT_CHOICES = [('','Choose Event')]+REGEVENT_CHOICES
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', \
            max_length=30, required=False, widget=forms.Select(choices=REGEVENT_CHOICES, attrs={'onchange': 'submit()', 'required':'True'}))
        SUBJECT_CHOICES = [('','--Select Subject--')]
        self.fields['subId'] = forms.CharField(label='Subject', required=False, widget=forms.Select(choices=SUBJECT_CHOICES, attrs={'required':'True'}))
        self.fields['file'] = forms.FileField(label='Select File', required=False, validators=[validate_file_extension])
        self.fields['file'].widget.attrs['required']='True'
        if self.data.get('regID'):
            event = regIDs.filter(id=self.data.get('regID')).first()
            if event.Mode == 'R':
                subjects = BTSubjects.objects.filter(RegEventId=event, course__CourseStructure__Category__in=['MDA'])
            elif event.Mode == 'B':
                subjects = BTSubjects.objects.filter(course__CourseStructure__Category__in=['MDA'], RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                    RegEventId__AYear=event.AYear, RegEventId__ASem=event.ASem, RegEventId__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
            elif event.Mode == 'D':
                subjects = BTSubjects.objects.filter(subject__course__CourseStructure__Category__in=['MDA'], RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                    RegEventId__AYear=event.AYear, RegEventId__ASem=event.ASem, RegEventId__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
            subjects = [(sub.id,str(sub.course.SubCode)+" "+str(sub.course.SubName)) for sub in subjects]
            SUBJECT_CHOICES += subjects
            self.fields['subId'] = forms.CharField(label='Subject', required=False, widget=forms.Select(choices=SUBJECT_CHOICES, attrs={'required':'True'}))


