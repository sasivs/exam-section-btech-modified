from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 

from ADPGDB.forms import DMYMSAYASSelectionForm, CreateRegistrationEventForm
from MTsuperintendent.models import MTProgrammeModel
from ADPGDB.models import MTRegistrationStatus
from MTsuperintendent.user_access_test import is_Associate_Dean

# Create your views here.

@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean)
def create_registration_event(request):
    msg = ''
    if request.method == 'POST':
        form = CreateRegistrationEventForm(request.POST)
        if form.is_valid() and form.cleaned_data.get('dept') and form.cleaned_data.get('aSem') and form.cleaned_data.get('mSem'):
            AYear = form.cleaned_data['aYear']
            ASem = form.cleaned_data['aSem']
            MYear = form.cleaned_data['mYear']
            MSem = form.cleaned_data['mSem']
            Dept = form.cleaned_data['dept']
            Mode = form.cleaned_data['mode']
            regulation = form.cleaned_data['regulation']

            if form.cleaned_data.get('dept')!='all':
                Dept = int(Dept)
                if MTRegistrationStatus.objects.filter(AYear=AYear, ASem=ASem, MYear=MYear, MSem=MSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode).exists():
                    msg = 'Registration event already created.'
                    return render(request, 'ADPGDB/BTRegistrationStatus.html', {'form':form, 'msg':msg})
                else:
                    rg_status_obj = MTRegistrationStatus(AYear=AYear, ASem=ASem, MYear=MYear, MSem=MSem, Dept=Dept, Regulation=regulation, \
                        Mode=Mode, RollListStatus=1, RegistrationStatus=1, MarksStatus=1, GradeStatus=1, Status=1)
                    rg_status_obj.save()
                    msg = 'The Event {} has been created successfully'.format(rg_status_obj.__str__())
            else:
                departments = MTProgrammeModel.objects.filter(ProgrammeType='PG')
                created_dept = []
                for department in departments:
                    dept = department.Dept
                    if not MTRegistrationStatus.objects.filter(AYear=AYear, ASem=ASem, MYear=MYear, MSem=MSem, Dept=dept, Regulation=regulation, \
                        Mode=Mode).exists():
                        rg_status_obj = MTRegistrationStatus(AYear=AYear, ASem=ASem, MYear=MYear, MSem=MSem, Dept=dept, Regulation=regulation, \
                            Mode=Mode, RollListStatus=1, RegistrationStatus=1, MarksStatus=1, GradeStatus=1, Status=1)
                        rg_status_obj.save()
                        created_dept.append(department.Specialization)
                created_dept = ','.join(created_dept)
                msg = 'The Event has been created successfully for {} departments'.format(created_dept)
    else:
        form = CreateRegistrationEventForm()
    return render(request, 'ADPGDB/BTRegistrationStatus.html', {'form':form, 'msg':msg})



@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean)
def update_manage_registrations(request):
    if(request.method=='POST'):
        form = DMYMSAYASSelectionForm(request.POST)
        data = {key:request.POST[key] for key in request.POST.keys()}
        if request.POST['aYear']!='' and request.POST['mYear']!='' and request.POST['aYear']!='0' and \
            request.POST['mYear']!='0' and 'regulation' in request.POST.keys() and request.POST['regulation']!='0':
            AYear = request.POST['aYear']
        else:
            form = DMYMSAYASSelectionForm(data)
            return render(request, 'ADPGDB/BTRegistrationStatus.html',{'form':form})

        if(request.POST['dept']!='0' and request.POST['mSem']!='0' and request.POST['aSem']!='0'):
            AYear = request.POST['aYear']
            ASem = request.POST['aSem']
            MYear = request.POST['mYear']
            MSem = request.POST['mSem']
            Dept = int(request.POST['dept'])
            Status = int(request.POST['status'])
            rollStatus = int(request.POST['roll-status'])
            regStatus = int(request.POST['reg-status'])
            marksStatus = int(request.POST['marks-status'])
            gradesStatus = int(request.POST['grades-status'])
            Mode = request.POST['mode']
            regulation = request.POST['regulation']
            rg_status = MTRegistrationStatus.objects.filter(AYear=AYear, ASem=ASem, MYear=MYear, MSem=MSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode)
            if(len(rg_status)==0):
                rg_status_obj = MTRegistrationStatus(AYear=AYear, ASem=ASem, MYear=MYear, MSem=MSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode,RegistrationStatus=regStatus, RollListStatus=rollStatus,Status=Status,MarksStatus=marksStatus, GradeStatus=gradesStatus)
                
                msg = f'The event {rg_status_obj.AYear}:{rg_status_obj.ASem}:{rg_status_obj.MYear}:{rg_status_obj.MSem}:\
                        {rg_status_obj.Dept}:{rg_status_obj.Regulation} has been successfully updated(Status:{rg_status_obj.Status}),  \
                        (RegistrationStatus:{rg_status_obj.RegistrationStatus}), (MarksStatus:{rg_status_obj.MarksStatus}), (GradesStatus:{rg_status_obj.GradeStatus}) \
                            for {rg_status_obj.Mode} mode.'
                rg_status_obj.save()
            else:
                rg_status.update(Status=Status, RollListStatus=rollStatus, RegistrationStatus=regStatus, MarksStatus=marksStatus, GradeStatus=gradesStatus)
                rg_status_obj = MTRegistrationStatus.objects.filter(AYear=AYear, ASem=ASem, MYear=MYear, MSem=MSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode).first()
                msg = f'The event {rg_status_obj.AYear}:{rg_status_obj.ASem}:{rg_status_obj.MYear}:{rg_status_obj.MSem}:\
                    {rg_status_obj.Dept}:{rg_status_obj.Regulation} has been successfully updated(Status:{rg_status_obj.Status}),  \
                       (RegistrationStatus:{rg_status_obj.RegistrationStatus}), (MarksStatus:{rg_status_obj.MarksStatus}), (GradesStatus:{rg_status_obj.GradeStatus}) \
                        for {rg_status_obj.Mode} mode.'
                

            return render(request, 'ADPGDB/BTRegistrationStatus.html',{'form':form, 'msg':msg}) 

            
    else:
        form = DMYMSAYASSelectionForm()
    return render(request, 'ADPGDB/BTRegistrationStatus.html',{'form':form})
    