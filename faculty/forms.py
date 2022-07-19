from django import forms 
from co_ordinator.models import StudentRegistrations, RollLists, Subjects
from superintendent.models import GradePoints
from faculty.models import GradesThreshold
from superintendent.validators import validate_file_extension


class AttendanceShoratgeUploadForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(AttendanceShoratgeUploadForm, self).__init__(*args, **kwargs)
        myChoices=[]
        for sub in Option:
            myChoices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id)+':'+str(sub.Section),sub.RegEventId.__str__()+','+\
                str(sub.Subject.SubCode)+', '+str(sub.Section))]

        myChoices = [('','--Select Subject--')]+myChoices
        self.fields['Subjects'] = forms.CharField(label='Choose Subject', \
            max_length=26, widget=forms.Select(choices=myChoices))
        self.fields['file'] = forms.FileField(validators=[validate_file_extension])

class AttendanceShoratgeStatusForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(AttendanceShoratgeStatusForm, self).__init__(*args, **kwargs)
        myChoices=[]
        for sub in Option:
            myChoices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id)+':'+str(sub.Section),sub.RegEventId.__str__()+','+\
                str(sub.Subject.SubCode)+', '+str(sub.Section))]
        myChoices = [('','--Select Subject--')]+myChoices
        self.fields['Subjects'] = forms.CharField(label='Choose Subject', \
            max_length=26, widget=forms.Select(choices=myChoices))

class GradeThresholdForm(forms.Form):
    def __init__(self, faculty_subject, *args,**kwargs):
        super(GradeThresholdForm, self).__init__(*args, **kwargs)
        grades = GradePoints.objects.filter(Regulation=faculty_subject.RegEventId.Regulation).exclude(Grade__in=['I', 'X', 'R'])
        prev_thresholds = GradesThreshold.objects.filter(Subject=faculty_subject.Subject, RegEventId=faculty_subject.RegEventId)
        for grade in grades:
            self.fields[str(grade.id)] = forms.CharField(label=grade.Grade, required=False, widget=forms.TextInput(attrs={'type':'number', 'max':100, 'required':'True'}))
            if prev_thresholds.filter(Grade=grade):
                self.fields[str(grade.id)].widget.attrs.update({'value':prev_thresholds.filter(Grade=grade).first().Threshold_Mark})
        # self.fields['uniform_grading'] = forms.ChoiceField(label='Uniform Grading', required=False, choices=[(1,'Yes'),(0,'No')], initial=1, widget=forms.RadioSelect(attrs={'onchange':"submit()", 'required':'True'}))
        # if 'uniform_grading' in self.data.keys():
        #     if self.data.get('uniform_grading')=='1':
        #         for grade in grades:
        #             self.fields[str(grade.id)] = forms.CharField(label=grade.Grade, required=False, widget=forms.TextInput(attrs={'type':'number', 'max':100, 'required':'True'}))
        #         if prev_thresholds and prev_thresholds.first().uniform_grading == True:
        #             for grade in grades:
        #                 if prev_thresholds.filter(Grade=grade):
        #                     self.fields[str(grade.id)].widget.attrs.update({'value':prev_thresholds.filter(Grade=grade).first().Threshold_Mark})
        #     else:
        #         student_registrations = StudentRegistrations.objects.filter(RegEventId=faculty_subject.RegEventId.id, sub_id=faculty_subject.Subject.id)
        #         sections = RollLists.objects.filter(RegEventId=faculty_subject.RegEventId, student__RegNo__in=student_registrations.values_list('RegNo', flat=True)).values_list('Section', flat=True).distinct()
        #         sections = list(set(sections))
        #         sections.sort()
        #         SECTION_CHOICES = [(sec, sec) for sec in sections]
        #         SECTION_CHOICES = [('', '------')] + SECTION_CHOICES
        #         self.fields['section'] = forms.ChoiceField(label='Select Section', required=False, choices=SECTION_CHOICES, widget=forms.Select(attrs={'required':'True', 'onchange':"submit()"}))
        #         if self.data.get('section'):
        #             self.fields['section'] = forms.ChoiceField(label='Select Section', required=False, choices=SECTION_CHOICES, initial=self.data.get('section'), widget=forms.Select(attrs={'required':'True', 'onchange':"submit()"}))
        #             for grade in grades:
        #                 self.fields[self.data.get('section')+str(grade.id)] = forms.CharField(label=grade.Grade, required=False, widget=forms.TextInput(attrs={'type':'number', 'max':100, 'required':'True','value':''}))
        #             if prev_thresholds and prev_thresholds.first().uniform_grading == False:    
        #                 for grade in grades:
        #                     if prev_thresholds.filter(Grade=grade, Section=self.data.get('section')):
        #                         self.fields[self.data.get('section')+str(grade.id)].widget.attrs.update({'value':prev_thresholds.filter(Grade=grade, Section=self.data.get('section')).first().Threshold_Mark})
        # else:
        #     if prev_thresholds:
        #         if prev_thresholds.first().uniform_grading:
        #             self.fields['uniform_grading'].initial = 1
        #         else:
        #             self.fields['uniform_grading'].initial = 0
        #     if self.fields['uniform_grading'].initial==1:
        #         for grade in grades:
        #             self.fields[str(grade.id)] = forms.CharField(label=grade.Grade, required=False, widget=forms.TextInput(attrs={'type':'number', 'max':100, 'required':'True'}))
        #             if prev_thresholds.filter(Grade=grade, uniform_grading=True):
        #                 self.fields[str(grade.id)].widget.attrs.update({'value':prev_thresholds.filter(Grade=grade, uniform_grading=True).first().Threshold_Mark})

        #     else:
        #         student_registrations = StudentRegistrations.objects.filter(RegEventId=faculty_subject.RegEventId.id, sub_id=faculty_subject.Subject.id)
        #         sections = RollLists.objects.filter(RegEventId=faculty_subject.RegEventId, student__RegNo__in=student_registrations.values_list('RegNo', flat=True)).values_list('Section', flat=True).distinct()
        #         sections = list(set(sections))
        #         sections.sort()
        #         SECTION_CHOICES = [(sec, sec) for sec in sections]
        #         SECTION_CHOICES = [('', '------')] + SECTION_CHOICES
        #         self.fields['section'] = forms.ChoiceField(label='Select Section', required=False, choices=SECTION_CHOICES, widget=forms.Select(attrs={'required':'True', 'onchange':"submit()"}))
                

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
            subject_Choices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id)+':'+str(sub.Section),sub.RegEventId.__str__()+', '+str(sub.Subject.SubCode)+', '+str(sub.Section))]
        subject_Choices = [('','--Select Subject--')] + subject_Choices
        EXAM_CHOICES = [('', '----------')]
        self.fields['subject'] = forms.CharField(label='Choose Subject', max_length=26, required=False, widget=forms.Select(choices=subject_Choices, attrs={'onchange':"submit()", 'required':'True'}))
        self.fields['exam-type'] = forms.CharField(label='Select Exam Type', max_length=26, required=False, widget=forms.Select(choices=EXAM_CHOICES, attrs={'required':'True'}))
        if self.data.get('subject'):
            subject = self.data.get('subject').split(':')[0]
            subject = Subjects.objects.get(id=subject)
            EXAM_CHOICES += subject.MarkDistribution.distributions() + [('all', 'All')]
            self.fields['exam-type'] = forms.CharField(label='Select Exam Type', required=False, max_length=26, widget=forms.Select(choices=EXAM_CHOICES, attrs={'required':'True'}))
            self.fields['file'] = forms.FileField(required=False, validators=[validate_file_extension])
            self.fields['file'].widget.attrs.update({'required':'True'})

class MarksStatusForm(forms.Form):
    def __init__(self, subjects, *args,**kwargs):
        super(MarksStatusForm, self).__init__(*args, **kwargs)
        subject_Choices=[]
        if subjects:
            for sub in subjects:
                subject_Choices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id)+':'+str(sub.Section),sub.RegEventId.__str__()+', '+\
                    str(sub.Subject.SubCode)+', '+str(sub.Section))]
        subject_Choices = [('','--Select Subject--')] + subject_Choices
        self.fields['subject'] = forms.CharField(label='Choose Subject', max_length=26, widget=forms.Select(choices=subject_Choices))

class MarksUpdateForm(forms.Form):
    def __init__(self, mark, *args,**kwargs):
        super(MarksUpdateForm, self).__init__(*args, **kwargs)
        subject = Subjects.objects.get(id=mark.Registration.sub_id)
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