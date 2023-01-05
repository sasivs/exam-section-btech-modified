from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from ADAUGDB.user_access_test import registration_access
from BThod.models import BTCoordinator
from ADAUGDB.models import BTRegistrationStatus, BTCycleCoordinator, BTCourseStructure, BTCurriculumComponents
from BTco_ordinator.forms import CheckRegistrationsFinalizeForm
from BTco_ordinator.models import BTStudentRegistrations_Staging, BTStudentRegistrations, BTDroppedRegularCourses, BTRollLists_Staging
from django.db import transaction
from django.db.models import Sum, F

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(registration_access)
def check_registrations_finalize(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    modes = None
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=0, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=0, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1)
    if(request.method=='POST'):
        form = CheckRegistrationsFinalizeForm(regIDs, request.POST)
        if request.POST.get('regID'):
            if request.POST.get('excess_credits_RegNo'):
                byear = int(request.POST.get('regID').split(':')[0])
                ayear = int(request.POST.get('regID').split(':')[1])
                asem = int(request.POST.get('regID').split(':')[2])
                dept = int(request.POST.get('regID').split(':')[3])
                regulation = float(request.POST.get('regID').split(':')[4])
                registrations = BTStudentRegistrations_Staging.objects.filter(RegEventId__BYear=byear, RegEventId__AYear=ayear, RegEventId__ASem=asem, RegEventId__Dept=dept, \
                    RegEventId__Regulation=regulation, student__student__id=request.POST.get('excess_credits_RegNo'))
                mode_selection = {'RadioMode'+str(reg.sub_id_id): reg.Mode for reg in registrations}
                from json import dumps
                modes = dumps(mode_selection)
                if request.POST.get('submit-form'):
                    if form.is_valid():
                        exam_mode = 0 
                        study_mode = 0
                        for sub in form.myFields:
                            if form.cleaned_data.get('Check'+str(sub[6])):
                                if form.cleaned_data.get('RadioMode'+str(sub[6])) != '':
                                    if form.cleaned_data.get('RadioMode'+str(sub[6])):
                                        study_mode += sub[2]
                                    else:
                                        exam_mode += sub[2]
                                else:
                                    return render(request, 'BTco_ordinator/BTCheckRegistrationsFinalize.html', {'form':form, 'msg':2, 'modes':modes})
                        
                        if study_mode <= 32 and (study_mode+exam_mode)<=34:
                            for sub in form.myFields:
                                if sub[5] == 'R':
                                    if not form.cleaned_data.get('Check'+str(sub[6])):
                                        registration = BTStudentRegistrations_Staging.objects.filter(id=sub[8]).first()
                                        if registration:
                                            dropped_course = BTDroppedRegularCourses(student_id=form.cleaned_data.get('excess_credits_RegNo'), subject_id=registration.sub_id_id, RegEventId_id=registration.RegEventId_id, Registered=False)
                                            dropped_course.save()
                                            BTStudentRegistrations_Staging.objects.filter(id=sub[8]).delete()
                                elif sub[5] == 'B':
                                    if not form.cleaned_data.get('Check'+str(sub[6])):
                                        BTStudentRegistrations_Staging.objects.filter(id=sub[8]).delete()
                                    else:
                                        BTStudentRegistrations_Staging.objects.filter(id=sub[8]).update(Mode=form.cleaned_data.get('RadioMode'+str(sub[6])))
                                elif sub[5] == 'D':
                                    if form.cleaned_data.get('Check'+str(sub[6])):
                                        dropped_course = BTDroppedRegularCourses.objects.filter(id=sub[8]).first()
                                        roll = BTRollLists_Staging.objects.filter(student__student__id=dropped_course.student.id, RegEventId_id=dropped_course.RegEventId.id).first()
                                        new_registration = BTStudentRegistrations_Staging(student=roll, sub_id_id=dropped_course.subject.id, Mode=1, RegEventId_id=dropped_course.RegEventId.id)
                                        new_registration.save()
                                        dropped_course.delete()
                            form = CheckRegistrationsFinalizeForm(regIDs)
                            return render(request, 'BTco_ordinator/BTCheckRegistrationsFinalize.html', {'form':form, 'msg':3})
                        else:
                            return render(request, 'BTco_ordinator/BTCheckRegistrationsFinalize.html', {'form':form, 'msg':1, 'study':study_mode, 'exam':exam_mode, 'modes':modes})
            elif request.POST.get('insuff_credits_RegNo'):
                byear = int(request.POST.get('regID').split(':')[0])
                ayear = int(request.POST.get('regID').split(':')[1])
                asem = int(request.POST.get('regID').split(':')[2])
                dept = int(request.POST.get('regID').split(':')[3])
                regulation = float(request.POST.get('regID').split(':')[4])
                registrations = BTStudentRegistrations_Staging.objects.filter(RegEventId__BYear=byear, RegEventId__AYear=ayear, RegEventId__ASem=asem, RegEventId__Dept=dept, \
                    RegEventId__Regulation=regulation, student__student__id=request.POST.get('insuff_credits_RegNo'))
                mode_selection = {'RadioMode'+str(reg.sub_id_id): reg.Mode for reg in registrations}
                from json import dumps
                modes = dumps(mode_selection)
                if request.POST.get('submit-form'):
                    if form.is_valid():

                        roll = BTRollLists_Staging.objects.filter(id=form.cleaned_data.get('insuff_credits_RegNo'), RegEventId__BYear=byear, RegEventId__AYear=ayear, \
                            RegEventId__ASem=asem, RegEventId__Dept=dept, RegEventId__BSem=asem, RegEventId__Regulation=regulation, RegEventId__Mode='R').first()
                        for sub in form.myFields:
                            if sub[9] > sub[10]:
                                if not sub[8]:
                                    new_registration = BTStudentRegistrations_Staging(student=roll, RegEventId_id=roll.RegEventId_id, Mode=1, sub_id_id=sub[6])
                                    new_registration.save()
                            elif sub[9] < sub[10]:
                                if form.cleaned_data.get('Delete'+str(sub[6])):
                                    if sub[5] == 'R':
                                        BTStudentRegistrations_Staging.objects.filter(id=sub[8]).delete()
                                    elif sub[5] == 'D':
                                        BTDroppedRegularCourses.objects.filter(id=sub[8]).delete()
                        
                        curriculum = BTCourseStructure.objects.filter(Dept=roll.student.student.Dept, Regulation=regulation)
                        byear_curriculum = curriculum.filter(BYear=byear, BSem=asem)
                        registrations = BTStudentRegistrations_Staging.objects.filter(student_id=roll.id)
                        dropped_courses = BTDroppedRegularCourses.objects.filter(student=roll.student, Registered=False)
                        relevant_dropped_courses = dropped_courses.filter(RegEventId__AYear=ayear, RegEventId__ASem=asem, RegEventId__BYear=byear, RegEventId__Dept=dept, RegEventId__Regulation=regulation, RegEventId__Mode='R')
                        curriculum_components = BTCurriculumComponents.objects.filter(Dept=roll.student.student.Dept, Regulation=regulation)
                        
                        for cs in byear_curriculum:
                            cs_regs = registrations.filter(sub_id__course__CourseStructure_id=cs.id)
                            cs_count = cs_regs.count()
                            cs_credits_count = cs_regs.aggregate(Sum('sub_id__course__CourseStructure__Credits')).get('sub_id__course__CourseStructure__Credits__sum') or 0
                            dropped_cs_regs = relevant_dropped_courses.filter(subject__course__CourseStructure_id=cs.id)
                            dropped_cs_count = dropped_cs_regs.count()
                            dropped_cs_credits_count = dropped_cs_regs.aggregate(Sum('subject__course__CourseStructure__Credits')).get('subject__course__CourseStructure__Credits__sum') or 0
                            if (dropped_cs_count+cs_count) != cs.count:
                                category_regs_credits_count = BTStudentRegistrations.objects.filter(sub_id__course__CourseStructure__Category=cs.Category, RegEventId__Mode='R').exclude(RegEventId__AYear=ayear, RegEventId__ASem=asem, RegEventId__BYear=byear, sub_id__course__CourseStructure_id=cs.id).\
                                    aggregate(Sum('sub_id__course__CourseStructure__Credits')).get('sub_id__course__CourseStructure__Credits__sum') or 0
                                category_dropped_regs_credits_count = dropped_courses.filter(subject__course__CourseStructure__Category=cs.Category).exclude(RegEventId__AYear=ayear, RegEventId__ASem=asem, RegEventId__BYear=byear, subject__course__CourseStructure_id=cs.id).\
                                    aggregate(Sum('subject__course__CourseStructure__Credits')).get('subject__course__CourseStructure__Credits__sum') or 0
                                upcoming_cs = curriculum.filter(BYear__gt=byear, Category=cs.Category).aggregate(credits=Sum(F('Credits')*F('count'))).get('credits') or 0
                                if asem == 1:
                                    upcoming_cs += curriculum.filter(BYear=byear, BSem=2, Category=cs.Category).aggregate(credits=Sum(F('Credits')*F('count'))).get('credits') or 0
                                total_credits = category_dropped_regs_credits_count+category_regs_credits_count+cs_credits_count+dropped_cs_credits_count+upcoming_cs
                                if total_credits < curriculum_components.filter(Category=cs.Category).first().MinimumCredits or \
                                    total_credits > curriculum_components.filter(Category=cs.Category).first().CreditsOffered:
                                    form = CheckRegistrationsFinalizeForm(regIDs, request.POST)
                                    mode_selection = {'RadioMode'+str(reg.sub_id_id): reg.Mode for reg in registrations}
                                    from json import dumps
                                    modes = dumps(mode_selection)
                                    return render(request, 'BTco_ordinator/BTCheckRegistrationsFinalize.html', {'form':form, 'modes':modes})
                        return render(request, 'BTco_ordinator/BTCheckRegistrationsFinalizeSuccess.html')

    else:
        form = CheckRegistrationsFinalizeForm(regIDs)
    return render(request, 'BTco_ordinator/BTCheckRegistrationsFinalize.html',{'form':form, 'modes':modes})