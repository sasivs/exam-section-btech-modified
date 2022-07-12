from django.shortcuts import redirect, render
from hod.forms import CoordinatorAssignmentForm
from hod.models import  FacultyInfo,Faculty_user,Coordinator
from SupExamDB.views import is_Hod
from django.contrib.auth.decorators import login_required, user_passes_test 
from superintendent.models import HOD
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

@login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_user(request):
    
    user = request.user
    hod = HOD.objects.filter(RevokeDate__isnull=True,User=user)
    faculty = FacultyInfo.objects.filter(Dept = hod.Dept,Working=True)
        

    return render(request, 'hod/FacultyUser.html',{'faculty':faculty})

login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_user_detail(request,pk):
    faculty = FacultyInfo.objects.get(id=pk)
    User = get_user_model()
    #print(User.objects.all().values())
    already_assigned = Faculty_user.objects.filter(RevokeDate__isnull=True)

    g = Group.objects.filter(name='Faculty').first()
    users = g.user_set.all().exclude(id__in=already_assigned.values_list('User_id', flat=True))
    #users = User.objects.all().exclude(id__in=already_assigned.values_list('User_id', flat=True))
    user_assigned = Faculty_user.objects.filter(Faculty_id = pk,RevokeDate__isnull=True)
    assigned_user =''
    if user_assigned :
        assigned_user = user_assigned[0].User_id
        assign_user = User.objects.filter(id=user_assigned[0].User_id)
        print(assign_user)
        users = users.union(assign_user)
    
    
    if request.method == 'POST':
        print( request.POST.get('fac_user'))
        if request.POST.get('fac_user') and (request.POST.get('fac_user')!= '0') and (request.POST.get('fac_user')!= assigned_user):

            facuser = Faculty_user.objects.filter(Faculty_id= pk,RevokeDate__isnull=True)
            if facuser:
                facuser.update(RevokeDate =timezone.now())
            facuser=  Faculty_user(User_id =  request.POST.get('fac_user'),Faculty_id = pk)
            facuser.save()

               
        return redirect('FacultyUserAssignment')
    return render(request, 'hod/FacultyUserdetail.html', { 'faculty':faculty,\
        'Users':users,'assigned_user':assigned_user})


login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_user_revoke(request,pk):
    faculty = FacultyInfo.objects.get(id=pk)
    User = get_user_model()
    fac = Faculty_user.objects.filter(Faculty_id=pk,RevokeDate__isnull=True)
    if fac:
        fac.update(RevokeDate =timezone.now())
    return redirect('FacultyUserAssignment')





@login_required(login_url="/login/")
@user_passes_test(is_Hod)
def faculty_Coordinator(request):
    user = request.user
    hod = HOD.objects.filter(RevokeDate__isnull=True,User=user)
    faculty = FacultyInfo.objects.filter(Dept = hod.Dept,Working=True)
    if(request.method == 'POST'):
        CoordinatorAssignmentForm(hod.Dept,request.POST)
        if form.is_valid():
            if form.cleaned_data.get('BYear') and form.cleaned_data.get('coordinator') and form.cleaned_data.get('user') and form.cleaned_data.get('submit'):
                initial_coodinator = Coordinator.objects.filter(RevokeDate__isnull=True, Dept=hod.Dept).first()
                if initial_coodinator:
                    if (initial_coodinator.Faculty.id != form.cleaned_data.get('hod')) or (initial_coodinator.User.id != form.cleaned_data.get('user')):
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
        
    return render(request, 'hod/CoordinatorAssignment.html',{'faculty':faculty})

