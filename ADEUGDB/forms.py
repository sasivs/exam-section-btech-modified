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



class BranchChangeForm(forms.Form):
    def __init__(self,  *args,**kwargs):
        super(BranchChangeForm, self).__init__(*args, **kwargs)
        self.fields['RegNo'] = forms.CharField(label='Registration Number',max_length=7,min_length=6)
        self.fields['RegNo'].widget.attrs['onchange'] = 'submit()'
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


class MandatoryCreditsForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(MandatoryCreditsForm, self).__init__(*args, **kwargs)
        regulation = BTRegulation.objects.all()
        regulation = [(row.Regulation, row.Regulation) for row in regulation]
        regulation = list(set(regulation))
        reguChoices = [('-- Select Regulation --','-- Select Regulation --')] +regulation
        departments = BTProgrammeModel.objects.filter(ProgrammeType='UG')
        deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        deptChoices = [('--Select Dept--','--Select Dept--')] + deptChoices
        bYearChoices = [('--Select Dept--','--Select BYear--'),(1,1), (2, 2),(3, 3),(4, 4)]
        self.fields['Regulation'] = forms.CharField(label='Regulation', widget = forms.Select(choices=reguChoices))
        self.fields['BYear'] = forms.CharField(label='BYear', widget = forms.Select(choices=bYearChoices))
        self.fields['Dept'] = forms.CharField(label='Department', widget = forms.Select(choices=deptChoices))
        self.fields['Credits'] = forms.CharField(label='Credits',max_length= 6)


class GradeChallengeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(GradeChallengeForm, self).__init__(*args, **kwargs)
        events = BTRegistrationStatus.objects.filter(Status=1)
        # regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Dept, BYear=faculty.BYear)
        regEventIDKVs = [(reg.id,reg.__str__()) for reg in events]
        regEventIDKVs = [('','-- Select Registration Event --')] + regEventIDKVs
        SUBJECT_CHOICES = [('', 'Choose Subject')]
        ROLL_CHOICES = [('', '--------')]
        EXAM_TYPE_CHOICES = [('', '--------')]
        self.fields['regID'] = forms.CharField(label='Registration Event', required=False, widget = forms.Select(choices=regEventIDKVs, attrs={'onchange':"submit()", 'required':'True'}))
        self.fields['subject'] = forms.CharField(label='Choose Subject', required=False, widget = forms.Select(choices=SUBJECT_CHOICES, attrs={'required':'True'}))
        self.fields['regd_no'] = forms.CharField(label='Choose Roll Number', required=False, widget=forms.Select(choices=ROLL_CHOICES, attrs={'required':'True'}))
        self.fields['exam-type'] = forms.CharField(label='Choose Exam Type', required=False, widget=forms.Select(choices=EXAM_TYPE_CHOICES, attrs={'required':'True'}))
        # if self.data.get('regID') and self.data.get('subject') and self.data.get('regd_no'):
        #     subject = BTSubjects.objects.get(id=self.data.get('subject'))
        #     self.subject = subject
        #     EXAM_TYPE_CHOICES += subject.MarkDistribution.distributions()
        #     self.fields['exam-type'] = forms.ChoiceField(label='Choose Exam Type', required=False, widget=forms.Select(choices=EXAM_TYPE_CHOICES, attrs={'required':'True'}))
        #     self.fields['mark'] = forms.CharField(label='Enter Marks', required=False, widget=forms.TextInput(attrs={'type':'number', 'required':'True'}))
        # elif self.data.get('regID') and self.data.get('subject'):
        #     marks_list = BTMarks_Staging.objects.filter(Registration__RegEventId=self.data.get('regID'), Registration__sub_id=self.data.get('subject')).order_by('Registration__RegNo')
        #     ROLL_CHOICES += [(mark.id, mark.Registration.RegNo) for mark in marks_list]
        #     self.fields['regd_no'] = forms.ChoiceField(label='Choose Roll Number', required=False, widget=forms.Select(choices=ROLL_CHOICES, attrs={'onchange':"submit()", 'required':'True'}))
        if self.data.get('regID'):
            student_registrations = BTStudentRegistrations.objects.filter(RegEventId=self.data.get('regID')).distinct('sub_id')
            self.regs = student_registrations
            SUBJECT_CHOICES += [(reg.sub_id.id, reg.sub_id.course.SubCode) for reg in self.regs]
            self.fields['subject'] = forms.CharField(label='Choose Subject', required=False, widget = forms.Select(choices=SUBJECT_CHOICES, attrs={'onchange':"submit()", 'required':'True'}))
            if self.data.get('subject'):
                marks_list = BTMarks_Staging.objects.filter(Registration__RegEventId=self.data.get('regID'), Registration__sub_id=self.data.get('subject')).order_by('Registration__student__student__RegNo')
                ROLL_CHOICES += [(mark.id, mark.Registration.student.student.RegNo) for mark in marks_list]
                self.fields['regd_no'] = forms.CharField(label='Choose Roll Number', required=False, widget=forms.Select(choices=ROLL_CHOICES, attrs={'onchange':"submit()", 'required':'True'}))
                if self.data.get('regd_no'):
                    subject = BTSubjects.objects.get(id=self.data.get('subject'))
                    self.subject = subject
                    EXAM_TYPE_CHOICES += subject.course.MarkDistribution.distributions()
                    self.fields['exam-type'] = forms.CharField(label='Choose Exam Type', required=False, widget=forms.Select(choices=EXAM_TYPE_CHOICES, attrs={'required':'True'}))
                    self.fields['mark'] = forms.CharField(label='Enter Marks', required=False, widget=forms.TextInput(attrs={'type':'number', 'required':'True'}))

    def clean_mark(self):
        if self.cleaned_data.get('mark'):
            mark = self.cleaned_data.get('mark')
            exam_type = self.cleaned_data.get('exam-type')
            exam_inner_index = int(exam_type.split(',')[1])
            exam_outer_index = int(exam_type.split(',')[0])
            mark_dis_limit = self.subject.course.MarkDistribution.get_mark_limit(exam_outer_index, exam_inner_index)
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

