# from asyncio.windows_events import NULL
# from django.http import HttpResponseRedirect, HttpResponse
# from django.shortcuts import redirect, render
# from django.urls import reverse
# from SupExamDBRegistrations.forms import FacultyAssignmentForm,FacultyDeletionForm,FacultyInfoUpdateForm,BacklogRegistrationForm, RegistrationsEventForm,FacultyUploadForm, \
#     SubjectsUploadForm, StudentRegistrationUpdateForm, SubjectDeletionForm, SubjectFinalizeEventForm, FacultyAssignmentStatusForm
# from SupExamDBRegistrations.models import Faculty_Coordinator, Faculty_user, FacultyInfo, RegistrationStatus, Regulation, StudentBacklogs, StudentInfo, StudentRegistrations, Subjects, Subjects_Staging,\
#     RollLists
# from SupExamDBRegistrations.resources import FacultyInfoResource
# from .home import is_Superintendent
# from django.contrib.auth.decorators import login_required, user_passes_test 
# from django.contrib.auth import logout 
# from django.db.models import F
# from tablib import Dataset
# from import_export.formats.base_formats import XLSX
# from django.contrib.auth import get_user_model
# from django.utils import timezone

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def faculty_user(request):
#     faculty = FacultyInfo.objects.all()
        

#     return render(request, 'SupExamDBRegistrations/FacultyUser.html',{'faculty':faculty})

# login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def faculty_user_detail(request,pk):
#     faculty = FacultyInfo.objects.get(id=pk)
#     User = get_user_model()
#     #print(User.objects.all().values())
#     already_assigned = Faculty_user.objects.filter(RevokeDate = None)
#     already_assigned2 = Faculty_Coordinator.objects.filter(RevokeDate = None)
#     already_assigned = already_assigned.union(already_assigned2)
#     users = User.objects.all().exclude(id__in=already_assigned.values_list('User_id', flat=True))
#     user_assigned = Faculty_user.objects.filter(Faculty_id = pk,RevokeDate=None)
#     assigned_user =''
#     if user_assigned :
#         assigned_user = user_assigned[0].User_id
#         assign_user = User.objects.filter(id=user_assigned[0].User_id)
#         print(assign_user)
#         users = users.union(assign_user)
    
    
#     if request.method == 'POST':
#         print( request.POST.get('fac_user'))
#         if request.POST.get('fac_user') and (request.POST.get('fac_user')!= '0'):
#             facuser = Faculty_user.objects.filter(Faculty_id= pk,RevokeDate=None)
#             if facuser:
#                 facuser.update(User_id =  request.POST.get('fac_user'))
#             else:
#                facuser=  Faculty_user(User_id =  request.POST.get('fac_user'),Faculty_id = pk)
#                facuser.save()

               
#         return redirect('FacultyUserAssignment')
#     return render(request, 'SupExamDBRegistrations/FacultyUserdetail.html', { 'faculty':faculty,\
#         'Users':users,'assigned_user':assigned_user})


# login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def faculty_user_revoke(request,pk):
#     faculty = FacultyInfo.objects.get(id=pk)
#     User = get_user_model()
#     fac = Faculty_user.objects.filter(Faculty_id=pk,RevokeDate=None)
#     if fac:
#         fac.update(RevokeDate =timezone.now().date())
#     return redirect('FacultyUserAssignment')





# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def faculty_Coordinator(request):
#     faculty = FacultyInfo.objects.all()
        
#     return render(request, 'SupExamDBRegistrations/FacultyCoordinator.html',{'faculty':faculty})

# login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def faculty_Coordinator_detail(request,pk):
#     faculty = FacultyInfo.objects.get(id=pk)
#     User = get_user_model()
#     #print(User.objects.all().values())
#     already_assigned = Faculty_user.objects.filter(RevokeDate = None)
#     already_assigned2 = Faculty_Coordinator.objects.filter(RevokeDate = None)
#     already_assigned = already_assigned.union(already_assigned2)
#     users = User.objects.all().exclude(id__in=already_assigned.values_list('User_id', flat=True))
#     user_assigned = Faculty_Coordinator.objects.filter(Faculty_id = pk,RevokeDate=None)
#     assigned_user =''
#     if user_assigned :
#         assigned_user = user_assigned[0].User_id
#         assign_user = User.objects.filter(id=user_assigned[0].User_id)
#         print(assign_user)
#         users = users.union(assign_user)
    
    
#     if request.method == 'POST':
#         print( request.POST.get('fac_Coordinator'))
#         if request.POST.get('fac_Coordinator') and (request.POST.get('fac_Coordinator')!= '0'):
#             facuser = Faculty_Coordinator.objects.filter(Faculty_id= pk,RevokeDate=None)
#             if facuser:
#                 facuser.update(User_id =  request.POST.get('fac_Coordinator'))
#             else:
#                facuser=  Faculty_Coordinator(User_id =  request.POST.get('fac_Coordinator'),Faculty_id = pk)
#                facuser.save()

               
#         return redirect('FacultyCoordinatorAssignment')
#     return render(request, 'SupExamDBRegistrations/FacultyCoordinatordetail.html', { 'faculty':faculty,\
#         'Users':users,'assigned_user':assigned_user})


# login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def faculty_Coordinator_revoke(request,pk):
#     faculty = FacultyInfo.objects.get(id=pk)
#     User = get_user_model()
#     fac = Faculty_Coordinator.objects.filter(Faculty_id=pk,RevokeDate=None)
#     if fac:
#         fac.update(RevokeDate =timezone.now().date())
#     return redirect('FacultyCoordinatorAssignment')

