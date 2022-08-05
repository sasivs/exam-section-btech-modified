from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from BTsuperintendent.models import BTProgrammeModel
from MTsuperintendent.models import MTProgrammeModel
from BTExamStaffDB.models import BTStudentInfo
from MTExamStaffDB.models import MTStudentInfo
from BTco_ordinator.models import BTStudentGradePoints
from MTco_ordinator.models import MTStudentGradePoints
from Transcripts.models import BTDepartmentExamEvents, MTDepartmentExamEvents, BTDeptExamEventStudents, MTDeptExamEventStudents, \
    BTStudentExamEvents, BTStudentCGPAs, MTStudentExamEvents, MTStudentCGPAs, BTHeldIn, MTHeldIn, BTDegreeAwardees, MTDegreeAwardees,\
    BTStudentBestGrades, BTStudentFinalSGPAs, BTStudentFinalCGPA
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.shortcuts import redirect


user_login_required = user_passes_test(lambda user: user.is_active, login_url='/')
def active_user_required(view_func):
    decorated_view_func = login_required(user_login_required(view_func))
    return decorated_view_func
@active_user_required

def logout_request(request):
    logout(request)
    return redirect("main:homepage")


def index(request):
    return render(request, 'index.html')
# Create your views here.
user_login_required = user_passes_test(lambda user: user.is_active, login_url='/')
def test_view(request):
    return render(request, 'Transcripts/test.html')

@login_required(login_url="/login/")
def my_view(request):
    # html = '<html> <body> This is my first page </body> </html>'
    # productList = ProductModel.objects.all()
    # itemList = ItemModel.objects.all()
    return render(request, 'Transcripts/index.html')
    # return render(request, 'index2.html',{'productList': productList, 'itemList': itemList})

@login_required(login_url="/login/")
def btech_printing(request):
    return render(request, 'Transcripts/BTechPrinting.html')

@login_required(login_url="/login/")
def mtech_printing(request):
    return render(request, 'Transcripts/MTechPrinting.html')

@login_required(login_url="/login/")
def phd_printing(request):
    return render(request, 'Transcripts/PhDPrinting.html')

@login_required(login_url="/login/")
def get_BT_programme_json(request):
    programmeList = BTProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
    progQS = list(programmeList.values())
    return JsonResponse({'data': progQS }, safe=False)

@login_required(login_url="/login/")
def get_MT_programme_json(request):
    programmeList = MTProgrammeModel.objects.filter(ProgrammeName='M.Tech.')
    progQS = list(programmeList.values())
    return JsonResponse({'data': progQS }, safe=False)


@login_required(login_url="/login/")
def get_BT_programme_events_json(request, department):
    deptExamEventsList = BTDepartmentExamEvents.objects.filter(Dept=int(department))
    deptExamEventsQS = list(deptExamEventsList.values())
    return JsonResponse({'data': deptExamEventsQS}, safe=False)

@login_required(login_url="/login/")
def get_MT_programme_events_json(request, department):
    deptExamEventsList = MTDepartmentExamEvents.objects.filter(Dept=int(department))
    deptExamEventsQS = list(deptExamEventsList.values())
    return JsonResponse({'data': deptExamEventsQS}, safe=False)



@login_required(login_url="/login/")
def get_BT_event_regNos(request, department, event):
    eventRegNosList = BTDeptExamEventStudents.objects.filter(Dept=department).filter(AYASBYBS=event)
    if(department<9):
        eventRegNosList = eventRegNosList.order_by('RollNo')
    else:
        eventRegNosList = eventRegNosList.order_by('RegNo')
        
    eventRegNosQS = list(eventRegNosList.values())
    return JsonResponse({'data':eventRegNosQS}, safe=False)

@login_required(login_url="/login/")
def get_MT_event_regNos(request, department, event):
    eventRegNosList = MTDeptExamEventStudents.objects.filter(Dept=department).filter(AYASBYBS=event)
    eventRegNosList = eventRegNosList.order_by('RegNo')
        
    eventRegNosQS = list(eventRegNosList.values())
    return JsonResponse({'data':eventRegNosQS}, safe=False)



@login_required(login_url="/login/")
def get_BT_regno_events(request,regno):
    regNoEventsList = BTDeptExamEventStudents.objects.filter(RegNo=regno)
    regNoEventsList = regNoEventsList.order_by('AYASBYBS')
        
    regNoEventsListQS = list(regNoEventsList.values())
    return JsonResponse({'data':regNoEventsListQS}, safe=False)


@login_required(login_url="/login/")
def get_MT_regno_events(request,regno):
    regNoEventsList = MTDeptExamEventStudents.objects.filter(RegNo=regno)
    regNoEventsList = regNoEventsList.order_by('AYASMYMS')
        
    regNoEventsListQS = list(regNoEventsList.values())
    return JsonResponse({'data':regNoEventsListQS}, safe=False)



@login_required(login_url="/login/")
def get_btech_ids(request, admissionYear, dept):
    studentList = BTStudentInfo.objects.filter(Dept=dept, AdmissionYear=admissionYear)
    if(studentList[0].RollNo):
        studentListQS = list(studentList.order_by('RollNo').values())
        flag=True
    else:
        studentListQS = list(studentList.order_by('RegNo').values())
        flag = False
    return JsonResponse({'data':studentListQS,'flag':flag }, safe=False)

@login_required(login_url="/login/")
def get_mtech_ids(request, admissionYear, dept):
    studentList = MTStudentInfo.objects.filter(Dept=dept, AdmissionYear=admissionYear)
    studentListQS = list(studentList.order_by('RegNo').values())
    flag = False
    return JsonResponse({'data':studentListQS,'flag':flag }, safe=False)



@login_required(login_url="/login/")
def get_BT_student_cgpa(request, option, regno, ayasbybs):
    if(option != 'regno'):
        studInfo = BTStudentInfo.objects.filter(RollNo=int(regno))
        tRegNo = studInfo[0].RegNo
    else:
        tRegNo = regno

    eventStatus = BTStudentExamEvents.objects.filter(RegNo=int(tRegNo)).filter(AYASBYBS=int(ayasbybs))
    cgpa = BTStudentCGPAs.objects.filter(RegNo=int(tRegNo)).filter(AYASBYBS_G=int(ayasbybs))

    cgpaQS = list(cgpa.values())
    eventStatusQS = list(eventStatus.values())
    return JsonResponse({'data':cgpaQS, 'status':eventStatusQS}) 

@login_required(login_url="/login/")
def get_MT_student_cgpa(request, option, regno, ayasmyms):

    eventStatus = MTStudentExamEvents.objects.filter(RegNo=int(regno)).filter(AYASBYBS=int(ayasmyms))
    cgpa = MTStudentCGPAs.objects.filter(RegNo=int(regno)).filter(AYASBYBS_G=int(ayasmyms))

    cgpaQS = list(cgpa.values())
    eventStatusQS = list(eventStatus.values())
    return JsonResponse({'data':cgpaQS, 'status':eventStatusQS}) 



@login_required(login_url="/login/")
def btech_printing_deptwise(request):
    programmeList = BTProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
    #progQS = list(programmeList.values())
    #return JsonResponse({'data': progQS} , safe=False)
    deptExamEventList = BTDepartmentExamEvents.objects.all()
    deptExamEventStudentList = BTDeptExamEventStudents.objects.all()
    return render(request, 'Transcripts/BTech-Dept-Wise.html',{
                         'programmeList': programmeList,
                         'deptExamEventList': deptExamEventList,
                         'deptWiseExamEventStudentList': deptExamEventStudentList,
                     })

@login_required(login_url="/login/")
def mtech_printing_deptwise(request):
    programmeList = MTProgrammeModel.objects.filter(ProgrammeName='M.Tech.')
    #progQS = list(programmeList.values())
    #return JsonResponse({'data': progQS} , safe=False)
    deptExamEventList = MTDepartmentExamEvents.objects.all()
    deptExamEventStudentList = MTDeptExamEventStudents.objects.all()
    return render(request, 'Transcripts/BTech-Dept-Wise.html',{
                         'programmeList': programmeList,
                         'deptExamEventList': deptExamEventList,
                         'deptWiseExamEventStudentList': deptExamEventStudentList,
                     })



@login_required(login_url="/login/")
def btech_printing_deptwise_paginated(request):
    programmeList = BTProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
    deptExamEventList = BTDepartmentExamEvents.objects.all()
    deptExamEventStudentList = BTDeptExamEventStudents.objects.all()
    return render(request, 'Transcripts/BTech-Dept-Wise-Pagination.html',{
                         'programmeList': programmeList,
                         'deptExamEventList': deptExamEventList,
                         'deptWiseExamEventStudentList': deptExamEventStudentList,
                     })

@login_required(login_url="/login/")
def mtech_printing_deptwise_paginated(request):
    programmeList = MTProgrammeModel.objects.filter(ProgrammeName='M.Tech.')
    deptExamEventList = MTDepartmentExamEvents.objects.all()
    deptExamEventStudentList = MTDeptExamEventStudents.objects.all()
    return render(request, 'Transcripts/BTech-Dept-Wise-Pagination.html',{
                         'programmeList': programmeList,
                         'deptExamEventList': deptExamEventList,
                         'deptWiseExamEventStudentList': deptExamEventStudentList,
                     })



@login_required(login_url="/login/")
def btech_printing_dept_wise_studentpage(request, idtype, dept, event):
    deptExamEventStudentList = BTDeptExamEventStudents.objects.filter(Dept=dept).filter(AYASBYBS=event)
    if(idtype=="regno"):
        deptExamEventStudentList = deptExamEventStudentList.order_by('RegNo')
    else:
        deptExamEventStudentList = deptExamEventStudentList.order_by('RollNo')
    paginator = Paginator(deptExamEventStudentList,1)
    page = request.GET.get('page')
    try:
        deptExamEventStudentPage = paginator.page(page)
    except PageNotAnInteger:
            # If page is not an integer deliver the first page
        deptExamEventStudentPage = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        deptExamEventStudentPage = paginator.page(paginator.num_pages)
    studentDetails = deptExamEventStudentPage.object_list[0]
    studentGrades = BTStudentGradePoints.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS=event)
    studentCGPA = BTStudentCGPAs.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS_G=event).first()
    heldInDetails = BTHeldIn.objects.filter(AYASBYBS=event).first()
    heldInStr = heldInDetails.HeldInMonth + ' ' + str(heldInDetails.HeldInYear)
    programmeDetails = BTProgrammeModel.objects.filter(Dept=dept).filter(ProgrammeName='B.Tech.').first()
    romans = {1:'I',2:'II',3:'III',4:'IV'}
    yearSemStr = romans[heldInDetails.BYear] + ' Yr '+ romans[heldInDetails.BSem] + ' Sem'
    eventStatus = BTStudentExamEvents.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS=event).first()
    print(eventStatus.IsRegular)
    return render(request,'Transcripts/BTech-Dept-Student-Grades.html',
            {'page': page, 
             'studentDetails': studentDetails,
            'studentEventPage': deptExamEventStudentPage, 
            'studentGrades' : studentGrades, 
            'studentCGPA': studentCGPA,
            'heldInStr': heldInStr,
            'programmeDetails': programmeDetails,
            'yearSemStr': yearSemStr,
            'eventStatus': eventStatus})

@login_required(login_url="/login/")
def mtech_printing_dept_wise_studentpage(request, idtype, dept, event):
    deptExamEventStudentList = MTDeptExamEventStudents.objects.filter(Dept=dept).filter(AYASMYMS=event)
    if(idtype=="regno"):
        deptExamEventStudentList = deptExamEventStudentList.order_by('RegNo')
    paginator = Paginator(deptExamEventStudentList,1)
    page = request.GET.get('page')
    try:
        deptExamEventStudentPage = paginator.page(page)
    except PageNotAnInteger:
            # If page is not an integer deliver the first page
        deptExamEventStudentPage = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        deptExamEventStudentPage = paginator.page(paginator.num_pages)
    studentDetails = deptExamEventStudentPage.object_list[0]
    studentGrades = MTStudentGradePoints.objects.filter(RegNo=studentDetails.RegNo).filter(AYASMYMS=event)
    studentCGPA = MTStudentCGPAs.objects.filter(RegNo=studentDetails.RegNo).filter(AYASMYMS_G=event).first()
    heldInDetails = MTHeldIn.objects.filter(AYASMYMS=event).first()
    heldInStr = heldInDetails.HeldInMonth + ' ' + str(heldInDetails.HeldInYear)
    programmeDetails = MTProgrammeModel.objects.filter(Dept=dept).filter(ProgrammeName='M.Tech.').first()
    romans = {1:'I',2:'II'}
    yearSemStr = romans[heldInDetails.MYear] + ' Yr '+ romans[heldInDetails.MSem] + ' Sem'
    eventStatus = MTStudentExamEvents.objects.filter(RegNo=studentDetails.RegNo).filter(AYASMYMS=event).first()
    print(eventStatus.IsRegular)
    return render(request,'Transcripts/BTech-Dept-Student-Grades.html',
            {'page': page, 
             'studentDetails': studentDetails,
            'studentEventPage': deptExamEventStudentPage, 
            'studentGrades' : studentGrades, 
            'studentCGPA': studentCGPA,
            'heldInStr': heldInStr,
            'programmeDetails': programmeDetails,
            'yearSemStr': yearSemStr,
            'eventStatus': eventStatus})



@login_required(login_url="/login/")
def btech_printing_studentpages(request, regNo):
    StudentExamEventsList = BTStudentExamEvents.objects.filter(RegNo=regNo)
    if(StudentExamEventsList.count()==0):
        programmeList = BTProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
        admissionYears = BTStudentInfo.objects.values_list('AdmissionYear', flat=True).distinct()
        return render(request, 'Transcripts/BTech-Student-Wise.html',{ 'programmeList':programmeList, 'admissionYears': admissionYears,}  )

    
    paginator = Paginator(StudentExamEventsList,1)
    page = request.GET.get('page')
    try:
        studentGradePage = paginator.page(page)
    except PageNotAnInteger:
            # If page is not an integer deliver the first page
        studentGradePage = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        studentGradePage = paginator.page(paginator.num_pages)
    studentDetails = studentGradePage.object_list[0]
    studentGrades = BTStudentGradePoints.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS=studentDetails.AYASBYBS)
    studentCGPA = BTStudentCGPAs.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS_G=studentDetails.AYASBYBS)[0]
    heldInDetails = BTHeldIn.objects.filter(AYASBYBS=studentDetails.AYASBYBS)[0]
    heldInStr = heldInDetails.HeldInMonth + ' ' + str(heldInDetails.HeldInYear)
    deptExamEvent = BTDeptExamEventStudents.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS=studentDetails.AYASBYBS)[0]
    programmeDetails = BTProgrammeModel.objects.filter(Dept=deptExamEvent.Dept).filter(ProgrammeName='B.Tech.')[0]
    romans = {1:'I',2:'II',3:'III',4:'IV'}
    yearSemStr = romans[heldInDetails.BYear] + ' Yr '+ romans[heldInDetails.BSem] + ' Sem'
    eventStatus = BTStudentExamEvents.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS=studentDetails.AYASBYBS)[0]
    print(eventStatus.IsRegular)
    return render(request,'Transcripts/BTech-Dept-Student-Grades.html',
            {'page': page, 
             'studentDetails': deptExamEvent,
            'studentEventPage': studentGradePage, 
            'studentGrades' : studentGrades, 
            'studentCGPA': studentCGPA,
            'heldInStr': heldInStr,
            'programmeDetails': programmeDetails,
            'yearSemStr': yearSemStr,
            'eventStatus': eventStatus})

@login_required(login_url="/login/")
def mtech_printing_studentpages(request, regNo):
    StudentExamEventsList = MTStudentExamEvents.objects.filter(RegNo=regNo)
    if(StudentExamEventsList.count()==0):
        programmeList = MTProgrammeModel.objects.filter(ProgrammeName='M.Tech.')
        admissionYears = MTStudentInfo.objects.values_list('AdmissionYear', flat=True).distinct()
        return render(request, 'Transcripts/BTech-Student-Wise.html',{ 'programmeList':programmeList, 'admissionYears': admissionYears,}  )

    
    paginator = Paginator(StudentExamEventsList,1)
    page = request.GET.get('page')
    try:
        studentGradePage = paginator.page(page)
    except PageNotAnInteger:
            # If page is not an integer deliver the first page
        studentGradePage = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        studentGradePage = paginator.page(paginator.num_pages)
    studentDetails = studentGradePage.object_list[0]
    studentGrades = MTStudentGradePoints.objects.filter(RegNo=studentDetails.RegNo).filter(AYASMYMS=studentDetails.AYASMYMS)
    studentCGPA = MTStudentCGPAs.objects.filter(RegNo=studentDetails.RegNo).filter(AYASMYMS_G=studentDetails.AYASMYMS)[0]
    heldInDetails = MTHeldIn.objects.filter(AYASBYBS=studentDetails.AYASMYMS)[0]
    heldInStr = heldInDetails.HeldInMonth + ' ' + str(heldInDetails.HeldInYear)
    deptExamEvent = MTDeptExamEventStudents.objects.filter(RegNo=studentDetails.RegNo).filter(AYASMYMS=studentDetails.AYASMYMS)[0]
    programmeDetails = MTProgrammeModel.objects.filter(Dept=deptExamEvent.Dept).filter(ProgrammeName='M.Tech.')[0]
    romans = {1:'I',2:'II'}
    yearSemStr = romans[heldInDetails.BYear] + ' Yr '+ romans[heldInDetails.BSem] + ' Sem'
    eventStatus = MTStudentExamEvents.objects.filter(RegNo=studentDetails.RegNo).filter(AYASMYMS=studentDetails.AYASMYMS)[0]
    print(eventStatus.IsRegular)
    return render(request,'Transcripts/BTech-Dept-Student-Grades.html',
            {'page': page, 
             'studentDetails': deptExamEvent,
            'studentEventPage': studentGradePage, 
            'studentGrades' : studentGrades, 
            'studentCGPA': studentCGPA,
            'heldInStr': heldInStr,
            'programmeDetails': programmeDetails,
            'yearSemStr': yearSemStr,
            'eventStatus': eventStatus})


@login_required(login_url="/login/")
def btech_printing_studentwise(request):
    programmeList = BTProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
    admissionYears = BTStudentInfo.objects.values_list('AdmissionYear', flat=True).distinct()
    return render(request, 'Transcripts/BTech-Student-Wise.html',{ 'programmeList':programmeList, 'admissionYears': admissionYears,}  )

@login_required(login_url="/login/")
def mtech_printing_studentwise(request):
    programmeList = MTProgrammeModel.objects.filter(ProgrammeName='M.Tech.')
    admissionYears = MTStudentInfo.objects.values_list('AdmissionYear', flat=True).distinct()
    return render(request, 'Transcripts/BTech-Student-Wise.html',{ 'programmeList':programmeList, 'admissionYears': admissionYears,}  )


@login_required(login_url="/login/")
def btech_printing_consolidated(request, regno):
    programmeList = BTStudentCGPAs.objects.filter(RegNo=regno)
    subjectsList=BTStudentGradePoints.objects.filter(RegNo=regno)
    progQS = list(programmeList.values())
    subQS=list(subjectsList.values())
    return JsonResponse({'data':progQS,'sub':subQS}, safe=False)

@login_required(login_url="/login/")
def mtech_printing_consolidated(request, regno):
    programmeList = MTStudentCGPAs.objects.filter(RegNo=regno)
    subjectsList=MTStudentGradePoints.objects.filter(RegNo=regno)
    progQS = list(programmeList.values())
    subQS=list(subjectsList.values())
    return JsonResponse({'data':progQS,'sub':subQS}, safe=False)


@login_required(login_url="/login/")
def btech_cmm(request):
    return render(request ,'Transcripts/BTechConsolidated.html')  

 

@login_required(login_url="/login/")
def btech_get_cmmdata_dept(request,department):
    deptRollList = BTDegreeAwardees.objects.filter(Dept=department)
    deptQS = list(deptRollList.values())
    return JsonResponse({'data':deptQS}, safe=False)

@login_required(login_url="/login/")
def mtech_get_cmmdata_dept(request,department):
    deptRollList = MTDegreeAwardees.objects.filter(Dept=department)
    deptQS = list(deptRollList.values())
    return JsonResponse({'data':deptQS}, safe=False)



@login_required(login_url="/login/")
def btech_get_cmm_grades(request,regNo):
    studentGradeList = BTStudentBestGrades.objects.filter(RegNo=regNo).order_by('Order','SubCode')
    studentGradeListQS = list(studentGradeList.values())
    sem1QS = list(studentGradeList.filter(BYBS=11).values())
    sem2QS = list(studentGradeList.filter(BYBS=12).values())
    sem3QS = list(studentGradeList.filter(BYBS=21).values())
    sem4QS = list(studentGradeList.filter(BYBS=22).values())
    sem5QS = list(studentGradeList.filter(BYBS=31).values())
    sem6QS = list(studentGradeList.filter(BYBS=32).values())
    sem7QS = list(studentGradeList.filter(BYBS=41).values())
    sem8QS = list(studentGradeList.filter(BYBS=42).values())

    sgpas = [BTStudentFinalSGPAs.objects.filter(RegNo=regNo).filter(BYBS=11)[0].SGPA, 
             BTStudentFinalSGPAs.objects.filter(RegNo=regNo).filter(BYBS=12)[0].SGPA,
             BTStudentFinalSGPAs.objects.filter(RegNo=regNo).filter(BYBS=21)[0].SGPA,
             BTStudentFinalSGPAs.objects.filter(RegNo=regNo).filter(BYBS=22)[0].SGPA,
             BTStudentFinalSGPAs.objects.filter(RegNo=regNo).filter(BYBS=31)[0].SGPA, 
             BTStudentFinalSGPAs.objects.filter(RegNo=regNo).filter(BYBS=32)[0].SGPA,
             BTStudentFinalSGPAs.objects.filter(RegNo=regNo).filter(BYBS=41)[0].SGPA,
             BTStudentFinalSGPAs.objects.filter(RegNo=regNo).filter(BYBS=42)[0].SGPA]
    da = BTDegreeAwardees.objects.filter(RegNo=regNo)[0]

    numberOfRows = [len(sem1QS)-len(sem2QS),len(sem3QS)-len(sem4QS),
                    len(sem5QS)-len(sem6QS),len(sem7QS)-len(sem8QS)]
    studentDetails = BTStudentInfo.objects.filter(RegNo=regNo)[0]
    branchDetails = BTProgrammeModel.objects.filter(Dept=studentDetails.Dept).filter(ProgrammeType='UG')[0]
    return JsonResponse({'data':studentGradeListQS,
                         'results':[sem1QS, sem2QS, sem3QS, sem4QS, sem5QS, sem6QS, sem7QS, sem8QS], 
                         'sgpas':sgpas,
                         'cgpa':BTStudentFinalCGPA.objects.filter(RegNo=regNo)[0].CGPA,
                         'numberOfRows':numberOfRows,
                         'studentName': studentDetails.Name,
                         'rollNo' : studentDetails.RollNo,
                         'branchName': branchDetails.Specialization,
                         'programmeName':branchDetails.ProgrammeName,
                         'degree':da.Degree 
                         },safe = False)



@login_required(login_url="/login/")
def get_BT_heldin_info(request, ayasbybs):
    heldInDetails = BTHeldIn.objects.filter(AYASBYBS=ayasbybs)
    heldInDetailsQS = list(heldInDetails.values())
    return JsonResponse({'data': heldInDetailsQS})

@login_required(login_url="/login/")
def get_MT_heldin_info(request, ayasmyms):
    heldInDetails = MTHeldIn.objects.filter(AYASMYMS=ayasmyms)
    heldInDetailsQS = list(heldInDetails.values())
    return JsonResponse({'data': heldInDetailsQS})




# @login_required(login_url="/login/")
# def test_view_name(request, dept):
#     deptExamEventsList = DepartmentExamEvents.objects.filter(Dept=int(dept))
#     deptExamEventsQS = list(deptExamEventsList.values())
#     return JsonResponse({'data': deptExamEventsQS}, safe=False)

# @login_required(login_url="/login/")
# def get_student_regno_grades(request, regno, ayasbybs):
#     studentGrades = StudentGradePointsV.objects.filter(RegNo=int(regno)).filter(AYASBYBS=int(ayasbybs)).order_by('Order','SubCode')
    
#     studentGradesQS = list(studentGrades.values())
#     return JsonResponse({'data':studentGradesQS}, safe=False)


# @login_required(login_url="/login/")
# def get_student_rollno_grades(request, rollno, ayasbybs):
#     studInfo = BTStudentInfo.objects.filter(RollNo=int(rollno))
#     regNo = studInfo[0].RegNo
#     studentGrades = StudentGradePointsV.objects.filter(RegNo=int(regNo)).filter(AYASBYBS=int(ayasbybs)).order_by('Order','SubCode')
#     studentGradesQS = list(studentGrades.values())
#     return JsonResponse({'data':studentGradesQS,'regNo':regNo}, safe=False)