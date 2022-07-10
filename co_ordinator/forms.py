from django import forms 
from django.db.models import Q 
from SupExamDBRegistrations.models import RegistrationStatus, StudentRegistrations, StudentRegistrations_Staging, Subjects
from SupExamDBRegistrations.constants import DEPARTMENTS, YEARS, SEMS
from co_ordinator.models import FacultyAssignment, NotRegistered
from faculty.models import Marks_Staging

#Create your forms here

class FacultySubjectAssignmentForm(forms.Form):
    def __init__(self, current_user, *args,**kwargs):
        super(FacultySubjectAssignmentForm, self).__init__(*args, **kwargs)
        self.regIDs = RegistrationStatus.objects.filter(Status=1, BYear=current_user.Dept)
        self.regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in self.regIDs]
        myChoices = [(DEPARTMENTS[option[4]-1]+':'+ YEARS[option[2]]+':'+ SEMS[option[3]]+':'+ str(option[0])+ ':'+\
            str(option[1])+':'+str(option[6])+':'+str(option[5]), DEPARTMENTS[option[4]-1]+':'+ \
                YEARS[option[2]]+':'+ SEMS[option[3]]+':'+ str(option[0])+ ':'+str(option[1])+':'+str(option[6])+\
                    ':'+str(option[5])) for oIndex, option in enumerate(self.regIDs)]
        myChoices = [('--Choose Event--','--Choose Event--')]+myChoices
        self.fields['regID'] = forms.CharField(label='Choose Registration ID', max_length=30, \
        widget=forms.Select(choices=myChoices))

class FacultyAssignmentStatusForm(forms.Form):
    def __init__(self, faculty, *args,**kwargs):
        super(FacultyAssignmentStatusForm,self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Status=1, Dept=faculty.Dept, BYear=faculty.BYear)
        regEventIDKVs = [(reg.id,reg.__str__()) for reg in regIDs]
        regEventIDKVs = [('-- Select Registration Event --','-- Select Registration Event --')] + regEventIDKVs
        self.fields['regID'] = forms.CharField(label='Registration Event', widget = forms.Select(choices=regEventIDKVs))

class GradeChallengeForm(forms.Form):
    def __init__(self, co_ordinator, *args, **kwargs):
        super(GradeChallengeForm, self).__init__(*args, **kwargs)
        faculty = FacultyAssignment.objects.filter(Faculty__Dept=co_ordinator.Dept, RegEventId__BYear=co_ordinator.BYear, RegEventId__Status=1)
        # regIDs = RegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Dept, BYear=faculty.BYear)
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
            subject = Subjects.objects.get(id=self.data.get('subject'))
            self.subject = subject
            EXAM_TYPE_CHOICES += subject.MarkDistribution.distributions()
            self.fields['exam-type'] = forms.ChoiceField(label='Choose Exam Type', widget=forms.Select(choices=EXAM_TYPE_CHOICES))
            self.fields['mark'] = forms.CharField(label='Enter Marks', widget=forms.TextInput(attrs={'type':'number'}))
        elif self.data.get('regID') and self.data.get('subject'):
            marks_list = Marks_Staging.objects.filter(Registration__RegEventId=self.data.get('regID'), Registration__sub_id=self.data.get('subject')).order_by('Registration__RegNo')
            ROLL_CHOICES += [(mark.id, mark.Registration.RegNo) for mark in marks_list]
            self.fields['regd_no'] = forms.ChoiceField(label='Choose Roll Number', widget=forms.Select(choices=ROLL_CHOICES, attrs={'onchange':"submit()"}))
        elif self.data.get('regID'):
            student_registrations = StudentRegistrations.objects.filter(RegEventId=self.data.get('regID'))
            self.regs = student_registrations
            subjects = Subjects.objects.filter(id__in=student_registrations.values_list('sub_id', flat=True))
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

class NotRegisteredRegistrationsForm(forms.Form):
    def __init__(self, co_ordinator, *args, **kwargs):
        super(NotRegisteredRegistrationsForm, self).__init__(*args, **kwargs)
        regIDs = RegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Dept, BYear=co_ordinator.BYear, Mode='R')
        REGID_CHOICES = [('', 'Choose Event')]
        REGID_CHOICES += [(reg.id, reg.__str__())for reg in regIDs]
        self.fields['regEvent'] = forms.ChoiceField(label='Choose Event', widget=forms.Select(choices=REGID_CHOICES, attrs={'onchange':"submit()"}))

        if self.data.get('regEvent'):
            regEvent = RegistrationStatus.objects.get(id=self.data.get('regEvent'))
            not_registered_objs = NotRegistered.objects.filter(RegEventId__Dept=regEvent.Dept, RegEventId__BYear=regEvent.BYear, Registered=False).order_by('Student__RegNo', '-RegEventId_id').distinct('Student__RegNo')
            REGNO_CHOICES = [('','Choose RegNo')]
            REGNO_CHOICES += [(nr_obj.id, str(nr_obj.Student.RegNo)+', '+nr_obj.RegEventId.__str__()) for nr_obj in not_registered_objs]
            self.fields['regd_no'] = forms.ChoiceField(label='Choose RegNo', widget=forms.Select(choices=REGNO_CHOICES)) 

            if self.data.get('regd_no'):
                self.myFields = []
                self.checkFields = []
                self.radioFields = []
                self.selectFields = [self.fields['regEvent'], self.fields['regd_no']]
                
                '''
                Query all the courses corresponding to the registration event and display those courses which are not registered even once.
                '''
                selected_nr_object = not_registered_objs.filter(id=self.data.get('regd_no'))
                not_registered_courses = Subjects.objects.filter(RegEventId=selected_nr_object.RegEventId).exclude(Q(Category='OEC')|Q(Category='DEC'))
                reg_status_objs = RegistrationStatus.objects.filter(AYear=regEvent.AYear, ASem=regEvent.ASem, Regulation=regEvent.Regulation)
                student_registrations = StudentRegistrations_Staging.objects.filter(RegEventId__in=reg_status_objs.values_list('id', flat=True), RegNo=self.data.get('regd_no'))
                Selection={student_registrations[i].sub_id:student_registrations[i].Mode for i in range(len(student_registrations))}
                student_regular_regs = student_registrations.filter(RegEventId__in=reg_status_objs.filter(Mode='R').values_list('id', flat=True))
                student_backlog_regs = student_registrations.filter(RegEventId__in=reg_status_objs.filter(Mode='B').values_list('id', flat=True))
                student_dropped_regs = student_registrations.filter(RegEventId__in=reg_status_objs.filter(Mode='D').values_list('id', flat=True))
                registered_courses = StudentRegistrations_Staging.objects.filter(RegNo=self.data.get('regd_no'), sub_id__in=not_registered_courses.values_list('id', flat=True))
                self.addBacklogSubjects(student_backlog_regs, Selection)
                self.addRegularSubjects(student_regular_regs)
                self.addDroppedRegularSubjects(student_dropped_regs)
                self.addNotregisteredCourses(not_registered_courses, registered_courses)
        
    def addBacklogSubjects(self, queryset,Selection):
        for bRow in queryset:
            existingSubjects = Subjects.objects.filter(id=bRow.sub_id)
            if(len(existingSubjects)!=0):
                if(bRow.sub_id in Selection.keys()):
                    subDetails = Subjects.objects.get(id=bRow.sub_id)
                    regevent = RegistrationStatus.objects.get(id=subDetails.RegEventId)
                    self.fields['Check' + str(bRow.sub_id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':True}))
                    if(bRow.Grade == 'R'):
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                    else:
                        mode = Selection[bRow.sub_id] 
                        self.fields['RadioMode' + str(bRow.sub_id)] = forms.ChoiceField(required=False, \
                            widget=forms.RadioSelect(),choices=[('1', 'Study Mode'), ('0', 'Exam Mode')])
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
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails[0].id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            self.checkFields.append(self['Check' + str(SubjectDetails[0].id)])
            self.radioFields.append(self['RadioMode' + str(SubjectDetails[0].id)])
            self.myFields.append((SubjectDetails[0].SubCode, SubjectDetails[0].SubName, SubjectDetails[0].Credits, self['Check' + str(SubjectDetails[0].id)], 
                                self['RadioMode' + str(SubjectDetails[0].id)],True,'R',regEvent.AYear, \
                                    regEvent.Regulation, SubjectDetails[0].id, bRow.id))
 
    def addDroppedRegularSubjects(self, queryset):
        for bRow in queryset:
            SubjectDetails = Subjects.objects.filter(id=bRow.sub_id)
            regEvent = RegistrationStatus.objects.get(id=SubjectDetails[0].RegEventId)
            self.fields['Check' + str(SubjectDetails[0].id)] = forms.BooleanField(required=False, \
                widget=forms.CheckboxInput(attrs={'checked': True}))
            self.fields['RadioMode' + str(SubjectDetails[0].id)] = forms.ChoiceField(required=False, \
                widget=forms.RadioSelect(attrs={'checked': True}), choices=[(1, 'Study Mode')])
            # self.fields['RadioMode' + str(SubjectDetails[0].id)].initial = 0
            self.checkFields.append(self['Check' + str(SubjectDetails[0].id)])
            self.radioFields.append(self['RadioMode' + str(SubjectDetails[0].id)])
            self.myFields.append((SubjectDetails[0].SubCode, SubjectDetails[0].SubName, SubjectDetails[0].Credits, \
                self['Check' + str(SubjectDetails[0].id)], self['RadioMode' + str(SubjectDetails[0].id)],True,\
                    'D',regEvent.AYear, regEvent.Regulation, SubjectDetails[0].id, bRow.id))

    def addNotregisteredCourses(self, queryset, registered_courses, Selection):
        for row in queryset:
            # if row.id in Selection.keys():
            #     registration = StudentRegistrations_Staging.objects.filter()
            #     self.fields['Check'+str(row.id)] = forms.BooleanField(required=False,\
            #         widget=forms.CheckboxInput(attrs={'checked':True}))
            #     self.fields['RadioMode' + str(row.id)] = forms.ChoiceField(required=False, \
            #                 widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
            #     self.myFields.append((row.SubCode, row.SubName, row.Credits, self['Check' + str(row.id)], 
            #                         self['RadioMode' + str(row.id)],row.id in Selection.keys(),'R', row.OfferedYear, \
            #                             row.Regulation, row.id))
            # else:
            if not registered_courses.filter(sub_id=row.id).exists():
                self.fields['Check' + str(row.id)] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
                self.fields['RadioMode' + str(row.id)] = forms.ChoiceField(required=False, \
                        widget=forms.RadioSelect(attrs={'checked': True}), choices=[('1', 'Study Mode')])
                self.myFields.append((row.SubCode, row.SubName, row.Credits, self['Check' + str(row.id)], 
                                self['RadioMode' + str(row.id)],row.id in Selection.keys(),'NR', row.OfferedYear, \
                                    row.Regulation, row.id, ''))
            

