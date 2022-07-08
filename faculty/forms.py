from django import forms 
from SupExamDBRegistrations.models import GradePoints, StudentRegistrations, RollLists, Subjects
from faculty.models import GradesThreshold


class AttendanceShoratgeUploadForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(AttendanceShoratgeUploadForm, self).__init__(*args, **kwargs)
        myChoices=[]
        for sub in Option:
            myChoices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id)+':'+str(sub.Section),sub.RegEventId.__str__()+','+\
                str(sub.Subject.SubCode)+', '+str(sub.Section))]

        myChoices = [('--Select Subject--','--Select Subject--')]+myChoices
        self.fields['Subjects'] = forms.CharField(label='Choose Subject', \
            max_length=26, widget=forms.Select(choices=myChoices))

class AttendanceShoratgeStatusForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(AttendanceShoratgeStatusForm, self).__init__(*args, **kwargs)
        myChoices=[]
        for sub in Option:
            myChoices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id)+':'+str(sub.Section),sub.RegEventId.__str__()+','+\
                str(sub.Subject.SubCode)+', '+str(sub.Section))]
        myChoices = [('--Select Subject--','--Select Subject--')]+myChoices
        self.fields['Subjects'] = forms.CharField(label='Choose Subject', \
            max_length=26, widget=forms.Select(choices=myChoices))

class GradeThresholdForm(forms.Form):
    def __init__(self, faculty_subject, *args,**kwargs):
        super(GradeThresholdForm, self).__init__(*args, **kwargs)
        grades = GradePoints.objects.filter(Regulation=faculty_subject.RegEventId.Regulation)
        prev_thresholds = GradesThreshold.objects.filter(subject=faculty_subject.Subject, RegEventId=faculty_subject.RegEventId)
        self.fields['uniform_grading'] = forms.BooleanField(label='Uniform Grading', widget=forms.CheckboxInput(attrs={'onchange':"submit()"}), initial=True)
        # if prev_thresholds:
        #     self.fields['uniform_grading'].initial = prev_thresholds.first().uniform_grading
        # if self.fields['uniform_grading'].initial:
        #     for grade in grades:
        #         self.fields[grade.id] = forms.IntegerField(label=grade.Grade, widget=forms.TextInput(attrs={'type':'number', 'max':100}))
        #         if prev_thresholds.filter(Grade=grade):
        #             self.fields[grade.id].initial = prev_thresholds.filter(Grade=grade).first().Threshold_Mark
        # else:
        #     student_registrations = StudentRegistrations.objects.filter(RegEventId=faculty_subject.RegEventId.id, sub_id=faculty_subject.Subject.id)
        #     sections = RollLists.objects.filter(RegEventId=faculty_subject.RegEventId, regd_no__in=student_registrations.values_list('regd_no', flat=True)).values_list('Section', flat=True).distinct()
        #     for section in sections:
        #         for grade in grades:
        #             self.fields[str(grade.id)+'_'+str(section)] = forms.IntegerField(label='Section-'+str(section)+' Grade-'+str(grade.Grade), \
        #                 widget=forms.TextInput(attrs={'type':'number', 'max':100}))
        #             if prev_thresholds.filter(Grade=grade, Section=section):
        #                 self.fields[str(grade.id)+'_'+str(section)].initial = prev_thresholds.filter(Grade=grade, Section=section).first().Threshold_Mark

        if 'uniform_grading' in self.data.keys():
            if self.data.get('uniform_grading')==True:
                for grade in grades:
                    self.fields[grade.id] = forms.IntegerField(label=grade.Grade, widget=forms.TextInput(attrs={'type':'number', 'max':100}))
                if prev_thresholds and prev_thresholds.first().unifom_grading == self.data.get('uniform_grading'):
                    for grade in grades:
                        if prev_thresholds.filter(Grade=grade):
                            self.fields[grade.id].initial = prev_thresholds.filter(Grade=grade).first().Threshold_Mark
            elif self.data.get('uniform_grading')==False:
                student_registrations = StudentRegistrations.objects.filter(RegEventId=faculty_subject.RegEventId.id, sub_id=faculty_subject.Subject.id)
                sections = RollLists.objects.filter(RegEventId=faculty_subject.RegEventId, regd_no__in=student_registrations.values_list('regd_no', flat=True)).values_list('Section', flat=True).distinct()
                for section in sections:
                    for grade in grades:
                        self.fields[str(grade.id)+'_'+str(section)] = forms.IntegerField(label='Section-'+str(section)+' Grade-'+str(grade.Grade), \
                            widget=forms.TextInput(attrs={'type':'number', 'max':100}))
                if prev_thresholds and prev_thresholds.first().unifom_grading == self.data.get('uniform_grading'):
                    for section in sections:
                        for grade in grades:
                            if prev_thresholds.filter(Grade=grade, Section=section):
                                self.fields[str(grade.id)+'_'+str(section)].initial = prev_thresholds.filter(Grade=grade, Section=section).first().Threshold_Mark
        else:
            if prev_thresholds:
                self.fields['uniform_grading'].initial = prev_thresholds.first().uniform_grading
            if self.fields['uniform_grading'].initial:
                for grade in grades:
                    self.fields[grade.id] = forms.IntegerField(label=grade.Grade, widget=forms.TextInput(attrs={'type':'number', 'max':100}))
                    if prev_thresholds.filter(Grade=grade):
                        self.fields[grade.id].initial = prev_thresholds.filter(Grade=grade).first().Threshold_Mark
            else:
                student_registrations = StudentRegistrations.objects.filter(RegEventId=faculty_subject.RegEventId.id, sub_id=faculty_subject.Subject.id)
                sections = RollLists.objects.filter(RegEventId=faculty_subject.RegEventId, regd_no__in=student_registrations.values_list('regd_no', flat=True)).values_list('Section', flat=True).distinct()
                for section in sections:
                    for grade in grades:
                        self.fields[str(grade.id)+'_'+str(section)] = forms.IntegerField(label='Section-'+str(section)+' Grade-'+str(grade.Grade), \
                            widget=forms.TextInput(attrs={'type':'number', 'max':100}))
                        if prev_thresholds.filter(Grade=grade, Section=section):
                            self.fields[str(grade.id)+'_'+str(section)].initial = prev_thresholds.filter(Grade=grade, Section=section).first().Threshold_Mark


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
        EXAM_CHOICES = ['', '----------']
        self.fields['subject'] = forms.CharField(label='Choose Subject', max_length=26, widget=forms.Select(choices=subject_Choices, attrs={'onchange':"submit()"}))
        self.fields['exam-type'] = forms.CharField(label='Select Exam Type', max_length=26, widget=forms.Select(choices=EXAM_CHOICES))
        if self.data.get('subject'):
            subject = self.data.get('subject').split(':')[0]
            subject = Subjects.objects.get(id=subject)
            EXAM_CHOICES += subject.MarkDistribution.distributions()
            self.fields['exam-type'] = forms.CharField(label='Select Exam Type', max_length=26, widget=forms.Select(choices=EXAM_CHOICES))
            self.fields['file'] = forms.FileField()

class MarksStatusForm(forms.Form):
    def __init__(self, subjects, *args,**kwargs):
        super(MarksStatusForm, self).__init__(*args, **kwargs)
        subject_Choices=[]
        for sub in subjects:
            subject_Choices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id)+':'+str(sub.Section),sub.RegEventId.__str__()+', '+\
                str(sub.Subject.SubCode)+', '+str(sub.Section))]
        subject_Choices = [('','--Select Subject--')] + subject_Choices
        self.fields['subject'] = forms.CharField(label='Choose Subject', max_length=26, widget=forms.Select(choices=subject_Choices))

class MarksUpdateForm(forms.Form):
    def __init__(self, mark, *args,**kwargs):
        super(MarksUpdateForm, self).__init__(*args, **kwargs)
        subject = Subjects.objects.get(id=mark.Registration.sub_id)
        EXAM_CHOICES += subject.MarkDistribution.distributions()
        self.subject = subject
        self.fields['exam-type'] = forms.CharField(label='Select Exam Type', max_length=26, widget=forms.Select(choices=EXAM_CHOICES))
        self.fields['mark'] = forms.CharField(label='Update Mark', widget=forms.TextInput(attrs={'type':'number'}))
    
    def clean_mark(self):
        mark = self.cleaned_data.get('mark')
        exam_type = self.cleaned_data.get('exam-type')
        exam_inner_index = exam_type.split(',')[1]
        exam_outer_index = exam_type.split(',')[0]
        mark_dis_limit = self.subject.MarkDistribution.get_mark_limit(exam_outer_index, exam_inner_index)
        if mark > mark_dis_limit:
            raise forms.ValidationError('Entered mark is greater than the maximum marks.')
        return mark