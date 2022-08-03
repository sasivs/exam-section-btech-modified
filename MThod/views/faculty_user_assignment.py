from django.shortcuts import redirect, render
from MThod.forms import CoordinatorAssignmentForm
from MThod.models import  MTFaculty_user,MTCoordinator
from MTExamStaffDB.models import MTFacultyInfo
from MTsuperintendent.user_access_test import is_Hod, co_ordinator_assignment_access
from django.contrib.auth.decorators import login_required, user_passes_test
from MTsuperintendent.models import MTHOD
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

@login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_user(request):
    
    user = request.user
    hod = MTHOD.objects.filter(RevokeDate__isnull=True,User=user).first()
    faculty = MTFacultyInfo.objects.filter(Dept=hod.Dept,Working=True)
    faculty_assigned = MTFaculty_user.objects.filter(Faculty__in=faculty, RevokeDate__isnull=True)
    for fac in faculty:
        if faculty_assigned.filter(Faculty=fac).exists():
            fac.User = faculty_assigned.filter(Faculty=fac).first().User
        else:
            fac.User = None

    return render(request, 'hod/FacultyUser.html',{'faculty':faculty})

login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_user_detail(request,pk):
    faculty = MTFacultyInfo.objects.get(id=pk)
    already_assigned = MTFaculty_user.objects.filter(RevokeDate__isnull=True)
    assigned_user = already_assigned.filter(Faculty_id=pk).first()
    already_assigned = already_assigned.exclude(Faculty_id=pk)
    group = Group.objects.filter(name='Faculty').first()
    users = group.user_set.all().exclude(id__in=already_assigned.values_list('User_id', flat=True))
    
    if request.method == 'POST':
        if assigned_user:
            if request.POST.get('fac_user') and (int(request.POST.get('fac_user')) != assigned_user.User.id):
                facuser = MTFaculty_user.objects.filter(Faculty_id= pk,RevokeDate__isnull=True).first()
                facuser.update(RevokeDate =timezone.now())
                facuser =  MTFaculty_user(User_id =  request.POST.get('fac_user'),Faculty_id = pk)
                facuser.save()
        else:
            fac_user = MTFaculty_user(User_id=request.POST.get('fac_user'), Faculty_id=pk)
            fac_user.save()
        return redirect('FacultyUserAssignment')
    return render(request, 'hod/FacultyUserdetail.html', { 'faculty':faculty,\
        'Users':users,'assigned_user':assigned_user})


login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_user_revoke(request,pk):
    fac = MTFaculty_user.objects.filter(Faculty_id=pk,RevokeDate__isnull=True).first()
    if fac:
        fac.RevokeDate =timezone.now()
        fac.save()
    return redirect('FacultyUserAssignment')





@login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_Coordinator(request):
    user = request.user
    hod = MTHOD.objects.filter(RevokeDate__isnull=True,User=user).first()
    if(request.method == 'POST'):
        form = CoordinatorAssignmentForm(hod.Dept,request.POST)
        if 'MYear' in request.POST.keys():
            assigned_coordinator = MTCoordinator.objects.filter(MYear=request.POST.get('MYear'), RevokeDate__isnull=True).first()
        if form.is_valid():
            if form.cleaned_data.get('MYear') and form.cleaned_data.get('coordinator') and form.cleaned_data.get('user') and 'submit-form' in request.POST.keys():
                initial_coodinator = MTCoordinator.objects.filter(RevokeDate__isnull=True, Dept=hod.Dept).first()
                if initial_coodinator:
                    if (initial_coodinator.Faculty.id != int(form.cleaned_data.get('hod'))) or (initial_coodinator.User.id != int(form.cleaned_data.get('user'))):
                        initial_coodinator.RevokeDate = timezone.now()
                        initial_coodinator.save()
                        new_coordinator = MTCoordinator(Faculty_id=form.cleaned_data.get('coordinator'), User_id=form.cleaned_data.get('user'), MYear=form.cleaned_data.get('MYear'),Dept =hod.Dept)
                        new_coordinator.save()
                else:
                    new_coordinator = MTCoordinator(Faculty_id=form.cleaned_data.get('coordinator'), User_id=form.cleaned_data.get('user'), MYear=form.cleaned_data.get('MYear'),Dept =hod.Dept)
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
        Coordinators = MTCoordinator.objects.all()
    elif(request.user.groups.filter(name='MTHOD').exists()):
        user = request.user
        hod = MTHOD.objects.filter(RevokeDate__isnull=True,User=user).first()
        Coordinators = MTCoordinator.objects.filter(Dept=hod.Dept)
    return render(request, 'hod/CoordinatorAssignmentStatus.html', {'Coordinators':Coordinators})
        