from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q 
from MTsuperintendent.user_access_test import faculty_subject_assignment_access, faculty_assignment_status_access
from MTExamStaffDB.models import MTFacultyInfo
from MTsuperintendent.constants import DEPT_DICT, ROMAN_TO_INT
from MTco_ordinator.forms import FacultySubjectAssignmentForm, FacultyAssignmentStatusForm
from MTco_ordinator.models import MTFacultyAssignment, MTStudentRegistrations, MTSubjects, MTRollLists
from MThod.models import MTCoordinator
from MTsuperintendent.models import MTHOD, MTRegistrationStatus


@login_required(login_url="/login/")
@user_passes_test(faculty_subject_assignment_access)
def faculty_subject_assignment(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Co-ordinator' in groups:
        current_user = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        valid_subjects = MTSubjects.objects.filter(OfferedBy=current_user.Dept, RegEventId__MYear=current_user.MYear)
        regular_regIDs = valid_subjects.filter(RegEventId__Status=1).values_list('RegEventId_id', flat=True)
        active_regIDs = MTRegistrationStatus.objects.filter(Status=1, MYear=current_user.MYear).exclude(Mode='R')
        other_regIDs = MTStudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
        regIDs = MTRegistrationStatus.objects.filter(Q(id__in=regular_regIDs)|Q(id__in=other_regIDs))
    elif 'HOD' in groups:
        current_user = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        valid_subjects = MTSubjects.objects.filter(OfferedBy=current_user.Dept, RegEventId__MYear=1)
        regular_regIDs = valid_subjects.filter(RegEventId__Status=1).values_list('RegEventId_id', flat=True)
        active_regIDs = MTRegistrationStatus.objects.filter(Status=1, MYear=1).exclude(Mode='R')
        other_regIDs = MTStudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
        regIDs = MTRegistrationStatus.objects.filter(Q(id__in=regular_regIDs)|Q(id__in=other_regIDs))
    if(request.method =='POST'):
        form = FacultySubjectAssignmentForm(regIDs, request.POST)
        if(form.is_valid()):
            regEvent=form.cleaned_data['regID']
            event_string = regEvent.split(':')
            dept = DEPT_DICT[event_string[0]]
            ayear = int(event_string[3])
            asem = int(event_string[4])
            myear = ROMAN_TO_INT[event_string[1]]
            msem = ROMAN_TO_INT[event_string[2]]
            regulation = int(event_string[5])
            mode = event_string[6]
            regEventId = MTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,MYear=myear,MSem=msem,\
                    Dept=dept,Mode=mode,Regulation=regulation).first()
            if mode == 'R':
                subjects = MTSubjects.objects.filter(RegEventId_id=regEventId.id, OfferedBy=current_user.Dept)
            else:
                student_Registrations = MTStudentRegistrations.objects.filter(RegEventId=regEventId.id).values_list('sub_id', flat=True)
                subjects = MTSubjects.objects.filter(OfferedBy=current_user.Dept, id__in=student_Registrations.values_list('sub_id', flat=True))
            request.session['currentRegEvent']=regEventId.id
            return render(request, 'co_ordinator/FacultyAssignment.html', {'form': form, 'subjects':subjects})
    else:
        form = FacultySubjectAssignmentForm(regIDs)
    return render(request, 'co_ordinator/FacultyAssignment.html',{'form':form})

@login_required(login_url="/login/")
@user_passes_test(faculty_assignment_status_access)
def faculty_subject_assignment_detail(request, pk):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        current_user = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
    elif 'HOD' in groups:
        current_user = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
    subject = MTSubjects.objects.get(id=pk)
    faculty = MTFacultyInfo.objects.filter(Dept=current_user.Dept, Working=True)
    # sections = MTRollLists.objects.filter(RegEventId_id=request.session.get('currentRegEvent')).values_list('Section', flat=True).distinct()
    faculty_assigned = MTFacultyAssignment.objects.filter(Subject=subject, RegEventId_id=request.session.get('currentRegEvent'))
    co_ordinator=''
    faculty_selected = ''
    if faculty_assigned:
        co_ordinator = faculty_assigned[0].Coordinator_id
        faculty_selected = faculty_assigned[0].Faculty.id
    # for fac in faculty:
    #     if faculty_assigned.filter(Faculty=fac).exists():
    #         fac.Section = []
    #         for fac_assign in faculty_assigned.filter(Faculty=fac):
    #             fac.Section.append(fac_assign.Section)
    
    if request.method == 'POST':
        if request.POST.get('faculty'):
            if faculty_assigned:
                # faculty_row = MTFacultyAssignment.objects.filter(Subject=subject, RegEventId_id=request.session.get('currentRegEvent')).first()
                faculty_row = faculty_assigned.first()
                faculty_row.Coordinator_id = request.POST.get('course-coordinator') or 0
                faculty_row.Faculty_id = request.POST.get('faculty')
                faculty_row.save()
            else:
                faculty_row = MTFacultyAssignment(Subject=subject, Coordinator_id=request.POST.get('course-coordinator'),\
                    Faculty_id=request.POST.get('faculty'), RegEventId_id=request.session['currentRegEvent'])
                faculty_row.save()
        return redirect('MTFacultySubjectAssignment')
    return render(request, 'co_ordinator/FacultyAssignmentdetail.html', {'subject':subject, 'faculty':faculty,\
        'co_ordinator':co_ordinator, 'faculty_id':faculty_selected})

@login_required(login_url="/login/")
@user_passes_test(faculty_assignment_status_access)
def faculty_assignment_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        current_user = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        current_user.group = 'Co-ordinator'  
        valid_subjects = MTSubjects.objects.filter(OfferedBy=current_user.Dept, RegEventId__MYear=current_user.MYear)
        regular_regIDs = valid_subjects.filter(RegEventId__Status=1).values_list('RegEventId_id', flat=True)
        active_regIDs = MTRegistrationStatus.objects.filter(Status=1, MYear=current_user.MYear).exclude(Mode='R')
        other_regIDs = MTStudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
        regIDs = MTRegistrationStatus.objects.filter(Q(id__in=regular_regIDs)|Q(id__in=other_regIDs))
    elif 'HOD' in groups:
        current_user = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        current_user.group = 'HOD'
        valid_subjects = MTSubjects.objects.filter(OfferedBy=current_user.Dept, RegEventId__MYear=1)
        regular_regIDs = valid_subjects.filter(RegEventId__Status=1).values_list('RegEventId_id', flat=True)
        active_regIDs = MTRegistrationStatus.objects.filter(Status=1, MYear=1).exclude(Mode='R')
        other_regIDs = MTStudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
        regIDs = MTRegistrationStatus.objects.filter(Q(id__in=regular_regIDs)|Q(id__in=other_regIDs))
    elif 'Superintendent' in groups:
        current_user = user
        current_user.group = 'Superintendent'
        regIDs = MTRegistrationStatus.objects.filter(Status=1)
    # elif 'Cycle-Co-ordinator' in groups:
    #     current_user = MTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
    #     current_user.group = 'Cycle-Co-ordinator'
    #     regIDs = MTRegistrationStatus.objects.filter(Status=1, MYear=1, Dept=current_user.Cycle)
    else:
        raise Http404("You are not authorized to view this page")
    if(request.method =='POST'):
        form = FacultyAssignmentStatusForm(regIDs, request.POST)
        if(form.is_valid()):
            regeventid=form.cleaned_data['regID']
            if current_user.group == 'Superintendent':
                faculty = MTFacultyAssignment.objects.filter(RegEventId__id=regeventid)
            elif current_user.group == 'Co-ordinator' or current_user.group == 'HOD':
                faculty = MTFacultyAssignment.objects.filter(RegEventId__id=regeventid, Subject__OfferedBy=current_user.Dept)
            # elif current_user.group == 'Cycle-Co-ordinator':
            #     faculty = MTFacultyAssignment.objects.filter(Subject__RegEventId__id=regeventid)
            return render(request, 'co_ordinator/FacultyAssignmentStatus.html',{'form':form, 'faculty':faculty})
    else:
        form = FacultyAssignmentStatusForm(regIDs)
    return render(request, 'co_ordinator/FacultyAssignmentStatus.html',{'form':form})
