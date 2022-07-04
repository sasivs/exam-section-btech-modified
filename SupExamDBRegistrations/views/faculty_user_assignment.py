from asyncio.windows_events import NULL
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from SupExamDBRegistrations.forms import FacultyAssignmentForm,FacultyDeletionForm,FacultyInfoUpdateForm,BacklogRegistrationForm, RegistrationsEventForm,FacultyUploadForm, \
    SubjectsUploadForm, StudentRegistrationUpdateForm, SubjectDeletionForm, SubjectFinalizeEventForm, FacultyAssignmentStatusForm
from SupExamDBRegistrations.models import Faculty_user, FacultyInfo, RegistrationStatus, Regulation, StudentBacklogs, StudentInfo, StudentRegistrations, Subjects, Subjects_Staging,\
    RollLists, FacultyAssignment
from SupExamDBRegistrations.resources import FacultyInfoResource
from .home import is_Superintendent
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.db.models import F
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from django.contrib.auth import get_user_model

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def faculty_user(request):
        faculty = FacultyInfo.objects.all()
        return render(request, 'SupExamDBRegistrations/FacultyUser.html',{'faculty':faculty})

login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def faculty_user_detail(request,pk):
    faculty = FacultyInfo.objects.get(id=pk)
    User = get_user_model()
    users = User.objects.all()
    print(User.objects.all().values())
    final_users=()
    already_assigned = Faculty_user.objects.filter(RevokeDate = None)
    for user in users:
        if(user.id not in already_assigned.UserId):
            final_users.__add__(user)

    
    
    if request.method == 'POST':

        if request.POST.get('faculty-'+str()):
               
         return redirect('FacultyUserAssignment')
    return render(request, 'SupExamDBRegistrations/FacultyUserdetail.html', { 'faculty':faculty,\
        'Users':final_users})


