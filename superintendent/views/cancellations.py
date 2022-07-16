from operator import itemgetter
from django.shortcuts import render
from superintendent.models import CancelledStudentInfo,CancelledStudentGrades,CancelledDroppedRegularCourses,CancelledNotPromoted,CancelledNotRegistered,CancelledRollLists,CancelledStudentRegistrations,CancelledMarks
from co_ordinator.models import DroppedRegularCourses,NotPromoted,NotRegistered,RollLists,RollLists_Staging,StudentRegistrations,StudentRegistrations_Staging
from ExamStaffDB.models import StudentInfo
from faculty.models import StudentGrades,Marks,Marks_Staging,StudentGrades_Staging
from superintendent.forms import StudentCancellationForm
from SupExamDB.views import is_Superintendent
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.db.models import F

    

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def seat_cancellation(request):
    studentInfo = []
    if(request.method=='POST'):
        form = StudentCancellationForm(request.POST)
        if(form.is_valid()):
            print(request.POST)
            regno = int(form.cleaned_data['RegNo'])
            studentInfo = StudentInfo.objects.filter(RegNo=regno)
            context = {'form':form}
            if(len(studentInfo)!=0):
                student=studentInfo.first()
                context['RegNo'] = studentInfo[0].RegNo
                context['Name'] = studentInfo[0].Name
                droppedregular= DroppedRegularCourses.objects.filter(student_id=student.id)
                notpromoted= NotPromoted.objects.filter(student_id=student.id)
                notregistered =NotRegistered.objects.filter(Student_id=student.id)
                rolls= RollLists.objects.filter(student_id=student.id)
                regs =StudentRegistrations.objects.filter(Regno=regno)
                grades =StudentGrades.objects.filter(RegId__in = regs.values_list('id'),flat =True)
                marks = Marks.objects.filter(Registration__in = regs)

                CancelledStudentInfo(RegNo=student.RegNo,RollNo=student.RollNo,Name=student.Name,Regulation=student.Regulation,Dept=student.Dept,AdmissionYear=student.AdmissionYear,Gender=student.Gender,Category=student.Category,GuardinaName=student.GuardinaName,Phone=student.Phone,email=student.email,Address1=student.Address1,Address2=student.Address2,Cycle=student.Cycle).save
                for i in rolls:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    CancelledRollLists.objects.create(**i_dict).save()
                for i in notregistered:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    CancelledNotRegistered().objects.create(**i_dict).save()
                for i in regs:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    CancelledStudentRegistrations().objects.create(**i_dict).save()
                for i in droppedregular:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    CancelledDroppedRegularCourses().objects.create(**i_dict).save()
                    
                for i in marks:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    CancelledMarks().objects.create(**i_dict).save()
                for i in grades:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    CancelledStudentGrades().objects.create(**i_dict).save()
                for i in notpromoted:
                    i_dict = i.__dict__
                    i_dict.pop('id') 
                    CancelledNotPromoted().objects.create(**i_dict).save()



                Marks_Staging.objects.filter(Registration__in = regs).delete()
                RollLists_Staging.objects.filter(Student_id=student.id).delete()
                StudentGrades_Staging.objects.filter(RegId__in = regs.values_list('id'),flat =True).delete()
                StudentRegistrations_Staging.objects.filter(Regno=regno).delete()
                marks.delete()
                grades.delete()
                regs.delete()
                rolls.delete()
                notregistered.delete()
                notpromoted.delete()
                droppedregular.delete()


                    
                
            
            return render(request,'SupExamDBRegistrations/BTStudentCancellation.html',context)
        else:
            print('form validation failed')
    else:
        form = StudentCancellationForm()
    context = {'form':form}
    return render(request,'SupExamDBRegistrations/BTStudentCancellation.html',context)

