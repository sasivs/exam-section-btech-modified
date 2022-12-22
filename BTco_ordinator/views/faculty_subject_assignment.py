from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q 
from ADAUGDB.user_access_test import faculty_subject_assignment_access, faculty_assignment_status_access
from BTExamStaffDB.models import BTFacultyInfo
from ADEUGDB.constants import DEPT_DICT, ROMAN_TO_INT
from BTco_ordinator.forms import FacultySubjectAssignmentForm, FacultyAssignmentStatusForm
from BTco_ordinator.models import BTFacultyAssignment, BTStudentRegistrations, BTSubjects, BTRollLists
from BThod.models import BTCoordinator
from ADAUGDB.models import BTRegistrationStatus
from ADAUGDB.models import BTHOD, BTCycleCoordinator, BTOpenElectiveRollLists
from django.db import transaction


@login_required(login_url="/login/")
@user_passes_test(faculty_subject_assignment_access)
def faculty_subject_assignment(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        current_user = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        current_user.group = 'Co-ordinator'
    elif 'HOD' in groups:
        current_user = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        current_user.group = 'HOD'
    if(request.method =='POST'):
        form = FacultySubjectAssignmentForm(current_user, request.POST)
        if(form.is_valid()):
            regEvent=form.cleaned_data['regID'].split(',')
            
            regEvents = BTRegistrationStatus.objects.filter(id__in=regEvent)
            if regEvents[0].Mode == 'R':
                subjects = BTSubjects.objects.filter(RegEventId_id__in=regEvents.filter(Mode='R').values_list('id', flat=True), course__OfferedBy=current_user.Dept)
                regular_subjects = subjects.exclude(course__CourseStructure__Category__in=['OEC', 'OPC'])
                oe_subjects = subjects.filter(course__CourseStructure__Category__in=['OEC', 'OPC'])
                distinct_oe_subjects = oe_subjects.distinct('course__SubCode')
                for sub in distinct_oe_subjects:
                    sub.id = '?'.join(list(map(str, oe_subjects.filter(course__SubCode=sub.course.SubCode).values_list('id', flat=True))))
                    sub.RegEventId = regEvent
                subjects = regular_subjects | distinct_oe_subjects 

            else:
                student_Registrations = BTStudentRegistrations.objects.filter(RegEventId_id_in=regEvent).values_list('sub_id_id', flat=True)
                subjects = BTSubjects.objects.filter(course__OfferedBy=current_user.Dept, id__in=student_Registrations)
                regular_subjects = subjects.exclude(course__CourseStructure__Category__in=['OEC', 'OPC'])
                oe_subjects = subjects.filter(course__CourseStructure__Category__in=['OEC', 'OPC'])
                distinct_oe_subjects = oe_subjects.distinct('course__SubCode')
                for sub in distinct_oe_subjects:
                    sub.id = '?'.join(oe_subjects.filter(course__SubCode=sub.course.SubCode).values_list('id', flat=True))
                    sub.RegEventId = regEvent
                subjects = regular_subjects | distinct_oe_subjects 
            request.session['currentRegEvent']=regEvent
            return render(request, 'BTco_ordinator/FacultyAssignment.html', {'form': form, 'subjects':subjects})
    else:
        form = FacultySubjectAssignmentForm(current_user)
    return render(request, 'BTco_ordinator/FacultyAssignment.html',{'form':form})

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(faculty_subject_assignment_access)
def faculty_subject_assignment_detail(request, pk):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        current_user = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
    elif 'HOD' in groups:
        current_user = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
    id_list = pk.split('?')
    subjects = BTSubjects.objects.filter(id__in=id_list)
    subject = subjects[0]
    faculty = BTFacultyInfo.objects.filter(Dept=current_user.Dept, Working=True)
    if not subjects[0].course.CourseStructure.Category in ['OEC', 'OPC']:
        sections = BTRollLists.objects.filter(RegEventId_id__in=request.session.get('currentRegEvent')).values_list('Section', flat=True).distinct().order_by('Section')
    else:
        sections = BTOpenElectiveRollLists.objects.filter(RegEventId_id__in=request.session.get('currentRegEvent')).values_list('Section', flat=True).distinct().order_by('Section')
    faculty_assigned = BTFacultyAssignment.objects.filter(Subject__in=subjects, RegEventId_id__in=request.session.get('currentRegEvent'))
    co_ordinator=''
    if faculty_assigned:
        co_ordinator = faculty_assigned[0].Coordinator_id
    for fac in faculty:
        if faculty_assigned.filter(Faculty=fac).exists():
            fac.Section = []
            for fac_assign in faculty_assigned.filter(Faculty=fac):
                fac.Section.append(fac_assign.Section)
    
    if request.method == 'POST':
        for subject in subjects:
            for event in request.session.get('currentRegEvent'):
                faculty_assigned_subject = faculty_assigned.filter(Subject=subject, RegEventId_id=event)
                for sec in sections:
                    if request.POST.get('faculty-'+str(sec)):
                        if faculty_assigned_subject and faculty_assigned_subject.get(Section=sec):
                            faculty_row = faculty_assigned_subject.get(Section=sec)
                            faculty_row.Coordinator_id = request.POST.get('course-coordinator') or 0
                            faculty_row.Faculty_id = request.POST.get('faculty-'+str(sec))
                            faculty_row.save()
                        else:
                            faculty_row = BTFacultyAssignment(Subject=subject, Coordinator_id=request.POST.get('course-coordinator'),\
                                Faculty_id=request.POST.get('faculty-'+str(sec)), Section=sec, RegEventId_id=event)
                            faculty_row.save()
        return redirect('BTFacultySubjectAssignment')
    return render(request, 'BTco_ordinator/FacultyAssignmentDetail.html', {'subject':subject, 'faculty':faculty,\
        'section':sections, 'co_ordinator':co_ordinator, 'faculty_section':faculty_assigned})

@login_required(login_url="/login/")
@user_passes_test(faculty_assignment_status_access)
def faculty_assignment_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        current_user = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        current_user.group = 'Co-ordinator'  
        valid_subjects = BTSubjects.objects.filter(course__OfferedBy=current_user.Dept, RegEventId__BYear=current_user.BYear)
        regular_regIDs = valid_subjects.filter(RegEventId__Status=1).values_list('RegEventId_id', flat=True)
        active_regIDs = BTRegistrationStatus.objects.filter(Status=1, BYear=current_user.BYear).exclude(Mode='R')
        other_regIDs = BTStudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
        regIDs = BTRegistrationStatus.objects.filter(Q(id__in=regular_regIDs)|Q(id__in=other_regIDs))
    elif 'HOD' in groups:
        current_user = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        current_user.group = 'HOD'
        valid_subjects = BTSubjects.objects.filter(course__OfferedBy=current_user.Dept)
        regular_regIDs = valid_subjects.filter(RegEventId__Status=1).values_list('RegEventId_id', flat=True)
        active_regIDs = BTRegistrationStatus.objects.filter(Status=1, BYear=1).exclude(Mode='R')
        other_regIDs = BTStudentRegistrations.objects.filter(RegEventId__in=active_regIDs.values_list('id', flat=True), sub_id__in=valid_subjects.values_list('id', flat=True)).values_list('RegEventId', flat=True)
        regIDs = BTRegistrationStatus.objects.filter(Q(id__in=regular_regIDs)|Q(id__in=other_regIDs))
    elif 'Superintendent' in groups:
        current_user = user
        current_user.group = 'Superintendent'
        regIDs = BTRegistrationStatus.objects.filter(Status=1)
    elif 'Associate-Dean-Academics' in groups or 'Associate-Dean-Exams' in groups:
        current_user = user
        current_user.group = 'Associate-Dean'
        regIDs = BTRegistrationStatus.objects.filter(Status=1)
    elif 'Cycle-Co-ordinator' in groups:
        current_user = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        current_user.group = 'Cycle-Co-ordinator'
        regIDs = BTRegistrationStatus.objects.filter(Status=1, BYear=1, Dept=current_user.Cycle)
    else:
        raise Http404("You are not authorized to view this page")
    if(request.method =='POST'):
        form = FacultyAssignmentStatusForm(regIDs, request.POST)
        if(form.is_valid()):
            regeventid=form.cleaned_data['regID']
            regEvent = BTRegistrationStatus.objects.filter(id=regeventid).first()
            if current_user.group == 'Superintendent' or current_user.group == 'Associate-Dean':
                faculty = BTFacultyAssignment.objects.filter(RegEventId__id=regeventid).order_by('Section')
            elif current_user.group == 'Co-ordinator' or current_user.group == 'HOD':
                if regEvent.Dept==current_user.Dept:
                    faculty = BTFacultyAssignment.objects.filter(RegEventId__id=regeventid).order_by('Section')
                else:
                    faculty = BTFacultyAssignment.objects.filter(RegEventId__id=regeventid, Subject__course__OfferedBy=current_user.Dept).order_by('Section')
            elif current_user.group == 'Cycle-Co-ordinator':
                faculty = BTFacultyAssignment.objects.filter(RegEventId__id=regeventid).order_by('Section')
            return render(request, 'BTco_ordinator/FacultyAssignmentStatus.html',{'form':form, 'faculty':faculty})
    else:
        form = FacultyAssignmentStatusForm(regIDs)
    return render(request, 'BTco_ordinator/FacultyAssignmentStatus.html',{'form':form})


def faculty_assignment(**kwargs):
    '''
    Dept can be given in the form of list consisting of departments.
    All the remaining arguments are not lists
    '''
    print(kwargs)
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    if kwargs.get('Mode') == 'R':
        regEvents = BTRegistrationStatus.objects.filter(AYear=kwargs.get('AYear'), ASem=kwargs.get('ASem'), BYear=kwargs.get('BYear'), BSem=kwargs.get('BSem'), \
            Regulation=kwargs.get('Regulation'), Mode=kwargs.get('Mode'))
        if not regEvents:
            return "No Events!!!!"
        depts = kwargs.get('Dept')
        if not kwargs.get('Dept') and kwargs.get('BYear')!=1:
            depts = [1,2,3,4,5,6,7,8]
        elif not kwargs.get('Dept') and kwargs.get('BYear')==1:
            depts = [9,10]
        for dept in depts:
            print(regEvents.filter(Dept=dept).first().__dict__)
            regEventId = regEvents.filter(Dept=dept).first().id
            dept_sub = BTSubjects.objects.filter(RegEventId_id=regEventId)
            for sub in dept_sub:
                print(sub.__dict__)
                offering_dept = sub.course.OfferedBy
                if offering_dept > 10: offering_dept -= 2
                print(offering_dept)
                fac_name = 'fac'+str(offering_dept)
                print(fac_name)
                fac_id = BTFacultyInfo.objects.filter(Name=fac_name).first()
                if not BTFacultyAssignment.objects.filter(Subject_id=sub.id, RegEventId_id=regEventId, Faculty_id=fac_id.id, Coordinator_id=fac_id.id).exists():
                    fac_assign_obj = BTFacultyAssignment(Subject_id=sub.id, RegEventId_id=regEventId, Faculty_id=fac_id.id, Coordinator_id=fac_id.id)
                    fac_assign_obj.save()
    elif kwargs.get('Mode') == 'M' or kwargs.get('Mode') == 'B':
        regEvents = BTRegistrationStatus.objects.filter(AYear=kwargs.get('AYear'), ASem=kwargs.get('ASem'), BYear=kwargs.get('BYear'), BSem=kwargs.get('BSem'), \
            Regulation=kwargs.get('Regulation'), Mode=kwargs.get('Mode'))
        if not regEvents:
            return "No Events!!!!"
        depts = kwargs.get('Dept')
        if not kwargs.get('Dept') and kwargs.get('BYear')!=1:
            depts = [1,2,3,4,5,6,7,8]
        elif not kwargs.get('Dept') and kwargs.get('BYear')==1:
            depts = [9,10]
        for dept in depts:
            print(regEvents.filter(Dept=dept).first().__dict__)
            regEventId = regEvents.filter(Dept=dept).first().id
            student_regs = BTStudentRegistrations.objects.filter(RegEventId_id=regEventId).distinct('sub_id_id')
            subjects = BTSubjects.objects.filter(id__in=student_regs.values_list('sub_id_id', flat=True))
            for sub in subjects:
                print(sub.__dict__)
                offering_dept = sub.course.OfferedBy
                if offering_dept > 10: offering_dept -= 2
                print(offering_dept)
                fac_name = 'fac'+str(offering_dept)
                print(fac_name)
                fac_id = BTFacultyInfo.objects.filter(Name=fac_name).first()
                if not BTFacultyAssignment.objects.filter(Subject_id=sub.id, RegEventId_id=regEventId, Faculty_id=fac_id.id, Coordinator_id=fac_id.id).exists():
                    fac_assign_obj = BTFacultyAssignment(Subject_id=sub.id, RegEventId_id=regEventId, Faculty_id=fac_id.id, Coordinator_id=fac_id.id)
                    fac_assign_obj.save()
    return "Completed!!!!"

