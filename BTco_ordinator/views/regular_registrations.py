from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from BTco_ordinator.forms import RegistrationsUploadForm, RegistrationsFinalizeEventForm
from ADAUGDB.models import BTRegistrationStatus, BTCourseStructure, BTCurriculumComponents
from ADAUGDB.models import BTCycleCoordinator
from BTco_ordinator.models import BTRollLists_Staging, BTRollLists, BTStudentRegistrations_Staging, BTStudentRegistrations, BTSubjects, BTNotRegistered,\
    BTDroppedRegularCourses
from BThod.models import BTCoordinator
from django.db.models import Q
from django.db import transaction
from ADAUGDB.user_access_test import registration_access
from django.db.models import Sum, F


@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(registration_access)
def btech_regular_registration(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear, Mode='R')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1, Mode='R')
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
    if(request.method=='POST'):
        form = RegistrationsUploadForm(regIDs, request.POST)
        if(form.is_valid()):
            if(form.cleaned_data['regID']!='--Choose Event--'):
                (ayear,asem,byear,bsem,dept,mode, regulation) = regIDs[int(form.cleaned_data['regID'])]
                event = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation).first()
                not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem,\
                    Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
                mode = 1
                if(byear==1):
                    rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__in=not_registered_students.values_list('Student', flat=True))
                    if len(rolls)==0:
                        msg = 'There is no roll list for the selected registration event.'
                        return render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
                    subs = BTSubjects.objects.filter(~Q(course__CourseStructure__Category__in=['OEC', 'OPC', 'DEC']),RegEventId=event)
                    if len(subs)==0:
                        msg = 'There are no subjects for the selected registration event.'
                        return render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
                    initial_registrations = BTStudentRegistrations_Staging.objects.filter(RegEventId_id=event.id, Mode=1)
                    for roll in rolls:
                        for sub in subs:
                            if not initial_registrations.filter(student=roll, sub_id_id=sub.id).exists():
                                regRow = BTStudentRegistrations_Staging(student=roll, Mode=mode, RegEventId_id=event.id, sub_id_id=sub.id)
                                regRow.save()
                    BTStudentRegistrations_Staging.objects.filter(~Q(student__student__RegNo__in=rolls.values_list('student__RegNo', flat=True)), RegEventId_id=event.id).delete()
                    msg = 'Your data upload for Student Registrations has been done successfully.'
                    return render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
                else:
                    rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__in=not_registered_students.values_list('Student', values=True))
                    if len(rolls)==0:
                        msg = 'There is no roll list for the selected registration event.'
                        return render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html', {'msg':msg})
                    subs = BTSubjects.objects.filter(~Q(course__CourseStructure__Category__in=['OEC', 'OPC', 'DEC']),RegEventId=event)
                    if len(subs)==0:
                        msg = 'There are no subjects for the selected registration event.'
                        return render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html', {'msg':msg})
                    initial_registrations = BTStudentRegistrations_Staging.objects.filter(RegEventId_id=event.id, Mode=1)
                    for roll in rolls:
                        for sub in subs:
                            if not initial_registrations.filter(student=roll, sub_id_id=sub.id).exists():
                                regRow = BTStudentRegistrations_Staging(student=roll, Mode=mode, RegEventId_id=event.id, sub_id_id=sub.id)
                                regRow.save()
                    msg = 'Your data upload for Student Registrations has been done successfully.'
                    BTStudentRegistrations_Staging.objects.filter(~Q(student__student__RegNo__in=rolls.values_list('student__RegNo', flat=True)), RegEventId_id=event.id).delete()
                    return render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
    else:
        form = RegistrationsUploadForm(Options=regIDs)
    return(render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html',{'form':form }))

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(registration_access)
def registrations_finalize(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=0, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=0, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1)
    if(request.method=='POST'):
        form = RegistrationsFinalizeEventForm(regIDs, request.POST)
        if(form.is_valid()):
            currentRegEvent = BTRegistrationStatus.objects.filter(id=form.cleaned_data.get('regID')).first()
            currentRegEventId = currentRegEvent.id
            rolllist = BTRollLists.objects.filter(RegEventId_id=currentRegEventId)
            execess_credits_students = []
            insuff_credits_students = []
            regs = BTStudentRegistrations_Staging.objects.filter(student__student__id__in=rolllist.values_list('student_id',flat=True), \
                RegEventId__AYear=currentRegEvent.AYear, RegEventId__ASem=currentRegEvent.ASem, RegEventId__BYear=currentRegEvent.BYear,\
                RegEventId__Dept=currentRegEvent.Dept)
            regulation_curriculum = BTCourseStructure.objects.filter(Regulation=currentRegEvent.Regulation)
            regulation_curriculum_components = BTCurriculumComponents.objects.filter(Regulation=currentRegEvent.Regulation)
            for roll in rolllist:
                curriculum = regulation_curriculum.filter(Dept=currentRegEvent.Dept)
                byear_curriculum = curriculum.filter(BYear=currentRegEvent.BYear, BSem=currentRegEvent.BSem)
                curriculum_components = regulation_curriculum_components.filter(Dept=roll.student.Dept)
                study_credits = regs.filter(student__student=roll.student, Mode=1).aggregate(Sum('sub_id__course__CourseStructure__Credits')).get('sub_id__course__CourseStructure__Credits__sum') or 0
                exam_credits = regs.filter(student__student=roll.student, Mode=0).aggregate(Sum('sub_id__course__CourseStructure__Credits')).get('sub_id__course__CourseStructure__Credits__sum') or 0
                
                if study_credits > 32 or (study_credits+exam_credits) > 34:
                    roll.study = study_credits
                    roll.exam = exam_credits
                    execess_credits_students.append(roll)
                if currentRegEvent.Mode == 'R':
                    dropped_courses = BTDroppedRegularCourses.objects.filter(student=roll.student, Registered=False)
                    relevant_dropped_courses = dropped_courses.filter(RegEventId__AYear=currentRegEvent.AYear, RegEventId__ASem=currentRegEvent.ASem, RegEventId__BYear=currentRegEvent.BYear, RegEventId__Dept=currentRegEvent.Dept, RegEventId__Regulation=currentRegEvent.Regulation, RegEventId__Mode='R')
                
                    student_regs = regs.filter(student_id=roll.id)
                    for cs in byear_curriculum:
                        cs_regs = student_regs.filter(sub_id__course__CourseStructure_id=cs.id)
                        cs_count = cs_regs.count()
                        cs_credits_count = cs_regs.aggregate(Sum('sub_id__course__CourseStructure__Credits')).get('sub_id__course__CourseStructure__Credits__sum') or 0
                        dropped_cs_regs = relevant_dropped_courses.filter(subject__course__CourseStructure_id=cs.id)
                        dropped_cs_count = dropped_cs_regs.count()
                        dropped_cs_credits_count = dropped_cs_regs.aggregate(Sum('subject__course__CourseStructure__Credits')).get('subject__course__CourseStructure__Credits__sum') or 0
                        if (dropped_cs_count+cs_count) != cs.count:
                            category_regs_credits_count = BTStudentRegistrations.objects.filter(sub_id__course__CourseStructure__Category=cs.Category, RegEventId__Mode='R').exclude(RegEventId__AYear=currentRegEvent.AYear, RegEventId__ASem=currentRegEvent.ASem, RegEventId__BYear=currentRegEvent.BYear, sub_id__course__CourseStructure_id=cs.id).\
                                aggregate(Sum('sub_id__course__CourseStructure__Credits')).get('sub_id__course__CourseStructure__Credits__sum') or 0
                            category_dropped_regs_credits_count = dropped_courses.filter(subject__course__CourseStructure__Category=cs.Category).exclude(RegEventId__AYear=currentRegEvent.AYear, RegEventId__ASem=currentRegEvent.ASem, RegEventId__BYear=currentRegEvent.BYear, subject__course__CourseStructure_id=cs.id).\
                                aggregate(Sum('subject__course__CourseStructure__Credits')).get('subject__course__CourseStructure__Credits__sum') or 0
                            upcoming_cs = curriculum.filter(BYear__gt=currentRegEvent.BYear, Category=cs.Category).aggregate(credits=Sum(F('Credits')*F('count'))).get('credits') or 0
                            if currentRegEvent.ASem == 1:
                                upcoming_cs += curriculum.filter(BYear=currentRegEvent.BYear, BSem=2, Category=cs.Category).aggregate(credits=Sum(F('Credits')*F('count'))).get('credits') or 0
                            total_credits = category_dropped_regs_credits_count+category_regs_credits_count+cs_credits_count+dropped_cs_credits_count+upcoming_cs
                            if total_credits < curriculum_components.filter(Category=cs.Category).first().MinimumCredits or \
                                total_credits > curriculum_components.filter(Category=cs.Category).first().CreditsOffered:
                                insuff_credits_students.append(roll)
                                break
            if execess_credits_students or insuff_credits_students:
                return render(request, 'BTco_ordinator/BTRegistrationsFinalize.html',{'form':form, 'excess_credits':execess_credits_students, 'insuff_credits':insuff_credits_students})
            regs = regs.filter(RegEventId=currentRegEventId).exclude(sub_id__course__CourseStructure__Category__in=['OEC', 'OPC'])
            for reg in regs:
                roll = rolllist.filter(student=reg.student.student).first()
                if not BTStudentRegistrations.objects.filter(student=roll, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id).exists():
                    s=BTStudentRegistrations(student=roll, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id)
                    s.save()
            currentRegEvent.RegistrationStatus = 0
            oesubs = BTSubjects.objects.filter(RegEventId=currentRegEventId,course__CourseStructure__Category__in=['OEC','OPC'])
            if len(oesubs) == 0:
                currentRegEvent.OERegistrationStatus=0
            currentRegEvent.save()
            return render(request, 'BTco_ordinator/BTRegistrationsFinalizeSuccess.html')
    else:
        form = RegistrationsFinalizeEventForm(regIDs)
    return render(request, 'BTco_ordinator/BTRegistrationsFinalize.html',{'form':form})
    
def regular_regs_script(kwargs):
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    events = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'), BSem__in=kwargs.get('BSem'),\
        Regulation__in=kwargs.get('Regulation'), Dept__in=kwargs.get('Dept'), Mode__in=kwargs.get('Mode'))
    for event in events:
        not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem,\
            Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
        mode = 1
        if(event.BYear==1):
            rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__in=not_registered_students.values_list('Student', flat=True))
            if len(rolls)==0:
                msg = 'There is no roll list for the selected registration event.'
                return msg
            subs = BTSubjects.objects.filter(~Q(course__CourseStructure__Category__in=['OEC', 'OPC', 'DEC']),RegEventId=event)
            if len(subs)==0:
                msg = 'There are no subjects for the selected registration event.'
                return msg
            initial_registrations = BTStudentRegistrations_Staging.objects.filter(RegEventId_id=event.id, Mode=1)
            for roll in rolls:
                for sub in subs:
                    if not initial_registrations.filter(student=roll, sub_id_id=sub.id).exists():
                        regRow = BTStudentRegistrations_Staging(student=roll, Mode=mode, RegEventId_id=event.id, sub_id_id=sub.id)
                        regRow.save()
            BTStudentRegistrations_Staging.objects.filter(~Q(student__student__RegNo__in=rolls.values_list('student__RegNo', flat=True)), RegEventId_id=event.id).delete()
            msg = 'Your data upload for Student Registrations has been done successfully.'
            return msg
        else:
            rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__in=not_registered_students.values_list('Student', values=True))
            if len(rolls)==0:
                msg = 'There is no roll list for the selected registration event.'
                return msg
            subs = BTSubjects.objects.filter(~Q(course__CourseStructure__Category__in=['OEC', 'OPC', 'DEC']),RegEventId=event)
            if len(subs)==0:
                msg = 'There are no subjects for the selected registration event.'
                return msg
            initial_registrations = BTStudentRegistrations_Staging.objects.filter(RegEventId_id=event.id, Mode=1)
            for roll in rolls:
                for sub in subs:
                    if not initial_registrations.filter(student=roll, sub_id_id=sub.id).exists():
                        regRow = BTStudentRegistrations_Staging(student=roll, Mode=mode, RegEventId_id=event.id, sub_id_id=sub.id)
                        regRow.save()
            msg = 'Your data upload for Student Registrations has been done successfully.'
            BTStudentRegistrations_Staging.objects.filter(~Q(student__student__RegNo__in=rolls.values_list('student__RegNo', flat=True)), RegEventId_id=event.id).delete()
            return msg

def registrations_finalize_script(kwargs):
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    events = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'), BSem__in=kwargs.get('BSem'),\
        Regulation__in=kwargs.get('Regulation'), Dept__in=kwargs.get('Dept'), Mode__in=kwargs.get('Mode'))
    for event in events:
        print(event.__dict__)
        regs = BTStudentRegistrations_Staging.objects.filter(RegEventId=event.id).exclude(sub_id__course__CourseStructure__Category__in=['OEC', 'OPC', 'DEC'])
        rolllist = BTRollLists.objects.filter(RegEventId_id=event.id)
        for reg in regs:
            roll = rolllist.filter(student=reg.student.student).first()
            if not BTStudentRegistrations.objects.filter(student=roll, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id).exists():
                s=BTStudentRegistrations(student=roll, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id)
                s.save()
        event.RegistrationStatus = 0 
        oesubs = BTSubjects.objects.filter(RegEventId=event.id,course__CourseStructure__Category__in=['OEC','OPC'])
        if len(oesubs) == 0:
            event.OERegistrationStatus=0
        event.save()
    return "done"
