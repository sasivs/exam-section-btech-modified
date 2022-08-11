from django import forms 
from MTco_ordinator.models import MTStudentRegistrations, MTRollLists, MTSubjects
from MTsuperintendent.models import MTGradePoints
from MTfaculty.models import MTGradesThreshold
from MTsuperintendent.validators import validate_file_extension



class AttendanceShoratgeUploadForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(AttendanceShoratgeUploadForm, self).__init__(*args, **kwargs)
        myChoices=[]
        for sub in Option:
            myChoices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id),sub.RegEventId.__str__()+','+\
                str(sub.Subject.SubCode))]

        myChoices = [('','--Select Subject--')]+myChoices
        self.fields['Subjects'] = forms.CharField(label='Choose Subject', \
            max_length=26, widget=forms.Select(choices=myChoices))
        self.fields['file'] = forms.FileField(validators=[validate_file_extension])

class AttendanceShoratgeStatusForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(AttendanceShoratgeStatusForm, self).__init__(*args, **kwargs)
        myChoices=[]
        for sub in Option:
            myChoices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id),sub.RegEventId.__str__()+','+\
                str(sub.Subject.SubCode))]
        myChoices = [('','--Select Subject--')]+myChoices
        self.fields['Subjects'] = forms.CharField(label='Choose Subject', \
            max_length=26, widget=forms.Select(choices=myChoices))

class GradeThresholdForm(forms.Form):
    def __init__(self, faculty_subject, *args,**kwargs):
        super(GradeThresholdForm, self).__init__(*args, **kwargs)
        grades = MTGradePoints.objects.filter(Regulation=faculty_subject.RegEventId.Regulation).exclude(Grade__in=['I', 'X', 'R','W'])
        prev_thresholds = MTGradesThreshold.objects.filter(Subject=faculty_subject.Subject, RegEventId=faculty_subject.RegEventId)
        prev_thresholds_study_mode = prev_thresholds.filter(Exam_Mode=False)
        prev_thresholds_exam_mode = prev_thresholds.filter(Exam_Mode=True)
        for grade in grades:
            self.fields[str(grade.id)] = forms.CharField(label=grade.Grade, required=False, widget=forms.TextInput(attrs={'type':'number', 'max':100, 'required':'True', 'class':'threshold'}))
            if prev_thresholds_study_mode.filter(Grade=grade):
                self.fields[str(grade.id)].widget.attrs.update({'value':prev_thresholds_study_mode.filter(Grade=grade).first().Threshold_Mark})
        exam_mode_grades = grades.filter(Grade__in=['P','F'])
        for grade in exam_mode_grades:
            self.fields[str('exam_mode_')+str(grade.id)] = forms.CharField(label='Exam-Mode-('+str(grade.Grade)+')', required=False, widget=forms.TextInput(attrs={'type':'number', 'max':100, 'required':'True'}))
            if prev_thresholds_exam_mode.filter(Grade=grade):
                self.fields[str('exam_mode_')+str(grade.id)].widget.attrs.update({'value':prev_thresholds_exam_mode.filter(Grade=grade).first().Threshold_Mark})      

class GradeThresholdStatusForm(forms.Form):
    def __init__(self, subjects, *args,**kwargs):
        super(GradeThresholdStatusForm, self).__init__(*args, **kwargs)
        subject_Choices=[]
        for sub in subjects:
            subject_Choices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id),sub.RegEventId.__str__()+', '+str(sub.Subject.SubCode))]

        subject_Choices = [('','--Select Subject--')] + subject_Choices
        self.fields['subject'] = forms.CharField(label='Choose Subject', max_length=26, widget=forms.Select(choices=subject_Choices))

class MarksUploadForm(forms.Form):
    def __init__(self, subjects, *args,**kwargs):
        super(MarksUploadForm, self).__init__(*args, **kwargs)
        subject_Choices=[]
        for sub in subjects:
            subject_Choices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id),sub.RegEventId.__str__()+', '+str(sub.Subject.SubCode))]
        subject_Choices = [('','--Select Subject--')] + subject_Choices
        EXAM_CHOICES = [('', '----------')]
        self.fields['subject'] = forms.CharField(label='Choose Subject', max_length=26, required=False, widget=forms.Select(choices=subject_Choices, attrs={'onchange':"submit()", 'required':'True'}))
        self.fields['exam-type'] = forms.CharField(label='Select Exam Type', max_length=26, required=False, widget=forms.Select(choices=EXAM_CHOICES, attrs={'required':'True'}))
        if self.data.get('subject'):
            subject = self.data.get('subject').split(':')[0]
            subject = MTSubjects.objects.get(id=subject)
            EXAM_CHOICES += subject.MarkDistribution.distributions() + [('all', 'All')]
            self.fields['exam-type'] = forms.CharField(label='Select Exam Type', required=False, max_length=26, widget=forms.Select(choices=EXAM_CHOICES, attrs={'required':'True'}))
            self.fields['file'] = forms.FileField(required=False,validators=[validate_file_extension])
            self.fields['file'].widget.attrs.update({'required':'True'})

class MarksStatusForm(forms.Form):
    def __init__(self, subjects, *args,**kwargs):
        super(MarksStatusForm, self).__init__(*args, **kwargs)
        subject_Choices=[]
        for sub in subjects:
            subject_Choices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id),sub.RegEventId.__str__()+', '+\
                str(sub.Subject.SubCode))]
        subject_Choices = [('','--Select Subject--')] + subject_Choices
        self.fields['subject'] = forms.CharField(label='Choose Subject', max_length=26, widget=forms.Select(choices=subject_Choices))

class MarksUpdateForm(forms.Form):
    def __init__(self, mark, *args,**kwargs):
        super(MarksUpdateForm, self).__init__(*args, **kwargs)
        subject = MTSubjects.objects.get(id=mark.Registration.sub_id)
        EXAM_CHOICES = [('', '----------')]
        EXAM_CHOICES += subject.MarkDistribution.distributions()
        self.subject = subject
        self.fields['exam-type'] = forms.CharField(label='Select Exam Type', max_length=26, widget=forms.Select(choices=EXAM_CHOICES))
        self.fields['mark'] = forms.CharField(label='Update Mark', widget=forms.TextInput(attrs={'type':'number'}))
    
    def clean_mark(self):
        mark = self.cleaned_data.get('mark')
        exam_type = self.cleaned_data.get('exam-type')
        exam_inner_index = int(exam_type.split(',')[1])
        exam_outer_index = int(exam_type.split(',')[0])
        mark_dis_limit = self.subject.MarkDistribution.get_marks_limit(exam_outer_index, exam_inner_index)
        if int(mark) > mark_dis_limit:
            raise forms.ValidationError('Entered mark is greater than the maximum marks.')
        return mark