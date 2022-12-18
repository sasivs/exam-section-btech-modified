from django import forms
from ADAUGDB.models import BTRegistrationStatus
from BTExamStaffDB.models import BTStudentInfo
from ADAUGDB.models import BTRegulation, BTProgrammeModel
from BTco_ordinator.models import BTStudentRegistrations, BTSubjects
from ADAUGDB.validators import validate_file_extension


class StudentInfoFileUpload(forms.Form):
    file = forms.FileField(validators=[validate_file_extension])



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


class UpdateRollNumberForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UpdateRollNumberForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField(label='Upload File', validators=[validate_file_extension])



class StudentInfoStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StudentInfoStatusForm, self).__init__(*args, **kwargs)
        admnyear = BTStudentInfo.objects.all()
        admnyear = [(row.AdmissionYear,row.AdmissionYear) for row in admnyear]
        admnyear = list(set(admnyear))
        admnyearchoice = [('-- Select Admission Year --','-- Select Admission Year --')] + admnyear
        self.fields['admnyear'] = forms.CharField(label='Admission Year', widget = forms.Select(choices=admnyearchoice))



class IXGradeStudentsAddition(forms.Form):
    def __init__(self, *args, **kwargs):
        super(IXGradeStudentsAddition, self).__init__(*args, **kwargs) 
        GRADE_CHOICES = (
            ('', 'Choose Grade'),
            ('I', 'I'),
            ('X', 'X')
        )   
        regs = BTRegistrationStatus.objects.filter(Status=1)
        REG_CHOICES = [(reg.id,  reg.__str__()) for reg in regs]
        REG_CHOICES = [(0, 'Choose Registration Event')] + REG_CHOICES
        self.fields['regId'] = forms.CharField(label='Choose Registration Event', max_length=30, widget=forms.Select(choices=REG_CHOICES, attrs={'onchange':'submit();', 'required':'True'}))
        if self.data.get('regId'):
            registrations = BTStudentRegistrations.objects.filter(RegEventId=self.data.get('regId'))
            subjects = BTSubjects.objects.filter(id__in=registrations.values_list('sub_id_id', flat=True)).order_by('course__SubCode')
            SUBJECT_CHOICES = [(sub.id, sub.course.SubCode) for sub in subjects]
            SUBJECT_CHOICES = [('', 'Select Subject')] + SUBJECT_CHOICES
            self.fields['subject'] = forms.CharField(label='Select Subject', max_length=30, required=False, widget=forms.Select(choices=SUBJECT_CHOICES, attrs={'required':'True'}))
            self.fields['regd_no'] = forms.CharField(label='Registration Number', max_length=10, required=False, widget=forms.TextInput(attrs={'size':10, 'type':'number', 'required':'True', "onkeypress":"return isNumberKey(event);"}))
            self.fields['grade'] = forms.CharField(label='Select Grade', required=False, max_length=30, widget=forms.Select(choices=GRADE_CHOICES, attrs={'required':'True'}))

    
    def clean_regd_no(self):
        regId = self.cleaned_data.get('regId')
        subject = self.cleaned_data.get('subject')
        regd_no = self.cleaned_data.get('regd_no')
        if subject and regd_no:
            if not BTStudentRegistrations.objects.filter(RegEventId_id=regId, sub_id=subject, student__student__RegNo=regd_no):
                raise forms.ValidationError('Invalid Registration Number')
        return regd_no


class IXGradeStudentsStatus(forms.Form):
    def __init__(self, regs, *args, **kwargs):
        super(IXGradeStudentsStatus, self).__init__(*args, **kwargs) 
        REG_CHOICES = []
        if regs:
            REG_CHOICES = [(reg.id, reg.__str__()) for reg in regs]
        REG_CHOICES = [('', 'Choose Registration Event')] + REG_CHOICES
        self.fields['regId'] = forms.CharField(label='Choose Registration Event', widget=forms.Select(choices=REG_CHOICES, attrs={'onchange':"submit()"}))


class FacultyUploadForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(FacultyUploadForm, self).__init__(*args, **kwargs)
        self.fields['file'] = forms.FileField(validators=[validate_file_extension])


class FacultyInfoUpdateForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(FacultyInfoUpdateForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + str(Options[fi][0])] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+str(Options[fi][0])].initial = False  
            self.checkFields.append(self['Check' + str(Options[fi][0])])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3],Options[fi][4],Options[fi][5], self['Check' + str(Options[fi][0])]))


class FacultyDeletionForm(forms.Form):
    def __init__(self, Options=None, *args,**kwargs):
        super(FacultyDeletionForm, self).__init__(*args, **kwargs)
        self.myFields = []
        self.checkFields = []
        for fi in range(len(Options)):
            self.fields['Check' + str(Options[fi][0])] = forms.BooleanField(required=False, widget=forms.CheckboxInput())
            self.fields['Check'+str(Options[fi][0])].initial = False  
            self.checkFields.append(self['Check' + str(Options[fi][0])])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2],Options[fi][3],Options[fi][4],Options[fi][5], self['Check' + str(Options[fi][0])]))


