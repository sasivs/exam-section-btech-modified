from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.http import HttpResponse
from ADAUGDB.user_access_test import template_download_access 
from BThod.models import BTCoordinator, BTFaculty_user
from BTco_ordinator.forms import TemplateDownloadForm
from ADAUGDB.models import BTRegistrationStatus

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
        if form.is_valid():
            if current_user.group == 'Co-ordinator':
                event = BTRegistrationStatus.objects.filter(id=form.cleaned_data.get('regID')).first()
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
                response['Content-Disposition'] = 'attachment; filename=Template({regevent}).xlsx'.format(regevent=event.__str__())
                workbook = generate_template(event.AYear, event.ASem, event.BYear, event.BSem, event.Dept, event.Mode, event.Regulation, form.cleaned_data.get('option'))
                workbook.save(response)
                return response
            elif current_user.group == 'Faculty':
                rom2int = {'I':1,'II':2,'III':3,'IV':4}
                regid = form.cleaned_data.get('regID').split(',')[0]
                subject = form.cleaned_data.get('regID').split(',')[1]
                strs = regid.split(':')
                ayear = int(strs[2])
                asem = int(strs[3])
                byear = rom2int[strs[0]]
                bsem = rom2int[strs[1]]
                regulation = float(strs[4])
                mode = strs[5]
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
                response['Content-Disposition'] = 'attachment; filename=Template({regevent}).xlsx'.format(regevent=event.__str__())
                workbook = generate_template(ayear, asem, byear, bsem, mode, regulation, subject)
                workbook.save(response)
                return response
    else:
        form = TemplateDownloadForm(current_user)
    return render(request, 'BTco_ordinator/TemplateDownload.html', {'form':form})
