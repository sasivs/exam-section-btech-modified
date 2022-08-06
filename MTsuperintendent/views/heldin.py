from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from MTsuperintendent.user_access_test import is_Superintendent
from MTsuperintendent.forms import HeldInForm
from MTsuperintendent.models import MTHeldIn


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def update_heldin(request):
    if request.method == 'POST':
        form = HeldInForm(request.POST)
        if form.is_valid() and 'submit-form' in request.POST.keys():
            ayasmyms = int(form.cleaned_data.get('ayasmyms'))
            msem = ayasmyms%10
            ayasmyms = ayasmyms//10
            myear = ayasmyms%10
            ayasmyms = ayasmyms//10
            asem = ayasmyms%10
            ayasmyms = ayasmyms//10
            ayear = ayasmyms
            prev_obj = MTHeldIn.objects.filter(AYASMYMS=form.cleaned_data.get('ayasmyms')).first()
            if prev_obj:
                prev_obj.HeldInMonth = form.cleaned_data.get('held_in_month')
                prev_obj.HeldInYear = form.cleaned_data.get('held_in_year')
                prev_obj.save()
                msg = 'HeldIn object updated successfully.'
            else:
                heldin_obj = MTHeldIn(AYear=ayear, MYear=myear, ASem=asem, MSem=msem, AYASMYMS=form.cleaned_data.get('ayasmyms'))
                heldin_obj.HeldInMonth = form.cleaned_data.get('held_in_month')
                heldin_obj.HeldInYear = form.cleaned_data.get('held_in_year')
                heldin_obj.save()
                msg = 'HeldIn object created successfully.'
            return render(request, 'MTsuperintendent/HeldIn.html', {'form':form, 'msg':msg})
        elif 'submit-form' not in request.POST.keys():
            prev_obj = MTHeldIn.objects.filter(AYASMYMS=request.POST.get('ayasmyms')).first()
            if prev_obj:
                held_in_month = prev_obj.HeldInMonth
                held_in_year = prev_obj.HeldInYear
                from json import dumps
                held_in_month = dumps(held_in_month)
                return render(request, 'MTsuperintendent/HeldIn.html', {'form':form, 'month':held_in_month, 'year':held_in_year})
    else:
        form = HeldInForm()
    return render(request, 'MTsuperintendent/HeldIn.html', {'form':form})