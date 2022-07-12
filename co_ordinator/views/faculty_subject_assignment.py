from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test 
from SupExamDBRegistrations.views.home import is_Superintendent
from hod.models import FacultyInfo
from superintendent.constants import DEPT_DICT, ROMAN_TO_INT
from co_ordinator.forms import FacultySubjectAssignmentForm, FacultyAssignmentStatusForm
from co_ordinator.models import FacultyAssignment, StudentRegistrations, Subjects, RollLists
from hod.models import Coordinator
from superintendent.models import HOD, RegistrationStatus


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def faculty_subject_assignment(request):
    user = request.user
    if 'Co_ordinator' in user.groups.all():
        current_user = Coordinator.objects.filter(User=user, RevokeDate__isnull=True)
    elif 'HOD' in user.groups.all():
        current_user = HOD.objects.filter(User=user, RevokeDate__isnull=True)
    if(request.method =='POST'):
        form = FacultySubjectAssignmentForm(request.POST)
        if(form.is_valid()):
            regEvent=form.cleaned_data['regID']
            event_string = regEvent.split(':')
            dept = DEPT_DICT[event_string[0]]
            ayear = int(event_string[3])
            asem = int(event_string[4])
            byear = ROMAN_TO_INT[event_string[1]]
            bsem = ROMAN_TO_INT[event_string[2]]
            regulation = int(event_string[5])
            mode = event_string[6]
            regEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation).first()
            if mode == 'R':
                subjects = Subjects.objects.filter(RegEventId_id=regEvent, OfferedBy=current_user.Dept)
            else:
                student_Registrations = StudentRegistrations.objects.filter(RegEventId=regEventId.id).values_list('sub_id', flat=True)
                subjects = Subjects.objects.filter(OfferedBy=current_user.Dept, id__in=student_Registrations.values_list('sub_id', flat=True))
            request.session['currentRegEvent']=regEventId
            return render(request, 'co_ordinator/FacultyAssignment.html', {'form': form, 'subjects':subjects})
    form = FacultySubjectAssignmentForm(co_ordinator=current_user)
    return render(request, 'co_ordinator/FacultyAssignment.html',{'form':form})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def faculty_subject_assignment_detail(request, pk):
    user = request.user
    if 'Co_ordinator' in user.groups.all():
        current_user = Coordinator.objects.filter(User=user, RevokeDate__isnull=True)
    elif 'HOD' in user.groups.all():
        current_user = HOD.objects.filter(User=user, RevokeDate__isnull=True)
    subject = Subjects.objects.get(id=pk)
    faculty = FacultyInfo.objects.filter(Dept=current_user.Dept)
    sections = RollLists.objects.filter(RegEventId_id=request.session.get('currentRegEvent').id).values_list('Section', flat=True).distinct()
    faculty_assigned = FacultyAssignment.objects.filter(subject=subject)
    co_ordinator=''
    faculty_section={}
    if faculty_assigned:
        co_ordinator = faculty_assigned[0].co_ordinator_id
        faculty_section = {row.Section: row.faculty_id for row in faculty_assigned}
    
    if request.method == 'POST':
        for sec in sections:
            if request.POST.get('faculty-'+str(sec)):
                if faculty_assigned and faculty_assigned.get(Section=sec):
                    faculty_row = faculty_assigned.get(Section=sec)
                    faculty_row.co_ordinator_id = request.POST.get('course-coordinator') or 0
                    faculty_row.faculty_id = request.POST.get('faculty-'+str(sec))
                    faculty_row.save()
                else:
                    faculty_row = FacultyAssignment(subject=subject, co_ordinator_id=request.POST.get('course-coordinator'),\
                        faculty_id=request.POST.get('faculty-'+str(sec)), Section=sec, RegEventId_id=request.session['currentRegEvent'].id)
                    faculty_row.save()
        return redirect('FacultySubjectAssignment')
    return render(request, 'co_ordinator/FacultyAssignmentdetail.html', {'subject':subject, 'faculty':faculty,\
        'section':sections, 'co_ordinator':co_ordinator, 'faculty_section':faculty_section})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def faculty_assignment_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co_ordinator' in groups:
        faculty = Coordinator.objects.filter(User=user, RevokeDate__isnull=True)
    elif 'HOD' in groups:
        faculty = HOD.objects.filter(User=user, RevokeDate__isnull=True)
    else:
        raise Http404("You are not authorized to view this page")
    if(request.method =='POST'):
        form = FacultyAssignmentStatusForm(faculty, request.POST)
        if(form.is_valid()):
            regeventid=form.cleaned_data['regID']
            faculty = FacultyAssignment.objects.filter(subject__RegEventId__id=regeventid)
            return render(request, 'SupExamDBRegistrations/FacultyAssignmentStatus.html',{'form':form, 'faculty':faculty})
    else:
        form = FacultyAssignmentStatusForm(faculty=faculty)
    return render(request, 'SupExamDBRegistrations/FacultyAssignmentStatus.html',{'form':form})