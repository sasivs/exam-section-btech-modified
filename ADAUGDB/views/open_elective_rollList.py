from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from ADAUGDB.user_access_test import is_Associate_Dean_Academics
from ADAUGDB.forms import OERollListStatusForm, OpenElectiveRollListForm
from ADAUGDB.resources import BTOpenElectiveRollListsResource
from ADAUGDB.models import BTOpenElectiveRollLists
from ADAUGDB.models import BTCycleCoordinator, BTHOD
from BThod.models import BTCoordinator
from ADAUGDB.models import BTRegistrationStatus
from import_export.formats.base_formats import XLSX
from tablib import Dataset
from ADAUGDB.user_access_test import  roll_list_status_access
from BTco_ordinator.models import BTRollLists_Staging





@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def open_elective_rollList(request):
    if(request.method == "POST"):
        form = OpenElectiveRollListForm(request.POST)
        if 'submit-form' in request.POST.keys():
            if form.is_valid() and request.POST['regid'] != 'Choose Event' and request.POST['sub'] != 'Choose Subject' and request.POST['file'] != '':
                rom2int = {'I':1,'II':2,'III':3,'IV':4}
                subid = form.cleaned_data.get('sub')
                regid = form.cleaned_data.get('redID')
                strs = regid.split(':')
                ayear = int(strs[3])
                asem = int(strs[4])
                byear = rom2int[strs[1]]
                bsem = rom2int[strs[2]]
                regulation = float(strs[5])
                mode = strs[6]
                file = form.cleaned_data.get('file')
                BTOpenElectiveRollLists.objects.filter(RegEventId__AYear=ayear,RegEventId__ASem=asem,RegEventId__BYear=byear,RegEventId__BSem=bsem,RegEventId__Regulation=regulation,RegEventId__Mode=mode,subject_id=subid).delete()
                data = bytes()
                for chunk in file.chunks():
                    data+=chunk
                dataset = XLSX().create_dataset(data)
                newDataset = Dataset()
                newDataset.headers = ['student','RegEventID','Subject','Section']
                for i in range(len(dataset)):
                    row = dataset[i]
                    rolls = BTRollLists_Staging.objects.get(student__RegNo=row[0],RegEventId__AYear=ayear,RegEventId__ASem=asem,RegEventId__BYear=byear,RegEventId__BSem=bsem,RegEventId__Regulation=regulation,RegEventId__Mode=mode)
                    newRow = (rolls.id,rolls.RegEventId.id,subid,row[2])
                    newDataset.append(newRow)
                oerolllist_resourse = BTOpenElectiveRollListsResource()
                result = oerolllist_resourse.import_data(newDataset,dry_run=True)
                if(not result.has_errors()):
                    oerolllist_resourse.import_data(newDataset,dry_run=False)
                    msg = 'RollList updated successfully.'
                    return render(request, 'ADAUGDB/OpenElectiveRollList.html',{'form':form, 'msg':msg})
                else:
                    errors = result.row_errors()
                    indices = set([i for i in range(len(newDataset))])
                    errorIndices = set([i[0]-1 for i in errors])
                    cleanIndices = indices.difference(errorIndices)
                    cleanDataset = Dataset()
                    for i in list(cleanIndices):
                        cleanDataset.append(newDataset[i])
                    cleanDataset.headers = newDataset.headers

                    result1 = oerolllist_resourse.import_data(newDataset,dry_run=True)
                    if not result1.has_errors():
                        oerolllist_resourse.import_data(newDataset,dry_run=False)
                    else:
                        print('Something went wrong in plain import')
                    
                    errorData = Dataset()
                    for i in list(errorIndices):
                        errorData.append(dataset[i])
                    OERollsErrRows = [ (errorData[i][0],errorData[i][1],errorData[i][2])\
                                for i in range(len(errorData))]
                    return render(request,'ADAUGDB/BTOERoleListErrorHandler.html',{'errorrows':OERollsErrRows})
                    
        return render(request, 'ADAUGDB/OpenElectiveRollList.html',{'form':form})
    else:
        form = OpenElectiveRollListForm()
        return render(request, 'ADAUGDB/OpenElectiveRollList.html',{'form':form})

@login_required(login_url="/login/")
@user_passes_test(roll_list_status_access)
def OERollList_Status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Superintendent' in groups or 'Associate-Dean-Academics' in groups or 'Associate-Dean-Exams' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1)
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept)
    elif 'Co-ordinator' in groups:
        co_ordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Dept, BYear=co_ordinator.BYear)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=cycle_cord.Cycle, BYear=1)
    if request.method == 'POST':
        form = OERollListStatusForm(request.POST)
        if(form.is_valid()):
                rom2int = {'I':1,'II':2,'III':3,'IV':4}
                regid = form.cleaned_data.get('redID')
                strs = regid.split(':')
                ayear = int(strs[3])
                asem = int(strs[4])
                byear = rom2int[strs[1]]
                bsem = rom2int[strs[2]]
                regulation = float(strs[5])
                mode = strs[6]
                subid = form.cleaned_data.get('sub')
                rows = BTOpenElectiveRollLists.objects.filter(subject_id=subid,RegEventId__AYear=ayear,RegEventId__ASem=asem,RegEventId__BYear=byear,RegEventId__BSem=bsem,RegEventId__Regulation=regulation,RegEventId__Mode=mode).order_by('student__id')
                return (render(request, 'BTco_ordinator/OERollListStatus.html',{'form':form,'rows':rows})) 
        return render(request, 'ADAUGDB/OERollListStatus.html', {'form':form,'rows':rows})
  
    else:
        form = OERollListStatusForm()
        return render(request, 'ADAUGDB/OERollListStatus.html', {'form':form})


