from django.shortcuts import render
from MTsuperintendent.models import MTCancelledStudentInfo,MTCancelledStudentGrades,MTCancelledNotRegistered,MTCancelledRollLists,MTCancelledStudentRegistrations,MTCancelledMarks
from MTco_ordinator.models import MTNotRegistered,MTRollLists,MTRollLists_Staging,MTStudentRegistrations,MTStudentRegistrations_Staging
from MTExamStaffDB.models import MTStudentInfo
from MTfaculty.models import MTStudentGrades,MTMarks,MTMarks_Staging,MTStudentGrades_Staging
from MTsuperintendent.forms import StudentCancellationForm
from SupExamDB.views import is_Superintendent
from django.contrib.auth.decorators import login_required, user_passes_test 
    

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def seat_cancellation(request):
    studentInfo = []
    if(request.method=='POST'):
        form = StudentCancellationForm(request.POST)
        if(form.is_valid()):
            regno = int(form.cleaned_data['RegNo'])
            studentInfo = MTStudentInfo.objects.filter(RegNo=regno)
            context = {'form':form}
            if(len(studentInfo)!=0):
                student=studentInfo.first()
                context['RegNo'] = studentInfo[0].RegNo
                context['Name'] = studentInfo[0].Name
                notregistered =MTNotRegistered.objects.filter(Student_id=student.id)
                rolls= MTRollLists.objects.filter(student_id=student.id)
                regs =MTStudentRegistrations.objects.filter(RegNo=regno)
                grades =MTStudentGrades.objects.filter(RegId__in = regs.values_list('id',flat =True))
                marks = MTMarks.objects.filter(Registration__in = regs)

                MTCancelledStudentInfo(RegNo=student.RegNo,Name=student.Name,Regulation=student.Regulation,Dept=student.Dept,AdmissionYear=student.AdmissionYear,Gender=student.Gender,Category=student.Category,GuardianName=student.GuardianName,Phone=student.Phone,email=student.email,Address1=student.Address1,Address2=student.Address2).save()
                for i in rolls:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    i_dict.pop('_state')
                    MTCancelledRollLists.objects.create(**i_dict)
                for i in notregistered:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    i_dict.pop('id') 
                    MTCancelledNotRegistered.objects.create(**i_dict)
                for i in regs:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    i_dict.pop('_state')
                    MTCancelledStudentRegistrations.objects.create(**i_dict)
                    
                for i in marks:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    i_dict.pop('_state')
                    MTCancelledMarks.objects.create(**i_dict)
                for i in grades:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    i_dict.pop('_state')
                    MTCancelledStudentGrades.objects.create(**i_dict)


                MTMarks_Staging.objects.filter(Registration__in = regs).delete()
                MTRollLists_Staging.objects.filter(student_id=student.id).delete()
                MTStudentGrades_Staging.objects.filter(RegId__in=regs.values_list('id',flat =True)).delete()
                MTStudentRegistrations_Staging.objects.filter(Regno=regno).delete()
                marks.delete()
                grades.delete()
                regs.delete()
                rolls.delete()
                notregistered.delete()

            return render(request,'superintendent/BTStudentCancellation.html',context)

    else:
        form = StudentCancellationForm()
    context = {'form':form}
    return render(request,'superintendent/BTStudentCancellation.html',context)

