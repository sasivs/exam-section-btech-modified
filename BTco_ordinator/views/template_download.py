from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.http import HttpResponse
from ADAUGDB.user_access_test import template_download_access 
from BThod.models import BTCoordinator, BTFaculty_user
from BTco_ordinator.forms import TemplateDownloadForm, BTFacultyAssignment
from ADAUGDB.models import BTRegistrationStatus
from ADAUGDB.constants import DEPARTMENTS, YEARS, SEMS, REGULATIONS

@login_required(login_url="/login/")
@user_passes_test(template_download_access)
def download_template(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        current_user = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        current_user.group = 'Co-ordinator'
    elif 'Faculty' in groups:
        current_user = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True)
        current_user.group = 'Faculty'
    if request.method == 'POST':
        form = TemplateDownloadForm(current_user, request.POST)
        if request.POST.get('submit-form'):
            if form.is_valid():
                if current_user.group == 'Co-ordinator':
                    event = BTRegistrationStatus.objects.filter(id=form.cleaned_data.get('regID')).first()
                    if int(form.cleaned_data.get('option')) == 1:
                        filename = DEPARTMENTS[event.Dept-1]+'-'+YEARS[event.BYear]+'-Sem-'+SEMS[event.ASem]+'-'+REGULATIONS[event.Regulation]+'-'+event.Mode
                    elif int(form.cleaned_data.get('option')) == 2:
                        filename = DEPARTMENTS[event.Dept-1]+'-'+YEARS[event.BYear]+'-Sem-'+SEMS[event.ASem]+'-'+REGULATIONS[event.Regulation]+'-Open-'+event.Mode
                    elif int(form.cleaned_data.get('option')) == 3:
                        filename = DEPARTMENTS[event.Dept-1]+'-'+YEARS[event.BYear]+'-Sem-'+SEMS[event.ASem]+'-'+REGULATIONS[event.Regulation]+'-MDC-'+event.Mode
                    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
                    response['Content-Disposition'] = 'attachment; filename={regevent}.xlsx'.format(regevent=filename)
                    if event.Mode == 'R':
                        workbook = generate_template(event.AYear, event.ASem, event.BYear, event.BSem, event.Dept, event.Mode, event.Regulation, form.cleaned_data.get('option'), response)
                        workbook.save(response)
                    return response
                elif current_user.group == 'Faculty':
                    rom2int = {'I':1,'II':2,'III':3,'IV':4}
                    regid = form.cleaned_data.get('regID').split(',')[0]
                    subject = form.cleaned_data.get('regID').split(',')[1]
                    if regid.startswith('SC'):
                        strs = regid.split(':')
                        ayear = int(strs[2])
                        asem = int(strs[3])
                        byear = rom2int[strs[0]]
                        bsem = rom2int[strs[1]]
                        regulation = float(strs[4])
                        mode = strs[5]
                        filename = subject + '-' + YEARS[byear] + '-Sem-' + SEMS[bsem] + '-' + REGULATIONS[regulation] + '-' + mode
                        depts = BTFacultyAssignment.objects.filter(Coordinator_id=current_user.Faculty_id, RegEventId__Status=1, Subject__course__SubCode=subject,\
                            RegEventId__AYear=ayear, RegEventId__ASem=asem, RegEventId__BYear=byear, RegEventId__BSem=bsem, RegEventId__Regulation=regulation, RegEventId__Mode=mode).\
                            values_list('RegEventId__Dept', flat=True)
                    else:
                        depts = BTFacultyAssignment.objects.filter(Coordinator_id=current_user.Faculty_id, RegEventId__Status=1, Subject__course__SubCode=subject,\
                            RegEventId_id=regid)
                        event_obj = depts.first().RegEventId
                        filename = subject + '-' + DEPARTMENTS[event_obj.Dept-1] + '-' + YEARS[event_obj.BYear] + '-Sem-' + SEMS[event_obj.BSem] + '-' + REGULATIONS[event_obj.Regulation] + '-' + event_obj.Mode
                        depts = depts.values_list('RegEventId__Dept', flat=True)
                        mode = event_obj.Mode
                        ayear = event_obj.AYear
                        byear = event_obj.BYear
                        bsem = event_obj.BSem
                        asem = event_obj.ASem
                        regulation = event_obj.Regulation
                    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
                    response['Content-Disposition'] = 'attachment; filename=Template({regevent}).xlsx'.format(regevent=filename)
                    if mode == 'R':
                        workbook = generate_template(ayear, asem, byear, bsem, mode, regulation, subject, depts, response)
                    return response
    else:
        form = TemplateDownloadForm(current_user)
    return render(request, 'BTco_ordinator/TemplateDownload.html', {'form':form})