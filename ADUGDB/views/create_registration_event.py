from django.contrib.auth.decorators import login_required, user_passes_test 
from BTsuperintendent.user_access_test import is_Associate_Dean
from django.shortcuts import render
from BTsuperintendent.models import BTProgrammeModel
from ADUGDB.models import BTRegistrationStatus
from ADUGDB.forms import DBYBSAYASSelectionForm, CreateRegistrationEventForm

# Create your views here.
@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean)
def create_registration_event(request):
    msg = ''
    if request.method == 'POST':
        form = CreateRegistrationEventForm(request.POST)
        if form.is_valid() and form.cleaned_data.get('dept') and form.cleaned_data.get('aSem') and form.cleaned_data.get('bSem'):
            AYear = form.cleaned_data['aYear']
            ASem = form.cleaned_data['aSem']
            BYear = form.cleaned_data['bYear']
            BSem = form.cleaned_data['bSem']
            Dept = form.cleaned_data['dept']
            Mode = form.cleaned_data['mode']
            regulation = form.cleaned_data['regulation']

            if form.cleaned_data.get('dept')!='all':
                Dept = int(Dept)
                if BTRegistrationStatus.objects.filter(AYear=AYear, ASem=ASem, BYear=BYear, BSem=BSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode).exists():
                    msg = 'Registration event already created.'
                    return render(request, 'ADUGDB/BTRegistrationStatus.html', {'form':form, 'msg':msg})
                else:
                    rg_status_obj = BTRegistrationStatus(AYear=AYear, ASem=ASem, BYear=BYear, BSem=BSem, Dept=Dept, Regulation=regulation, \
                        Mode=Mode, RollListStatus=1, RegistrationStatus=1, MarksStatus=1, OERollListStatus=1, OERegistartionStatus=1, GradeStatus=1, Status=1)
                    rg_status_obj.save()
                    msg = 'The Event {} has been created successfully'.format(rg_status_obj.__str__())
            else:
                if form.cleaned_data.get('bYear') == 1: 
                    departments = BTProgrammeModel.objects.filter(ProgrammeType='UG', Dept__in=[10,9])
                else:
                    departments = BTProgrammeModel.objects.filter(ProgrammeType='UG').exclude(Dept__in=[10,9])
                created_dept = []
                for department in departments:
                    dept = department.Dept
                    if not BTRegistrationStatus.objects.filter(AYear=AYear, ASem=ASem, BYear=BYear, BSem=BSem, Dept=dept, Regulation=regulation, \
                        Mode=Mode).exists():
                        rg_status_obj = BTRegistrationStatus(AYear=AYear, ASem=ASem, BYear=BYear, BSem=BSem, Dept=dept, Regulation=regulation, \
                            Mode=Mode, RollListStatus=1, RegistrationStatus=1, OERollListStatus=1, OERegistartionStatus=1, MarksStatus=1, GradeStatus=1, Status=1)
                        rg_status_obj.save()
                        created_dept.append(department.Specialization)
                created_dept = ','.join(created_dept)
                msg = 'The Event has been created successfully for {} departments'.format(created_dept)
    else:
        form = CreateRegistrationEventForm()
    return render(request, 'ADUGDB/BTRegistrationStatus.html', {'form':form, 'msg':msg})


@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean)
def update_manage_registrations(request):
    if(request.method=='POST'):
        form = DBYBSAYASSelectionForm(request.POST)
        data = {key:request.POST[key] for key in request.POST.keys()}
        if request.POST['aYear']!='' and request.POST['bYear']!='' and request.POST['aYear']!='0' and \
            request.POST['bYear']!='0' and 'regulation' in request.POST.keys() and request.POST['regulation']!='0':
            AYear = request.POST['aYear']
        else:
            form = DBYBSAYASSelectionForm(data)
            return render(request, 'ADUGDB/BTRegistrationStatus.html',{'form':form})

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
            oerollstatus = int(request.POST['oerolls-status'])
            oeregstatus = int(request.POST['oeregs-status'])
            Mode = request.POST['mode']
            regulation = request.POST['regulation']
            rg_status = BTRegistrationStatus.objects.filter(AYear=AYear, ASem=ASem, BYear=BYear, BSem=BSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode)
            if(len(rg_status)==0):
                rg_status_obj = BTRegistrationStatus(AYear=AYear, ASem=ASem, BYear=BYear, BSem=BSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode, RollListStatus=rollStatus, RegistrationStatus=regStatus, MarksStatus=marksStatus, GradeStatus=gradesStatus, \
                    OERollListStatus=oerollstatus, OERegistartionStatus=oeregstatus, Status=Status)
                msg = f'The event {rg_status_obj.AYear}:{rg_status_obj.ASem}:{rg_status_obj.BYear}:{rg_status_obj.BSem}:\
                        {rg_status_obj.Dept}:{rg_status_obj.Regulation} has been successfully updated(Status:{rg_status_obj.Status}),  \
                        (RegistrationStatus:{rg_status_obj.RegistrationStatus}), (MarksStatus:{rg_status_obj.MarksStatus}), (GradesStatus:{rg_status_obj.GradeStatus}) \
                            for {rg_status_obj.Mode} mode.'
                rg_status_obj.save()
                
            else:
                rg_status.update(Status=Status,RollListStatus=rollStatus,RegistrationStatus=regStatus, MarksStatus=marksStatus, \
                    GradeStatus=gradesStatus, OERollListStatus=oerollstatus, OERegistartionStatus=oeregstatus)
                rg_status_obj = BTRegistrationStatus.objects.filter(AYear=AYear, ASem=ASem, BYear=BYear, BSem=BSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode).first()
                msg = f'The event {rg_status_obj.AYear}:{rg_status_obj.ASem}:{rg_status_obj.BYear}:{rg_status_obj.BSem}:\
                    {rg_status_obj.Dept}:{rg_status_obj.Regulation} has been successfully updated(Status:{rg_status_obj.Status}),  \
                       (RegistrationStatus:{rg_status_obj.RegistrationStatus}), (MarksStatus:{rg_status_obj.MarksStatus}), (GradesStatus:{rg_status_obj.GradeStatus}) \
                        for {rg_status_obj.Mode} mode.'
            return render(request, 'ADUGDB/BTRegistrationStatus.html',{'form':form, 'msg':msg}) 
    else:
        form = DBYBSAYASSelectionForm()
    return render(request, 'ADUGDB/BTRegistrationStatus.html',{'form':form})
