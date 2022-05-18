from django.db.models.enums import Choices
from django.forms.widgets import CheckboxInput, RadioSelect
from Registrations.models import StudentMakeupBacklogs
from django import forms 
from django.forms import models 
from django.forms.fields import MultipleChoiceField
from django.core.exceptions import ValidationError
from django.forms.fields import ChoiceField
DEMO_CHOICES =(
    ("1", "Naveen"),
    ("2", "Pranav"),
    ("3", "Isha"),
    ("4", "Saloni"),
)
class SimpleForm(forms.Form):
    lucky_number = forms.MultipleChoiceField(choices=DEMO_CHOICES)

    # def clean_lucky_number(self):
    #     data = self.cleaned_data['lucky_number']
    #     if(data < 100):
    #         raise ValidationError('Enter a number between 100 to 1000')
    #     elif(data >1000):
    #         raise ValidationError('Enter a number between 100 to 1000')
    #     return(data)

class StudentIDForm(forms.Form):
    Choices = [('RegNo','RegNo'), ('RollNo','RollNo')]
    id_choice = forms.ChoiceField(choices=Choices, widget=forms.RadioSelect)
    student_id = forms.IntegerField()
    def clean_student_id(self):
        data = self.cleaned_data['student_id']
        data_choice = self.cleaned_data['id_choice']
        if(data_choice=='RollNo'):
            if( not (len(str(data))==6) or(len(str(data))==7)) :
                raise ValidationError('Roll Number must have 6 or 7 digits')
            elif(str(data).startswith('9') or str(data).startswith('0')):
                raise ValidationError('Roll Number should start with 1 to 8')
        else:
            if( not (len(str(data))==6) or(len(str(data))==7)) :
                raise ValidationError('Registration Number must have 6 or 7 digits')
            elif(not str(data).startswith('9')):
                raise ValidationError('Registration Number should start with 9')
        return(data)

class CustomModelChoiceIterator(models.ModelChoiceIterator):
    def choice(self, obj):
        return (self.field.prepare_value(obj),self.field.label_from_instance(obj), obj)

class CustomModelChoiceField(models.ModelMultipleChoiceField):
    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return CustomModelChoiceIterator(self)
    choices = property(_get_choices,  
                       MultipleChoiceField._set_choices)


class RegistrationsInsertionForm(forms.ModelForm):
    checkBoxes = CustomModelChoiceField( widget = forms.CheckboxSelectMultiple, 
                                        queryset = StudentMakeupBacklogs.objects.all() )
    
    def __init__(self,*args,**kwargs):
        self.cleaned_data['checkBoxes'].queryset = StudentMakeupBacklogs.objects.filter(RegNo=kwargs.pop('RegNo'))
        super(RegistrationsInsertionForm,self).__init__(*args,**kwargs)
        
class RegistrationForm(forms.Form):
    def __init__(self, RegNo=None, Options=None, Selection=None, *args,**kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['RegNo'] = forms.IntegerField(widget=forms.HiddenInput())
        self.fields['RegNo'].initial = RegNo 

        self.fields['Choices'] = forms.MultipleChoiceField(required = False, choices=Options, widget=forms.CheckboxSelectMultiple())
        self.fields['Choices'].initial = Selection 
        
    
class MarksForm(forms.Form):
    def __init__(self, SubCode=None, studentRegistrations=None, Selection=None,*args,**kwargs):
        super(MarksForm, self).__init__(*args, **kwargs)
        i=0
        for rec in studentRegistrations:
            self.fields['marks'+str(rec.RegNo)] =  forms.IntegerField(widget = forms.TextInput,label=str(rec.RegNo))
            self.fields['marks'+str(rec.RegNo)].initial = Selection[i]
            i+=1

class RegistrationForm1(forms.Form):
    def __init__(self, RegNo=None, Options=None, Selection=None, *args,**kwargs):
        super(RegistrationForm1, self).__init__(*args, **kwargs)
        self.fields['RegNo'] = forms.IntegerField(required=False, widget=forms.HiddenInput())
        self.fields['RegNo'].initial = RegNo 

        #self.fields['Choices'] = forms.MultipleChoiceField(choices=Options, widget=forms.CheckboxSelectMultiple())
        #self.fields['Choices'].initial = Selection 
        self.myFields = []
        #self.fields['Check']=forms.MultipleChoiceField(required=False, choices= Options, widget=forms.CheckboxSelectMultiple())
        #self.fields['Check'].initial=Selection
        self.checkFields = []
        self.radioFields = []
        for fi in range(len(Options)):
            self.fields['Check' + Options[fi][0]] = forms.BooleanField(required=False, widget=CheckboxInput())
            
            if(Options[fi][0] in Selection.keys()):
                self.fields['Check'+Options[fi][0]].initial = True 
                if(Options[fi][3] == 'R'):     
                    self.fields['RadioMode' + Options[fi][0]] = forms.ChoiceField(required=False, widget=RadioSelect(), choices=[(1, 'Study Mode')])
                    self.fields['RadioMode' + Options[fi][0]].initial = 1
                else:
                    self.fields['RadioMode' + Options[fi][0]] = forms.ChoiceField(required=False, widget=RadioSelect(), choices=[(0, 'Exam Mode'), (1, 'Study Mode')])
                    self.fields['RadioMode' + Options[fi][0]].initial = Selection[Options[fi][0]]
                
                    #self.fields['RadioMode' + Options[fi][0]].widget.attrs['disabled'] = True  
            else:
                if(Options[fi][3] == 'R'):
                    self.fields['RadioMode' + Options[fi][0]] = forms.ChoiceField(required=False, widget=RadioSelect(), choices=[(1, 'Study Mode')])     
                    self.fields['RadioMode' + Options[fi][0]].initial = 1
                    #self.fields['RadioMode' + Options[fi][0]].widget.attrs['disabled'] = True  
                else:
                    self.fields['RadioMode' + Options[fi][0]] = forms.ChoiceField(required=False, widget=RadioSelect(), choices=[(0, 'Exam Mode'), (1, 'Study Mode')])
                    self.fields['RadioMode' + Options[fi][0]].initial = 0
                     
            
            self.checkFields.append(self['Check' + Options[fi][0]])
            self.radioFields.append(self['RadioMode' + Options[fi][0]])
            self.myFields.append((Options[fi][0], Options[fi][1], Options[fi][2], self['Check' + Options[fi][0]], 
                                self['RadioMode' + Options[fi][0]]))
            #self.fields['RadioMode'+Selection[fi][1]].label = Options[fi][1]
            ''''self.fields['Check'+Options[fi][1]] = forms.MultipleChoiceField(required=False, choices= Options, widget=forms.CheckboxSelectMultiple())
            self.fields['Check'+Options[fi][1]].label = 'Y/N'
            self.fields['Check'+Options[fi][1]].initial = Selection '''
            #self.myFields.append((Options[fi][1],self['RadioMode'+Options[fi][1]], self['Check'+Options[fi][1]]))

class TestForm(forms.Form):
    a=forms.ChoiceField( widget=RadioSelect(attrs={'class':'form-check form-check-inline'}), choices=[(0, 'Exam Mode'), (1, 'Study mode')])
    b=forms.BooleanField()
    c=forms.BooleanField()
    d=forms.ChoiceField( widget=RadioSelect(), choices=[(0, 'Exam Mode'), (1, 'Study mode')])
    def __init__(self, *args,**kwargs):
        super(TestForm, self).__init__(*args, **kwargs)
        self.t = [(self['a'],self['b']),(self['c'],self['d'])]
