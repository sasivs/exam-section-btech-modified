from django.shortcuts import render
from ADAUGDB.models import BTCancelledStudentInfo,BTCancelledStudentGrades,BTCancelledDroppedRegularCourses,BTCancelledNotPromoted,BTCancelledNotRegistered,BTCancelledRollLists,BTCancelledStudentRegistrations,BTCancelledMarks
from BTco_ordinator.models import BTDroppedRegularCourses,BTNotPromoted,BTNotRegistered,BTRollLists,BTRollLists_Staging,BTStudentRegistrations,BTStudentRegistrations_Staging
from BTExamStaffDB.models import BTStudentInfo
from BTfaculty.models import BTStudentGrades,BTMarks,BTMarks_Staging,BTStudentGrades_Staging
from ADAUGDB.forms import StudentCancellationForm, StudentCancellationStatusForm
from ADAUGDB.user_access_test import seat_cancellation_status_access, is_Associate_Dean_Academics
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.db import transaction

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def seat_cancellation(request):
    studentInfo = []
    if(request.method=='POST'):
        form = StudentCancellationForm(request.POST)
        if(form.is_valid()):
            regno = int(form.cleaned_data['RegNo'])
            date = form.cleaned_data.get('Date')
            remark = form.cleaned_data.get('remark')
            studentInfo = BTStudentInfo.objects.filter(RegNo=regno)
            context = {'form':form}
            if(len(studentInfo)!=0):
                student=studentInfo.first()
                context['RegNo'] = studentInfo[0].RegNo
                context['Name'] = studentInfo[0].Name
                droppedregular= BTDroppedRegularCourses.objects.filter(student_id=student.id)
                notpromoted= BTNotPromoted.objects.filter(student_id=student.id)
                notregistered =BTNotRegistered.objects.filter(Student_id=student.id)
                rolls= BTRollLists.objects.filter(student_id=student.id)
                regs =BTStudentRegistrations.objects.filter(student__student__RegNo=regno)
                grades =BTStudentGrades.objects.filter(RegId_id__in = regs.values_list('id',flat =True))
                marks = BTMarks.objects.filter(Registration__in = regs)

                BTCancelledStudentInfo(id=student.id,Remarks=remark,CancelledDate=date,RegNo=student.RegNo,RollNo=student.RollNo,Name=student.Name,Regulation=student.Regulation,Dept=student.Dept,AdmissionYear=student.AdmissionYear,Gender=student.Gender,Category=student.Category,GuardianName=student.GuardianName,Phone=student.Phone,email=student.email,Address1=student.Address1,Address2=student.Address2,Cycle=student.Cycle).save()
                for i in rolls:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTCancelledRollLists.objects.create(**i_dict)
                for i in notregistered:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTCancelledNotRegistered.objects.create(**i_dict)
                for i in regs:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTCancelledStudentRegistrations.objects.create(**i_dict)
                for i in droppedregular:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTCancelledDroppedRegularCourses.objects.create(**i_dict)
                    
                for i in marks:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTCancelledMarks.objects.create(**i_dict)
                for i in grades:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTCancelledStudentGrades.objects.create(**i_dict)
                for i in notpromoted:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTCancelledNotPromoted.objects.create(**i_dict)



                BTMarks_Staging.objects.filter(Registration__in = regs).delete()
                BTRollLists_Staging.objects.filter(student_id=student.id).delete()
                BTStudentGrades_Staging.objects.filter(RegId_id__in = regs.values_list('id',flat =True)).delete()
                BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=regno).delete()
                marks.delete()
                grades.delete()
                regs.delete()
                rolls.delete()
                notregistered.delete()
                notpromoted.delete()
                droppedregular.delete()
                studentInfo.delete()


                    
                
            
            return render(request,'ADAUGDB/BTStudentCancellation.html',context)

    else:
        form = StudentCancellationForm()
    context = {'form':form}
    return render(request,'ADAUGDB/BTStudentCancellation.html',context)

@login_required(login_url="/login/")
@user_passes_test(seat_cancellation_status_access)
def seat_cancellation_status(request):
    if request.method == 'POST':
        form = StudentCancellationStatusForm(request.POST)
        if form.is_valid():
            ayear = form.cleaned_data.get('AYear')
            cancelled_students = BTCancelledStudentInfo.objects.filter(CancelledDate__year=ayear)
            return render(request, 'ADAUGDB/BTStudentCancellationStatus.html', {'form':form, 'cancelled_students':cancelled_students})
    else:
        form = StudentCancellationStatusForm()
    return render(request, 'ADAUGDB/BTStudentCancellationStatus.html', {'form':form})

