from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from ADAUGDB.user_access_test import is_Associate_Dean_Exams
from ADEUGDB.forms import HeldInForm
from ADEUGDB.models import BTHeldIn


@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Exams)
def update_heldin(request):
    if request.method == 'POST':
        form = HeldInForm(request.POST)
        if form.is_valid() and 'submit-form' in request.POST.keys():
            ayasbybs = int(form.cleaned_data.get('ayasbybs'))
            bsem = ayasbybs%10
            ayasbybs = ayasbybs//10
            byear = ayasbybs%10
            ayasbybs = ayasbybs//10
            asem = ayasbybs%10
            ayasbybs = ayasbybs//10
            ayear = ayasbybs
            prev_obj = BTHeldIn.objects.filter(AYASBYBS=form.cleaned_data.get('ayasbybs')).first()
            if prev_obj:
                prev_obj.HeldInMonth = form.cleaned_data.get('held_in_month')
                prev_obj.HeldInYear = form.cleaned_data.get('held_in_year')
                prev_obj.save()
                msg = 'HeldIn object updated successfully.'
            else:
                heldin_obj = BTHeldIn(AYear=ayear, BYear=byear, ASem=asem, BSem=bsem, AYASBYBS=form.cleaned_data.get('ayasbybs'))
                heldin_obj.HeldInMonth = form.cleaned_data.get('held_in_month')
                heldin_obj.HeldInYear = form.cleaned_data.get('held_in_year')
                heldin_obj.save()
                msg = 'HeldIn object created successfully.'
            return render(request, 'ADEUGDB/HeldIn.html', {'form':form, 'msg':msg})
        elif 'submit-form' not in request.POST.keys():
            prev_obj = BTHeldIn.objects.filter(AYASBYBS=request.POST.get('ayasbybs')).first()
            if prev_obj:
                held_in_month = prev_obj.HeldInMonth
                held_in_year = prev_obj.HeldInYear
                from json import dumps
                held_in_month = dumps(held_in_month)
                return render(request, 'ADEUGDB/HeldIn.html', {'form':form, 'month':held_in_month, 'year':held_in_year})
    else:
        form = HeldInForm()
    return render(request, 'ADEUGDB/HeldIn.html', {'form':form})