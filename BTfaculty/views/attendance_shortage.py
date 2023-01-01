from django.contrib.auth.decorators import login_required, user_passes_test 
from django.http import HttpResponse
from django.shortcuts import render
from BTExamStaffDB.models import BTIXGradeStudents
from BTfaculty.forms import AttendanceShoratgeStatusForm, AttendanceShoratgeUploadForm
from BTco_ordinator.models import BTFacultyAssignment, BTRollLists, BTStudentRegistrations
from BTfaculty.models import BTAttendance_Shortage
from ADAUGDB.models import BTRegistrationStatus
from ADAUGDB.user_access_test import is_Faculty, attendance_shortage_status_access, sample_regno_sheet_access
from import_export.formats.base_formats import XLSX
from BThod.models import BTCoordinator, BTFaculty_user
from ADAUGDB.models import BTCycleCoordinator, BTHOD
from django.db import transaction

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(is_Faculty)
def attendance_shortage_upload(request):
    user = request.user
    faculty = BTFaculty_user.objects.filter(RevokeDate__isnull=True,User=user).first()
    subjects  = BTFacultyAssignment.objects.filter(Faculty=faculty.Faculty,RegEventId__Status=1).order_by('Subject__course__SubCode','Section')
    if(request.method == 'POST'):
            form = AttendanceShoratgeUploadForm(subjects, request.POST, request.FILES)
        # if(form.is_valid()):
            sub = request.POST['Subjects'].split(':')[0]
            regEvent = request.POST['Subjects'].split(':')[1]
            section = request.POST['Subjects'].split(':')[2]
            
            file = request.FILES['file']
            
            data = bytes()
            for chunk in file.chunks():
                data+=chunk
            dataset = XLSX().create_dataset(data)

            roll_list = BTRollLists.objects.filter(RegEventId_id=regEvent, Section=section).values_list('student__RegNo', flat=True)
            errorRegNo = []
            for i in range(len(dataset)):
                regno = dataset[i][0]
                if regno not in roll_list:
                    errorRegNo.append(regno)
                    continue 
                student_registration = BTStudentRegistrations.objects.filter(student__student__RegNo=regno, RegEventId=regEvent, sub_id_id=sub)
                att_short = BTAttendance_Shortage.objects.filter(Registration=student_registration.first())
                if len(att_short) == 0 :
                    att_short = BTAttendance_Shortage(Registration=student_registration.first())
                    att_short.save()
            msg = 'Attendance Shortage Updated successfully.'
            return render(request, 'BTfaculty/AttendanceShortageUpload.html', {'form':form, 'error':errorRegNo, 'msg':msg})
    else:
        
        form = AttendanceShoratgeUploadForm(subjects)
        return render(request, 'BTfaculty/AttendanceShortageUpload.html',{'form':form})


@login_required(login_url="/login/")
@user_passes_test(attendance_shortage_status_access)
def attendance_shortage_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    subjects = None
    if 'Faculty' in groups:
        faculty = BTFaculty_user.objects.filter(RevokeDate__isnull=True,User=user).first()
        subjects  = BTFacultyAssignment.objects.filter(Faculty=faculty.Faculty,RegEventId__Status=1).order_by('Subject__course__SubCode','Section')
    elif 'Superintendent' in groups or 'Associate-Dean-Academics' in groups or 'Associate-Dean-Exams' in groups:
        subjects = BTFacultyAssignment.objects.filter(RegEventId__Status=1).order_by('Subject__course__SubCode','Section')
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(Subject__course__OfferedBy=hod.Dept, RegEventId__Status=1).order_by('Subject__course__SubCode','Section')
    elif 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(RegEventId__BYear=coordinator.BYear, Subject__course__OfferedBy=coordinator.Dept, RegEventId__Status=1).order_by('Subject__course__SubCode','Section')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(RegEventId__BYear=1, Subject__course__OfferedBy=cycle_cord.Cycle, RegEventId__Status=1).order_by('Subject__course__SubCode','Section')
    if(request.method == 'POST'):
        form = AttendanceShoratgeStatusForm(subjects,request.POST)
        sub = request.POST['Subjects'].split(':')[0]
        regEvent = request.POST['Subjects'].split(':')[1]
        section = request.POST['Subjects'].split(':')[2]
        msg = ''
        roll_list = BTRollLists.objects.filter(RegEventId_id=regEvent, Section=section)
        att_short = BTAttendance_Shortage.objects.filter(Registration__RegEventId=regEvent, Registration__sub_id__course_id=sub, Registration__student__student__RegNo__in=roll_list.values_list('student__RegNo', flat=True)).order_by('Registration__student__student__RegNo')
        if request.POST.get('delete'):
            att_short.filter(id=request.POST.get('delete')).delete()
            roll_list = BTRollLists.objects.filter(RegEventId_id=regEvent, Section=section)
            att_short = BTAttendance_Shortage.objects.filter(Registration__RegEventId=regEvent, Registration__sub_id__course_id=sub, Registration__student__student__RegNo__in=roll_list.values_list('student__RegNo', flat=True)).order_by('Registration__student__student__RegNo')
            msg = 'Attendance shortage record has been deleted successfully'
        return render(request, 'BTfaculty/AttendanceShortageStatus.html',{'form':form ,'att_short':att_short, 'msg':msg})

    else:
        form = AttendanceShoratgeStatusForm(subjects)
    return render(request, 'BTfaculty/AttendanceShortageStatus.html',{'form':form})


@login_required(login_url="/login/")
@user_passes_test(sample_regno_sheet_access)
def download_sample_attendance_shortage_sheet(request):
    from BTco_ordinator.utils import RegNoTemplateBookGenerator
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
    response['Content-Disposition'] = 'attachment; filename=sample-{model}.xlsx'.format(model='ModelTemplate')
    BookGenerator = RegNoTemplateBookGenerator()
    workbook = BookGenerator.generate_workbook()
    workbook.save(response)
    return response

def add_Rixgrades(file, kwargs=None):
    import pandas as pd
    file = pd.read_excel(file)
    if kwargs:
        if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
            return "Provide the required arguments!!!!"
        file = file[(file['AYear']==kwargs.get('AYear')) & (file['ASem']==kwargs.get('ASem')) & (file['BYear']==kwargs.get('BYear'))\
            & (file['BSem']==kwargs.get('BSem')) & (file['Dept']==kwargs.get('Dept')) & (file['Regulation']==kwargs.get('Regulation')) & \
            (file['Mode']==kwargs.get('Mode'))]
    error_rows=[]
    for rIndex, row in file.iterrows():
        print(row)
        regEvent = BTRegistrationStatus.objects.filter(AYear=row['AYear'], ASem=row['ASem'], BYear=row['BYear'], BSem=row['BSem'], Dept=row['Dept'], Regulation=row['Regulation'], Mode=row['Mode']).first()
        registration = BTStudentRegistrations.objects.filter(student__student__RegNo=row['RegNo'], RegEventId_id=regEvent.id, sub_id__course__SubCode=row['SubCode']).first()
        if registration:
            if row['Grade'] == 'R':
                if not BTAttendance_Shortage.objects.filter(Registration_id=registration.id).exists():
                    att_short = BTAttendance_Shortage(Registration_id=registration.id)
                    att_short.save()
            else:
                if not BTIXGradeStudents.objects.filter(Registration_id=registration.id).exists():
                    ix_grade = BTIXGradeStudents(Registration_id=registration.id, Grade=row['Grade'])
                    ix_grade.save()
                else:
                    BTIXGradeStudents.objects.filter(Registration_id=registration.id).update(Grade=row['Grade'])
        else:
            error_rows.append(row)
    print(error_rows)
    print("These rows have no registrations.")
    return 'Completed!!'
        

