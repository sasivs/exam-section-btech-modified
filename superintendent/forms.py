from django import forms
from django.contrib.auth.models import Group
from superintendent.models import HOD
from SupExamDBRegistrations.models import FacultyInfo, RegistrationStatus, StudentRegistrations, Subjects
from superintendent.models import Departments

class HODAssignmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(HODAssignmentForm, self).__init__(*args, **kwargs)
        departments = Departments.objects.filter(ProgrammeName='BTech', ProgrammeType='UG')
        DEPT_CHOICES = [('', '--------')]
        HOD_CHOICES = [('', '--------')]
        USER_CHOICES = [('', '--------')]
        DEPT_CHOICES += [(dept.Dept, dept.Specilaization) for dept in departments.values_list('Dept', flat=True)]
        self.fields['dept'] = forms.CharField(label='Department', widget=forms.Select(choices=DEPT_CHOICES, attrs={'onchange':"submit()"}))
        self.fields['hod'] = forms.CharField(label='HOD', widget=forms.Select(choices=HOD_CHOICES))
        self.fields['user'] = forms.CharField(label='User', widget=forms.Select(choices=USER_CHOICES))
        if self.data.get('dept'):
            faculty= FacultyInfo.objects.filter(working=True, Dept=self.data.get('dept'))
            HOD_CHOICES += [(fac.id, fac.Name) for fac in faculty]
            self.fields['hod'] = forms.CharField(label='HOD', widget=forms.Select(choices=HOD_CHOICES))
            group = Group.objects.filter(name='HOD').first()
            assigned_users = HOD.objects.filter(RevokeDate__isnull=True).exclude(Dept=self.data.get('dept'))
            users = group.user_set.exclude(id__in=assigned_users.values_list('User', flat=True))
            self.fields['user'] = forms.CharField(label='User', widget=forms.Select(choices=USER_CHOICES))
            USER_CHOICES += [(user.id, user.username) for user in users]
            initial_hod = HOD.objects.filter(Dept=self.data.get('dept'), RevokeDate__isnull=True).first()
            if initial_hod:
                self.fields['hod'].initial = initial_hod.Faculty.id
                self.fields['user'].initial = initial_hod.User.id

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



class MarksDistributionForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(MarksDistributionForm, self).__init__(*args, **kwargs)
        self.fields['Distribution'] = forms.CharField(label='Distribution', widget=forms.Textarea(attrs={'rows':5, 'cols':10}))
        self.fields['DistributionName'] = forms.CharField(label='DistributionName', widget=forms.Textarea(attrs={'rows':5, 'cols':10}))


