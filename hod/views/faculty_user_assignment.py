from django.shortcuts import redirect, render
from hod.forms import CoordinatorAssignmentForm
from hod.models import  BTFaculty_user,BTCoordinator
from ExamStaffDB.models import BTFacultyInfo
from superintendent.user_access_test import is_Hod, co_ordinator_assignment_access
from django.contrib.auth.decorators import login_required, user_passes_test
from superintendent.models import BTHOD
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

@login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_user(request):
    
    user = request.user
    hod = BTHOD.objects.filter(RevokeDate__isnull=True,User=user).first()
    faculty = BTFacultyInfo.objects.filter(Dept=hod.Dept,Working=True)
    faculty_assigned = BTFaculty_user.objects.filter(Faculty__in=faculty, RevokeDate__isnull=True)
    for fac in faculty:
        if faculty_assigned.filter(Faculty=fac).exists():
            fac.User = faculty_assigned.filter(Faculty=fac).first().User
        else:
            fac.User = None

    return render(request, 'hod/FacultyUser.html',{'faculty':faculty})

login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_user_detail(request,pk):
    faculty = BTFacultyInfo.objects.get(id=pk)
    already_assigned = BTFaculty_user.objects.filter(RevokeDate__isnull=True)
    assigned_user = already_assigned.filter(Faculty_id=pk).first()
    already_assigned = already_assigned.exclude(Faculty_id=pk)
    group = Group.objects.filter(name='Faculty').first()
    users = group.user_set.all().exclude(id__in=already_assigned.values_list('User_id', flat=True))
    
    if request.method == 'POST':
        if assigned_user:
            if request.POST.get('fac_user') and (int(request.POST.get('fac_user')) != assigned_user.User.id):
                facuser = BTFaculty_user.objects.filter(Faculty_id= pk,RevokeDate__isnull=True).first()
                facuser.update(RevokeDate =timezone.now())
                facuser =  BTFaculty_user(User_id =  request.POST.get('fac_user'),Faculty_id = pk)
                facuser.save()
        else:
            fac_user = BTFaculty_user(User_id=request.POST.get('fac_user'), Faculty_id=pk)
            fac_user.save()
        return redirect('FacultyUserAssignment')
    return render(request, 'hod/FacultyUserdetail.html', { 'faculty':faculty,\
        'Users':users,'assigned_user':assigned_user})


login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_user_revoke(request,pk):
    fac = BTFaculty_user.objects.filter(Faculty_id=pk,RevokeDate__isnull=True).first()
    if fac:
        fac.RevokeDate = timezone.now()
        fac.save()
    return redirect('FacultyUserAssignment')





@login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_Coordinator(request):
    user = request.user
    hod = BTHOD.objects.filter(RevokeDate__isnull=True,User=user).first()
    if(request.method == 'POST'):
        form = CoordinatorAssignmentForm(hod.Dept,request.POST)
        if 'BYear' in request.POST.keys():
            assigned_coordinator = BTCoordinator.objects.filter(BYear=request.POST.get('BYear'), RevokeDate__isnull=True).first()
        if form.is_valid():
            if form.cleaned_data.get('BYear') and form.cleaned_data.get('coordinator') and form.cleaned_data.get('user') and 'submit-form' in request.POST.keys():
                initial_coodinator = BTCoordinator.objects.filter(RevokeDate__isnull=True, Dept=hod.Dept, BYear=form.cleaned_data.get('BYear')).first()
                if initial_coodinator:
                    if (initial_coodinator.Faculty.id != int(form.cleaned_data.get('coordinator'))) or (initial_coodinator.User.id != int(form.cleaned_data.get('user'))):
                        initial_coodinator.RevokeDate = timezone.now()
                        initial_coodinator.save()
                        new_coordinator = BTCoordinator(Faculty_id=form.cleaned_data.get('coordinator'), User_id=form.cleaned_data.get('user'), BYear=form.cleaned_data.get('BYear'),Dept =hod.Dept)
                        new_coordinator.save()
                else:
                    new_coordinator = BTCoordinator(Faculty_id=form.cleaned_data.get('coordinator'), User_id=form.cleaned_data.get('user'), BYear=form.cleaned_data.get('BYear'),Dept =hod.Dept)
                    new_coordinator.save()
                msg = 'Coordinator assignment is done successfully'
                return render(request, 'hod/CoordinatorAssignment.html', {'form':form, 'msg':msg})
            else:
                if assigned_coordinator:
                    return render(request, 'hod/CoordinatorAssignment.html', {'form':form, 'initial_cord':assigned_coordinator.Faculty.id, 'initial_user':assigned_coordinator.User.id})
    else:
        form = CoordinatorAssignmentForm(hod.Dept)
        
    return render(request, 'hod/CoordinatorAssignment.html',{'form':form})


@login_required(login_url="/login/")
@user_passes_test(co_ordinator_assignment_access)
def faculty_Coordinator_Status(request):
    if(request.user.groups.filter(name='Superintendent').exists()):
        user = request.user
        Coordinators = BTCoordinator.objects.all()
    elif(request.user.groups.filter(name='HOD').exists()):
        user = request.user
        hod = BTHOD.objects.filter(RevokeDate__isnull=True,User=user).first()
        Coordinators = BTCoordinator.objects.filter(Dept=hod.Dept)
    return render(request, 'hod/CoordinatorAssignmentStatus.html', {'Coordinators':Coordinators})
        
