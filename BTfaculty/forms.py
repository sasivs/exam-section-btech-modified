from django import forms 
from BTco_ordinator.models import BTStudentRegistrations, BTRollLists, BTSubjects
from ADAUGDB.models import BTGradePoints
from BTfaculty.models import BTGradesThreshold
from ADAUGDB.validators import validate_file_extension


class AttendanceShoratgeUploadForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(AttendanceShoratgeUploadForm, self).__init__(*args, **kwargs)
        myChoices=[]
        for sub in Option:
            myChoices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id)+':'+str(sub.Section),sub.RegEventId.__str__()+','+\
                str(sub.Subject.course.SubCode)+', '+str(sub.Section))]

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
                str(sub.Subject.course.SubCode)+', '+str(sub.Section))]
        myChoices = [('','--Select Subject--')]+myChoices
        self.fields['Subjects'] = forms.CharField(label='Choose Subject', \
            max_length=26, widget=forms.Select(choices=myChoices))

class GradeThresholdForm(forms.Form):
    def __init__(self, faculty_subject, *args,**kwargs):
        super(GradeThresholdForm, self).__init__(*args, **kwargs)
        subject = faculty_subject[0].Subject
        grades = BTGradePoints.objects.filter(Regulation=subject.RegEventId.Regulation).exclude(Grade__in=['I', 'X', 'R','W'])
        prev_thresholds = BTGradesThreshold.objects.filter(Subject=subject, RegEventId=faculty_subject[0].RegEventId)
        prev_thresholds_study_mode = prev_thresholds.filter(Exam_Mode=False)
        prev_thresholds_exam_mode = prev_thresholds.filter(Exam_Mode=True)
        for grade in grades:
            self.fields[str(grade.id)] = forms.CharField(label=grade.Grade, required=False, widget=forms.TextInput(attrs={'type':'number','step':'0.25', 'max':100, 'required':'True', 'class':'threshold'}))
            if prev_thresholds_study_mode.filter(Grade=grade):
                self.fields[str(grade.id)].widget.attrs.update({'value':prev_thresholds_study_mode.filter(Grade=grade).first().Threshold_Mark})
        exam_mode_grades = grades.filter(Grade__in=['P','F'])
        for grade in exam_mode_grades:
            self.fields[str('exam_mode_')+str(grade.id)] = forms.CharField(label='Exam-Mode-('+str(grade.Grade)+')', required=False, widget=forms.TextInput(attrs={'type':'number','step':'0.25', 'max':100, 'required':'True'}))
            if prev_thresholds_exam_mode.filter(Grade=grade):
                self.fields[str('exam_mode_')+str(grade.id)].widget.attrs.update({'value':prev_thresholds_exam_mode.filter(Grade=grade).first().Threshold_Mark})
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
        oe_subjects = {}
        for sub in subjects:
            if sub.Subject.course.Category not in ['OEC', 'OPC']:
                subject_Choices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id),sub.RegEventId.__str__()+', '+str(sub.Subject.course.SubCode))]
            else:
                if not oe_subjects.get((sub.Subject.course.SubCode, 'OE'+sub.RegEventId.__open_str__())):
                    oe_subjects[(sub.Subject.course.SubCode, 'OE'+sub.RegEventId.__open_str__())] = [[sub.RegEventId.id], [sub.Subject.id]]
                else:
                    oe_subjects[(sub.Subject.course.SubCode, 'OE'+sub.RegEventId.__open_str__())][0].append(sub.RegEventId.id)
                    oe_subjects[(sub.Subject.course.SubCode, 'OE'+sub.RegEventId.__open_str__())][1].append(sub.Subject.id)
        subject_Choices+= [(','.join(value[1])+':'+('OE'+','.join(value[0])),key[1]+', '+str(key[0])) for key,value in oe_subjects.items() ]
        subject_Choices = [('','--Select Subject--')] + subject_Choices
        self.fields['subject'] = forms.CharField(label='Choose Subject', max_length=26, widget=forms.Select(choices=subject_Choices))

class MarksUploadForm(forms.Form):
    def __init__(self, subjects, *args,**kwargs):
        super(MarksUploadForm, self).__init__(*args, **kwargs)
        subject_Choices=[]
        oe_subjects = {}
        for sub in subjects:
            if sub.Subject.course.Category not in ['OEC', 'OPC']:
                subject_Choices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id)+':'+str(sub.Section),sub.RegEventId.__str__()+', '+str(sub.Subject.course.SubCode)+', '+str(sub.Section))]
            else:
                if not oe_subjects.get((sub.Subject.course.SubCode, sub.Section, 'OE'+sub.RegEventId.__open_str__())):
                    oe_subjects[(sub.Subject.course.SubCode, sub.Section, 'OE'+sub.RegEventId.__open_str__())] = [[sub.RegEventId.id], [sub.Subject.id]]
                else:
                    oe_subjects[(sub.Subject.course.SubCode, sub.Section, 'OE'+sub.RegEventId.__open_str__())][0].append(sub.RegEventId.id)
                    oe_subjects[(sub.Subject.course.SubCode, sub.Section, 'OE'+sub.RegEventId.__open_str__())][1].append(sub.Subject.id)
        subject_Choices+= [(','.join(value[1])+':'+('OE'+','.join(value[0]))+':'+str(key[1]),key[2]+', '+str(key[0])+', '+str(key[1])) for key,value in oe_subjects.items() ]
        subject_Choices = [('','--Select Subject--')] + subject_Choices
        EXAM_CHOICES = [('', '----------')]
        self.fields['subject'] = forms.CharField(label='Choose Subject', max_length=26, required=False, widget=forms.Select(choices=subject_Choices, attrs={'onchange':"submit()", 'required':'True'}))
        self.fields['exam-type'] = forms.CharField(label='Select Exam Type', max_length=26, required=False, widget=forms.Select(choices=EXAM_CHOICES, attrs={'required':'True'}))
        if self.data.get('subject'):
            subject = self.data.get('subject').split(':')[0]
            subject = BTSubjects.objects.get(id=subject)
            EXAM_CHOICES += subject.course.MarkDistribution.distributions() + [('all', 'All')]
            self.fields['exam-type'] = forms.CharField(label='Select Exam Type', required=False, max_length=26, widget=forms.Select(choices=EXAM_CHOICES, attrs={'required':'True'}))
            self.fields['file'] = forms.FileField(required=False, validators=[validate_file_extension])
            self.fields['file'].widget.attrs.update({'required':'True'})

class MarksStatusForm(forms.Form):
    def __init__(self, subjects, *args,**kwargs):
        super(MarksStatusForm, self).__init__(*args, **kwargs)
        subject_Choices=[]
        oe_subjects = {}
        if subjects:
            for sub in subjects:
                if sub.Subject.course.Category not in ['OEC', 'OPC']:
                    subject_Choices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id)+':'+str(sub.Section),sub.RegEventId.__str__()+', '+\
                        str(sub.Subject.course.SubCode)+', '+str(sub.Section))]
                else:
                    if not oe_subjects.get((sub.Subject.course.SubCode, sub.Section, 'OE'+sub.RegEventId.__open_str__())):
                        oe_subjects[(sub.Subject.course.SubCode, sub.Section, 'OE'+sub.RegEventId.__open_str__())] = [[sub.RegEventId.id], [sub.Subject.id]]
                    else:
                        oe_subjects[(sub.Subject.course.SubCode, sub.Section, 'OE'+sub.RegEventId.__open_str__())][0].append(sub.RegEventId.id)
                        oe_subjects[(sub.Subject.course.SubCode, sub.Section, 'OE'+sub.RegEventId.__open_str__())][1].append(sub.Subject.id)
        subject_Choices+= [(','.join(value[1])+':'+('OE'+','.join(value[0]))+':'+str(key[1]),key[2]+', '+str(key[0])+', '+str(key[1])) for key,value in oe_subjects.items() ]        
        subject_Choices = [('','--Select Subject--')] + subject_Choices
        self.fields['subject'] = forms.CharField(label='Choose Subject', max_length=26, widget=forms.Select(choices=subject_Choices))

class MarksUpdateForm(forms.Form):
    def __init__(self, mark, *args,**kwargs):
        super(MarksUpdateForm, self).__init__(*args, **kwargs)
        subject = BTSubjects.objects.get(id=mark.Registration.sub_id_id)
        EXAM_CHOICES = [('', '----------')]
        EXAM_CHOICES += subject.course.MarkDistribution.distributions()
        self.subject = subject
        self.fields['exam-type'] = forms.CharField(label='Select Exam Type', max_length=26, widget=forms.Select(choices=EXAM_CHOICES))
        self.fields['mark'] = forms.CharField(label='Update Mark', widget=forms.TextInput(attrs={'type':'number', 'step':'0.25'}))
    
    def clean_mark(self):
        mark = self.cleaned_data.get('mark')
        exam_type = self.cleaned_data.get('exam-type')
        exam_inner_index = int(exam_type.split(',')[1])
        exam_outer_index = int(exam_type.split(',')[0])
        mark_dis_limit = self.subject.course.MarkDistribution.get_marks_limit(exam_outer_index, exam_inner_index)
        if float(mark) > mark_dis_limit:
            raise forms.ValidationError('Entered mark is greater than the maximum marks.')
        return mark