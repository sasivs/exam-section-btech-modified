from inspect import currentframe
from telnetlib import STATUS
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q 
from superintendent.user_access_test import faculty_subject_assignment_access, faculty_assignment_status_access
from ExamStaffDB.models import FacultyInfo
from superintendent.constants import DEPT_DICT, ROMAN_TO_INT
from co_ordinator.forms import FacultySubjectAssignmentForm, FacultyAssignmentStatusForm
from co_ordinator.models import FacultyAssignment, StudentRegistrations, Subjects, RollLists
from hod.models import Coordinator
from superintendent.models import HOD, CycleCoordinator, RegistrationStatus


@login_required(login_url="/login/")
@user_passes_test(faculty_subject_assignment_access)
def faculty_subject_assignment(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Co-ordinator' in groups:
        current_user = Coordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        valid_subjects = Subjects.objects.filter(OfferedBy=current_user.Dept, RegEventId__BYear=current_user.BYear)
        regular_regIDs = valid_subjects.filter(RegEventId__Status=1, RegEventId__RegistrationStatus=1).values_list('RegEventId_id', flat=True)
        active_regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=current_user.BYear).exclude(Mode='R')
        other_regIDs = StudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
        regIDs = RegistrationStatus.objects.filter(Q(id__in=regular_regIDs)|Q(id__in=other_regIDs))
    elif 'HOD' in groups:
        current_user = HOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        valid_subjects = Subjects.objects.filter(OfferedBy=current_user.Dept, RegEventId__BYear=1)
        regular_regIDs = valid_subjects.filter(RegEventId__Status=1, RegEventId__RegistrationStatus=1).values_list('RegEventId_id', flat=True)
        active_regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=1).exclude(Mode='R')
        other_regIDs = StudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
        regIDs = RegistrationStatus.objects.filter(Q(id__in=regular_regIDs)|Q(id__in=other_regIDs))
    if(request.method =='POST'):
        form = FacultySubjectAssignmentForm(regIDs, request.POST)
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
                subjects = Subjects.objects.filter(RegEventId_id=regEventId.id, OfferedBy=current_user.Dept)
            else:
                student_Registrations = StudentRegistrations.objects.filter(RegEventId=regEventId.id).values_list('sub_id', flat=True)
                subjects = Subjects.objects.filter(OfferedBy=current_user.Dept, id__in=student_Registrations.values_list('sub_id', flat=True))
            request.session['currentRegEvent']=regEventId.id
            return render(request, 'co_ordinator/FacultyAssignment.html', {'form': form, 'subjects':subjects})
    else:
        form = FacultySubjectAssignmentForm(regIDs)
    return render(request, 'co_ordinator/FacultyAssignment.html',{'form':form})

@login_required(login_url="/login/")
@user_passes_test(faculty_subject_assignment_access)
def faculty_subject_assignment_detail(request, pk):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        current_user = Coordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
    elif 'HOD' in groups:
        current_user = HOD.objects.filter(User=user, RevokeDate__isnull=True).first()
    subject = Subjects.objects.get(id=pk)
    faculty = FacultyInfo.objects.filter(Dept=current_user.Dept, Working=True)
    sections = RollLists.objects.filter(RegEventId_id=request.session.get('currentRegEvent')).values_list('Section', flat=True).distinct()
    faculty_assigned = FacultyAssignment.objects.filter(Subject=subject, RegEventId_id=request.session.get('currentRegEvent'))
    co_ordinator=''
    if faculty_assigned:
        co_ordinator = faculty_assigned[0].Coordinator_id
    for fac in faculty:
        if faculty_assigned.filter(Faculty=fac).exists():
            fac.Section = []
            for fac_assign in faculty_assigned.filter(Faculty=fac):
                fac.Section.append(fac_assign.Section)
    
    if request.method == 'POST':
        for sec in sections:
            if request.POST.get('faculty-'+str(sec)):
                if faculty_assigned and faculty_assigned.get(Section=sec):
                    faculty_row = faculty_assigned.get(Section=sec)
                    faculty_row.co_ordinator_id = request.POST.get('course-coordinator') or 0
                    faculty_row.faculty_id = request.POST.get('faculty-'+str(sec))
                    faculty_row.save()
                else:
                    faculty_row = FacultyAssignment(Subject=subject, Coordinator_id=request.POST.get('course-coordinator'),\
                        Faculty_id=request.POST.get('faculty-'+str(sec)), Section=sec, RegEventId_id=request.session['currentRegEvent'])
                    faculty_row.save()
        return redirect('FacultySubjectAssignment')
    return render(request, 'co_ordinator/FacultyAssignmentdetail.html', {'subject':subject, 'faculty':faculty,\
        'section':sections, 'co_ordinator':co_ordinator, 'faculty_section':faculty_assigned})

@login_required(login_url="/login/")
@user_passes_test(faculty_assignment_status_access)
def faculty_assignment_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        current_user = Coordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        current_user.group = 'Co-ordinator'  
        valid_subjects = Subjects.objects.filter(OfferedBy=current_user.Dept, RegEventId__BYear=current_user.BYear)
        regular_regIDs = valid_subjects.filter(RegEventId__Status=1, RegEventId__RegistrationStatus=1).values_list('RegEventId_id', flat=True)
        active_regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=current_user.BYear).exclude(Mode='R')
        other_regIDs = StudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
        regIDs = RegistrationStatus.objects.filter(Q(id__in=regular_regIDs)|Q(id__in=other_regIDs))
    elif 'HOD' in groups:
        current_user = HOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        current_user.group = 'HOD'
        valid_subjects = Subjects.objects.filter(OfferedBy=current_user.Dept, RegEventId__BYear=1)
        regular_regIDs = valid_subjects.filter(RegEventId__Status=1, RegEventId__RegistrationStatus=1).values_list('RegEventId_id', flat=True)
        active_regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=1).exclude(Mode='R')
        other_regIDs = StudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
        regIDs = RegistrationStatus.objects.filter(Q(id__in=regular_regIDs)|Q(id__in=other_regIDs))
    elif 'Superintendent' in groups:
        current_user = user
        current_user.group = 'Superintendent'
        regIDs = RegistrationStatus.objects.filter(Status=1)
    elif 'Cycle-Co-ordinator' in groups:
        current_user = CycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        current_user.group = 'Cycle-Co-ordinator'
        regIDs = RegistrationStatus.objects.filter(Status=1, BYear=1, Dept=current_user.Cycle)
    else:
        raise Http404("You are not authorized to view this page")
    if(request.method =='POST'):
        form = FacultyAssignmentStatusForm(regIDs, request.POST)
        if(form.is_valid()):
            regeventid=form.cleaned_data['regID']
            if current_user.group == 'Superintendent':
                faculty = FacultyAssignment.objects.filter(RegEventId__id=regeventid)
            elif current_user.group == 'Co-ordinator' or current_user.group == 'HOD':
                faculty = FacultyAssignment.objects.filter(RegEventId__id=regeventid, Subject__OfferedBy=current_user.Dept)
            elif current_user.group == 'Cycle-Co-ordinator':
                faculty = FacultyAssignment.objects.filter(RegEventId__id=regeventid)
            return render(request, 'co_ordinator/FacultyAssignmentStatus.html',{'form':form, 'faculty':faculty})
    else:
        form = FacultyAssignmentStatusForm(regIDs)
    return render(request, 'co_ordinator/FacultyAssignmentStatus.html',{'form':form})