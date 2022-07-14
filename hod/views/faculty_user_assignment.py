from django.shortcuts import redirect, render
from hod.forms import CoordinatorAssignmentForm
from hod.models import  Faculty_user,Coordinator
from ExamStaffDB.models import FacultyInfo
from superintendent.user_access_test import is_Hod, co_ordinator_assignment_access
from django.contrib.auth.decorators import login_required, user_passes_test
from superintendent.models import HOD
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

@login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_user(request):
    
    user = request.user
    hod = HOD.objects.filter(RevokeDate__isnull=True,User=user).first()
    faculty = FacultyInfo.objects.filter(Dept=hod.Dept,Working=True)
        

    return render(request, 'hod/FacultyUser.html',{'faculty':faculty})

login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_user_detail(request,pk):
    faculty = FacultyInfo.objects.get(id=pk)
    already_assigned = Faculty_user.objects.filter(RevokeDate__isnull=True)
    assigned_user = already_assigned.filter(Faculty_id=pk).first()
    already_assigned = already_assigned.exclude(Faculty_id=pk)
    group = Group.objects.filter(name='Faculty').first()
    users = group.user_set.all().exclude(id__in=already_assigned.values_list('User_id', flat=True))
    
    if request.method == 'POST':
        if assigned_user:
            if request.POST.get('fac_user') and (int(request.POST.get('fac_user')) != assigned_user.User.id):
                facuser = Faculty_user.objects.filter(Faculty_id= pk,RevokeDate__isnull=True).first()
                facuser.update(RevokeDate =timezone.now())
                facuser =  Faculty_user(User_id =  request.POST.get('fac_user'),Faculty_id = pk)
                facuser.save()
        else:
            fac_user = Faculty_user(User_id=request.POST.get('fac_user'), Faculty_id=pk)
            fac_user.save()
        return redirect('FacultyUserAssignment')
    return render(request, 'hod/FacultyUserdetail.html', { 'faculty':faculty,\
        'Users':users,'assigned_user':assigned_user})


login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_user_revoke(request,pk):
    fac = Faculty_user.objects.filter(Faculty_id=pk,RevokeDate__isnull=True).first()
    if fac:
        fac.update(RevokeDate =timezone.now())
    return redirect('FacultyUserAssignment')





@login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_Coordinator(request):
    user = request.user
    hod = HOD.objects.filter(RevokeDate__isnull=True,User=user).first()
    if(request.method == 'POST'):
        form = CoordinatorAssignmentForm(hod.Dept,request.POST)
        if form.is_valid():
            if form.cleaned_data.get('BYear') and form.cleaned_data.get('coordinator') and form.cleaned_data.get('user') and 'submit-form' in request.POST.keys():
                initial_coodinator = Coordinator.objects.filter(RevokeDate__isnull=True, Dept=hod.Dept).first()
                if initial_coodinator:
                    if (initial_coodinator.Faculty.id != int(form.cleaned_data.get('hod'))) or (initial_coodinator.User.id != int(form.cleaned_data.get('user'))):
                        initial_coodinator.RevokeDate = timezone.now()
                        initial_coodinator.save()
                        new_coordinator = Coordinator(Faculty_id=form.cleaned_data.get('coordinator'), User_id=form.cleaned_data.get('user'), BYear=form.cleaned_data.get('BYear'),Dept =hod.Dept)
                        new_coordinator.save()
                else:
                    new_coordinator = Coordinator(Faculty_id=form.cleaned_data.get('coordinator'), User_id=form.cleaned_data.get('user'), BYear=form.cleaned_data.get('BYear'),Dept =hod.Dept)
                    new_coordinator.save()
                msg = 'Coordinator assignment is done successfully'
                return render(request, 'hod/CoordinatorAssignment.html', {'form':form, 'msg':msg})
    else:
        form = CoordinatorAssignmentForm(hod.Dept)
        
    return render(request, 'hod/CoordinatorAssignment.html',{'form':form})


@login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_Coordinator_Status(request):
    if(request.user.groups.filter(name='Superintendent').exists()):
        user = request.user
        Coordinators = Coordinator.objects.all()
    elif(request.user.groups.filter(name='hod').exists()):
        user = request.user
        hod = HOD.objects.filter(RevokeDate__isnull=True,User=user)
        Coordinators = Coordinator.objects.filter(Dept=hod.Dept)
    return render(request, 'hod/CoordinatorAssignmentStatus.html', {'Coordinators':Coordinators})
        
