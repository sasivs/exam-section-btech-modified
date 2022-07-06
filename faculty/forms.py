from email.policy import default
from operator import itemgetter
from random import choices
from shutil import SpecialFileError
from SupExamDBRegistrations.models import  RegistrationStatus
from django import forms 
from django.forms import CheckboxInput, RadioSelect, ValidationError
from django.db.models import F, Q 
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
import datetime

class AttendanceShoratgeUploadForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(AttendanceShoratgeUploadForm, self).__init__(*args, **kwargs)
        myChoices=[]
        for sub in Option:
            myChoices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id),sub.RegEventId.__str__()+','+str(sub.Subject.SubCode))]

        myChoices = [('--Select Subject--','--Select Subject--')]+myChoices
        self.fields['Subjects'] = forms.CharField(label='Choose Subject', \
            max_length=26, widget=forms.Select(choices=myChoices))

class AttendanceShoratgeStatusForm(forms.Form):
    def __init__(self,Option=None , *args,**kwargs):
        super(AttendanceShoratgeStatusForm, self).__init__(*args, **kwargs)
        myChoices=[]
        for sub in Option:
            myChoices+= [(str(sub.Subject.id)+':'+str(sub.RegEventId.id),sub.RegEventId.__str__()+','+str(sub.Subject.SubCode))]
        myChoices = [('--Select Subject--','--Select Subject--')]+myChoices
        self.fields['Subjects'] = forms.CharField(label='Choose Subject', \
            max_length=26, widget=forms.Select(choices=myChoices))
