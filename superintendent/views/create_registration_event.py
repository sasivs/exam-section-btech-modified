from django.contrib.auth.decorators import login_required, user_passes_test 
from superintendent.user_access_test import is_Superintendent
from django.shortcuts import render
from superintendent.models import RegistrationStatus
from superintendent.forms import DBYBSAYASSelectionForm

# Create your views here.
@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def manage_registrations(request):
    if(request.method=='POST'):
        form = DBYBSAYASSelectionForm(request.POST)
        data = {key:request.POST[key] for key in request.POST.keys()}
        if request.POST['aYear']!='' and request.POST['bYear']!='' and request.POST['aYear']!='0' and \
            request.POST['bYear']!='0' and 'regulation' in request.POST.keys() and request.POST['regulation']!='0':
            AYear = request.POST['aYear']
        else:
            form = DBYBSAYASSelectionForm(data)
            return render(request, 'superintendent/BTRegistrationStatus.html',{'form':form})

        if(request.POST['dept']!='0' and request.POST['bSem']!='0' and request.POST['aSem']!='0'):
            AYear = request.POST['aYear']
            ASem = request.POST['aSem']
            BYear = request.POST['bYear']
            BSem = request.POST['bSem']
            Dept = int(request.POST['dept'])
            Status = int(request.POST['status'])
            rollStatus = int(request.POST['roll-status'])
            regStatus = int(request.POST['reg-status'])
            marksStatus = int(request.POST['marks-status'])
            gradesStatus = int(request.POST['grades-status'])
            Mode = request.POST['mode']
            regulation = request.POST['regulation']
            rg_status = RegistrationStatus.objects.filter(AYear=AYear, ASem=ASem, BYear=BYear, BSem=BSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode)
            if(len(rg_status)==0):
                rg_status_obj = RegistrationStatus(AYear=AYear, ASem=ASem, BYear=BYear, BSem=BSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode, RollListStatus=rollStatus, RegistrationStatus=regStatus, MarksStatus=marksStatus, GradeStatus=gradesStatus, Status=Status)
                msg = f'The event {rg_status_obj.AYear}:{rg_status_obj.ASem}:{rg_status_obj.BYear}:{rg_status_obj.BSem}:\
                        {rg_status_obj.Dept}:{rg_status_obj.Regulation} has been successfully updated(Status:{rg_status_obj.Status}),  \
                        (RegistrationStatus:{rg_status_obj.RegistrationStatus}), (MarksStatus:{rg_status_obj.MarksStatus}), (GradesStatus:{rg_status_obj.GradeStatus}) \
                            for {rg_status_obj.Mode} mode.'
                rg_status_obj.save()
                
            else:
                rg_status.update(Status=Status, )
                rg_status_obj = RegistrationStatus.objects.get(AYear=AYear, ASem=ASem, BYear=BYear, BSem=BSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode, Status=Status, RegistrationStatus=regStatus, MarksStatus=marksStatus, GradeStatus=gradesStatus)
                msg = f'The event {rg_status_obj.AYear}:{rg_status_obj.ASem}:{rg_status_obj.BYear}:{rg_status_obj.BSem}:\
                    {rg_status_obj.Dept}:{rg_status_obj.Regulation} has been successfully updated(Status:{rg_status_obj.Status}),  \
                       (RegistrationStatus:{rg_status_obj.RegistrationStatus}), (MarksStatus:{rg_status_obj.MarksStatus}), (GradesStatus:{rg_status_obj.GradeStatus}) \
                        for {rg_status_obj.Mode} mode.'
            return render(request, 'superintendent/BTRegistrationStatus.html',{'form':form, 'msg':msg}) 
    else:
        form = DBYBSAYASSelectionForm()
    return render(request, 'superintendent/BTRegistrationStatus.html',{'form':form})
