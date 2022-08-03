from django.shortcuts import render
from BTsuperintendent.models import BTCancelledStudentInfo,BTCancelledStudentGrades,BTCancelledDroppedRegularCourses,BTCancelledNotPromoted,BTCancelledNotRegistered,BTCancelledRollLists,BTCancelledStudentRegistrations,BTCancelledMarks
from BTco_ordinator.models import BTDroppedRegularCourses,BTNotPromoted,BTNotRegistered,BTRollLists,BTRollLists_Staging,BTStudentRegistrations,BTStudentRegistrations_Staging
from BTExamStaffDB.models import BTStudentInfo
from BTfaculty.models import BTStudentGrades,BTMarks,BTMarks_Staging,BTStudentGrades_Staging
from BTsuperintendent.forms import StudentCancellationForm
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
                regs =BTStudentRegistrations.objects.filter(RegNo=regno)
                grades =BTStudentGrades.objects.filter(RegId__in = regs.values_list('id',flat =True))
                marks = BTMarks.objects.filter(Registration__in = regs)

                BTCancelledStudentInfo(RegNo=student.RegNo,RollNo=student.RollNo,Name=student.Name,Regulation=student.Regulation,Dept=student.Dept,AdmissionYear=student.AdmissionYear,Gender=student.Gender,Category=student.Category,GuardianName=student.GuardianName,Phone=student.Phone,email=student.email,Address1=student.Address1,Address2=student.Address2,Cycle=student.Cycle).save()
                for i in rolls:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    i_dict.pop('_state')
                    BTCancelledRollLists.objects.create(**i_dict)
                for i in notregistered:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    i_dict.pop('id') 
                    BTCancelledNotRegistered.objects.create(**i_dict)
                for i in regs:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    i_dict.pop('_state')
                    BTCancelledStudentRegistrations.objects.create(**i_dict)
                for i in droppedregular:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    i_dict.pop('_state')
                    BTCancelledDroppedRegularCourses.objects.create(**i_dict)
                    
                for i in marks:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    i_dict.pop('_state')
                    BTCancelledMarks.objects.create(**i_dict)
                for i in grades:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    i_dict.pop('_state')
                    BTCancelledStudentGrades.objects.create(**i_dict)
                for i in notpromoted:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    i_dict.pop('_state')
                    BTCancelledNotPromoted.objects.create(**i_dict)



                BTMarks_Staging.objects.filter(Registration__in = regs).delete()
                BTRollLists_Staging.objects.filter(student_id=student.id).delete()
                BTStudentGrades_Staging.objects.filter(RegId__in = regs.values_list('id'),flat =True).delete()
                BTStudentRegistrations_Staging.objects.filter(Regno=regno).delete()
                marks.delete()
                grades.delete()
                regs.delete()
                rolls.delete()
                notregistered.delete()
                notpromoted.delete()
                droppedregular.delete()


                    
                
            
            return render(request,'superintendent/BTStudentCancellation.html',context)

    else:
        form = StudentCancellationForm()
    context = {'form':form}
    return render(request,'superintendent/BTStudentCancellation.html',context)

