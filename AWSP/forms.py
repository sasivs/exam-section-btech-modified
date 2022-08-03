from django import forms

class UG_PGSelectForm(forms.Form):
    def __init__(self, *args,**kwargs):
        super(UG_PGSelectForm, self).__init__(*args, **kwargs)
        PROGRAMME_CHOICES = [('UG', 'B.Tech.'), ('PG', 'M.Tech')]
        self.fields['program'] = forms.ChoiceField(required=False, choices=PROGRAMME_CHOICES, widget=forms.RadioSelect(attrs={'required':'True'}))
