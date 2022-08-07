from django import forms
from MTsuperintendent.models import MTProgrammeModel, MTRegulation
from MTco_ordinator.models import MTStudentBacklogs, MTFacultyAssignment, MTSubjects, MTStudentRegistrations
from MTfaculty.models import MTMarks_Staging
import datetime



class CreateRegistrationEventForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(CreateRegistrationEventForm, self).__init__(*args, **kwargs)
        departments = MTProgrammeModel.objects.filter(ProgrammeType='PG')
        deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        deptChoices += [('all', 'All Departments')]
        deptChoices = [('','--Select Dept--')] + deptChoices
        mYearChoices = [('','--Select MYear--'),(1,1), (2, 2)]
        mSemChoices = [('','--Select MSem--'),(1,1),(2,2)]
        aYearChoices = [('','--Select AYear--')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        aSemChoices = [('','--Select ASem--')] + [(1,1),(2,2),(3,3)]
        aYearBox = forms.IntegerField(label='Select AYear', required=False, widget=forms.Select(choices=aYearChoices,attrs={'onchange':'submit();', 'required':'True'}))
        aSemBox = forms.IntegerField(label='Select ASem', required=False, widget=forms.Select(choices=aSemChoices, attrs={'required':'True'}))
        mYearBox = forms.IntegerField(label='Select MYear', required=False, widget=forms.Select(choices=mYearChoices,attrs={'onchange':'submit();', 'required':'True'}))
        mSemBox = forms.IntegerField(label='Select MSem', required=False, widget=forms.Select(choices=mSemChoices, attrs={'required':'True'}))
        deptBox = forms.CharField(label='Select Department', required=False, widget=forms.Select(choices=deptChoices, attrs={'required':'True'}))
        rChoices = [('','--Select Regulation--')]
        regulationBox = forms.IntegerField(label='Select Regulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))
        modeBox = forms.ChoiceField(label='Select Mode', required=False, widget=forms.RadioSelect(attrs={'required':'True'}),choices = [('R', 'Regular'),('B','Backlog'),('M','Makeup')])
        self.fields['aYear'] = aYearBox
        self.fields['aSem'] = aSemBox
        self.fields['mYear'] = mYearBox
        self.fields['mSem'] = mSemBox
        self.fields['dept'] = deptBox
        self.fields['regulation'] = regulationBox
        self.fields['mode'] = modeBox
        if self.data.get('aYear') and self.data.get('mYear'):
            regulations = MTRegulation.objects.filter(AYear=self.data.get('aYear')).filter(MYear = self.data.get('mYear'))
            backlog_course_regulations = MTStudentBacklogs.objects.filter(MYear=self.data.get('mYear'))
            backlog_course_regulations = [(regu.Regulation,regu.Regulation) for regu in backlog_course_regulations]
            regulations = [(regu.Regulation,regu.Regulation) for regu in regulations]
            regulations += backlog_course_regulations
            regulations = list(set(regulations))
            rChoices += regulations
            self.fields['regulation'] = forms.IntegerField(label='Select Regulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))



class DMYMSAYASSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DMYMSAYASSelectionForm, self).__init__(*args, **kwargs)
        departments = MTProgrammeModel.objects.filter(ProgrammeType='PG')
        deptChoices =[(rec.Dept, rec.Specialization) for rec in departments ]
        deptChoices = [(0,'--Select Dept--')] + deptChoices
        mYearChoices = [(0,'--Select MYear--'),(1,1), (2, 2)]
        mSemChoices = [(0,'--Select MSem--'),(1,1),(2,2)]
        aYearChoices = [(0,'--Select AYear--')] + [(i,i) for i in range(2015,datetime.datetime.now().year+1)]
        aSemChoices = [(0,'--Select ASem--')] + [(1,1),(2,2),(3,3)]
        aYearBox = forms.IntegerField(label='Select AYear', required=False, widget=forms.Select(choices=aYearChoices,attrs={'onchange':'submit();', 'required':'True'}))
        aSemBox = forms.IntegerField(label='Select ASem', required=False, widget=forms.Select(choices=aSemChoices))
        mYearBox = forms.IntegerField(label='Select MYear', required=False, widget=forms.Select(choices=mYearChoices,attrs={'onchange':'submit();', 'required':'True'}))
        mSemBox = forms.IntegerField(label='Select MSem', required=False, widget=forms.Select(choices=mSemChoices, attrs={'required':'True'}))
        deptBox = forms.CharField(label='Select Department', required=False, widget=forms.Select(choices=deptChoices, attrs={'required':'True'}))
        rChoices = [(0,'--Select Regulation--')]
        statusBox = forms.ChoiceField(label='Enable/Disable', required=False, widget=forms.RadioSelect(), choices=[(0, 'Disable'), (1, 'Enable')])
        rollBox = forms.ChoiceField(label='RollList Status', required=False, widget=forms.RadioSelect(), choices=[(0, 'Disable'), (1, 'Enable')])
        regBox = forms.ChoiceField(label='Registration Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        marksBox = forms.ChoiceField(label='Marks Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        gradesBox = forms.ChoiceField(label='Grades Status', required=False, widget=forms.RadioSelect(attrs={'required':'True'}), choices=[(0, 'Disable'), (1, 'Enable')])
        modeBox = forms.ChoiceField(label='Regular/Backlog', required=False, widget=forms.RadioSelect(attrs={'required':'True'}),choices = [('R', 'Regular'),('B','Backlog'),('M','Makeup')] )
        regulationBox = forms.IntegerField(label='Select Regulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))
        self.fields['aYear'] = aYearBox
        self.fields['aSem'] = aSemBox
        self.fields['mYear'] = mYearBox
        self.fields['mSem'] = mSemBox
        self.fields['dept'] = deptBox
        self.fields['regulation'] = regulationBox
        self.fields['status'] = statusBox
        self.fields['roll-status'] = rollBox
        self.fields['reg-status'] = regBox
        self.fields['marks-status'] = marksBox
        self.fields['grades-status'] = gradesBox
        self.fields['mode'] = modeBox
        if 'aYear' in self.data and 'mYear' in self.data and self.data['aYear']!='' and \
            self.data['mYear']!='' and self.data['aYear']!='0' and \
            self.data['mYear']!='0':
            regulations = MTRegulation.objects.filter(AYear=self.data.get('aYear')).filter(MYear = self.data.get('mYear'))
            backlog_course_regulations = MTStudentBacklogs.objects.filter(MYear=self.data.get('mYear'))
            backlog_course_regulations = [(regu.Regulation,regu.Regulation) for regu in backlog_course_regulations]
            regulations = [(regu.Regulation,regu.Regulation) for regu in regulations]
            regulations += backlog_course_regulations
            regulations = list(set(regulations))
            rChoices += regulations
            self.fields['regulation'] = forms.IntegerField(label='Select MTRegulation', required=False, widget=forms.Select(choices=rChoices, attrs={'required':'True'}))


class GradeChallengeForm(forms.Form):
    def __init__(self, co_ordinator, *args, **kwargs):
        super(GradeChallengeForm, self).__init__(*args, **kwargs)
        faculty = MTFacultyAssignment.objects.filter(Faculty__Dept=co_ordinator.Dept, RegEventId__MYear=co_ordinator.MYear, RegEventId__Status=1)
        # regIDs = MTRegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Dept, MYear=faculty.MYear)
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
            subject = MTSubjects.objects.get(id=self.data.get('subject'))
            self.subject = subject
            EXAM_TYPE_CHOICES += subject.MarkDistribution.distributions()
            self.fields['exam-type'] = forms.ChoiceField(label='Choose Exam Type', widget=forms.Select(choices=EXAM_TYPE_CHOICES))
            self.fields['mark'] = forms.CharField(label='Enter Marks', widget=forms.TextInput(attrs={'type':'number'}))
        elif self.data.get('regID') and self.data.get('subject'):
            marks_list = MTMarks_Staging.objects.filter(Registration__RegEventId=self.data.get('regID'), Registration__sub_id=self.data.get('subject')).order_by('Registration__RegNo')
            ROLL_CHOICES += [(mark.id, mark.Registration.RegNo) for mark in marks_list]
            self.fields['regd_no'] = forms.ChoiceField(label='Choose Roll Number', widget=forms.Select(choices=ROLL_CHOICES, attrs={'onchange':"submit()"}))
        elif self.data.get('regID'):
            student_registrations = MTStudentRegistrations.objects.filter(RegEventId=self.data.get('regID'))
            self.regs = student_registrations
            subjects = MTSubjects.objects.filter(id__in=student_registrations.values_list('sub_id', flat=True))
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
