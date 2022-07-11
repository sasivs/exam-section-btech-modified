from django import forms
from superintendent.models import RegistrationStatus
from co_ordinator.models import StudentRegistrations, Subjects


class StudentInfoFileUpload(forms.Form):
    file = forms.FileField()



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
        self.fields['file'] = forms.FileField(label='Upload File')


class IXGradeStudentsAddition(forms.Form):
    def __init__(self, *args, **kwargs):
        super(IXGradeStudentsAddition, self).__init__(*args, **kwargs) 
        GRADE_CHOICES = (
            ('', 'Choose Grade'),
            ('I', 'I'),
            ('X', 'X')
        )   
        regs = RegistrationStatus.objects.filter(Status=1)
        REG_CHOICES = [(reg.id, reg.__str__()) for reg in regs]
        REG_CHOICES = [('', 'Choose Registration Event')] + REG_CHOICES
        self.fields['regId'] = forms.CharField(label='Choose Registration Event', widget=forms.Select(choices=REG_CHOICES, attrs={'onchange':"submit()"}))
        if self.data.get('regId'):
            registrations = StudentRegistrations.objects.filter(RegEventId=self.data.get('regId'))
            subjects = Subjects.objects.filter(id__in=registrations.values_list('sub_id', flat=True))
            SUBJECT_CHOICES = [(sub.id, sub.SubCode) for sub in subjects]
            SUBJECT_CHOICES = [('', 'Select Subject')] + SUBJECT_CHOICES
            self.fields['subject'] = forms.ChoiceField(label='Select Subject', widget=forms.Select(choices=SUBJECT_CHOICES))
            self.fields['regd_no'] = forms.CharField(label='Registration Number', max_length=10, widget=forms.TextInput(attrs={'size':10, 'type':'number'}))
            self.fields['grade'] = forms.ChoiceField(label='Select Grade', widget=forms.Select(choices=GRADE_CHOICES))

    
    def clean_regd_no(self):
        regId = self.cleaned_data.get('regId')
        subject = self.cleaned_data.get('subject')
        regd_no = self.cleaned_data.get('regd_no')
        if not StudentRegistrations.objects.filter(RegEventId=regId, sub_id=subject, RegNo=regd_no):
            raise forms.ValidationError('Invalid Registration Number')
        return regd_no


class IXGradeStudentsStatus(forms.Form):
    def __init__(self, *args, **kwargs):
        super(IXGradeStudentsStatus, self).__init__(*args, **kwargs) 
        regs = RegistrationStatus.objects.filter(Status=1)
        REG_CHOICES = [(reg.id, reg.__str__()) for reg in regs]
        REG_CHOICES = [('', 'Choose Registration Event')] + REG_CHOICES
        self.fields['regId'] = forms.CharField(label='Choose Registration Event', widget=forms.Select(choices=REG_CHOICES, attrs={'onchange':"submit()"}))


