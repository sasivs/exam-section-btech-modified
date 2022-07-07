from django import forms
from django.contrib.auth.models import Group
from superintendent.models import HOD
from SupExamDBRegistrations.models import FacultyInfo
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




