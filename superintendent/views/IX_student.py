from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from SupExamDBRegistrations.views.home import is_Superintendent
from SupExamDBRegistrations.models import StudentRegistrations
from superintendent.forms import IXGradeStudentsAddition, IXGradeStudentsStatus
from superintendent.models import IXGradeStudents

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def ix_student_assignment(request):
    if request.method == 'POST':
        form = IXGradeStudentsAddition(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('submit'):
                regEvent = form.cleaned_data.get('regId')
                subject = form.cleaned_data.get('subject')
                regd_no = form.cleaned_data.get('regd_no')
                grade = form.cleaned_data.get('grade')
                student_registration = StudentRegistrations.objects.filter(RegEventId=regEvent, sub_id=subject, RegNo=regd_no).first()
                ix_row = IXGradeStudents(Registration=student_registration, Grade=grade)
                ix_row.save()
                msg = 'Student Grade Added Successfully.'
                return render(request, 'superintendent/IXStudentAddition.html', {'form':form, 'msg':msg})
    else:
        form = IXGradeStudentsAddition()
    return render(request, 'superintendent/IXStudentAddition.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def ix_student_status(request):
    msg = ''
    if request.method == 'POST':
        form = IXGradeStudentsStatus(request.POST)
        if request.POST.get('submit'):
            regEvent = request.POST.get('regId')
            students = IXGradeStudents.objects.filter(Registration__RegEventId=regEvent)
        elif request.POST.get('delete'):
            IXGradeStudents.objects.filter(id=request.POST.get('delete')).delete()
            regEvent = request.POST.get('regId')
            students = IXGradeStudents.objects.filter(Registration__RegEventId=regEvent)
            msg = 'Record Deleted Successfully.'
    else:
        form = IXGradeStudentsStatus()
    return render(request, 'superintendent/IXGradeStudentsStatus.html', {'form':form, 'students':students, 'msg':msg})

