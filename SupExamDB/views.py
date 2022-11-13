

# from django.shortcuts import render

# # Create your views here.


# from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# from django.http.response import HttpResponseRedirect, JsonResponse
# from django.urls import reverse 
# from ADAUGDB.models import BTProgrammeModel
# from BTco_ordinator.models import BTStudentGradePoints
# from BTExamStaffDB.models import BTStudentInfo
# from Transcripts.models import BTStudentExamEvents, BTDepartmentExamEvents, BTDeptExamEventStudents,\
#      BTStudentCGPAs, BTHeldIn
# from BTExamStaffDB.models import BTFacultyInfo
# from SupExamDB.forms import UploadFileForm, FacultyUpdateForm
# from BTExamStaffDB.resources import FacultyInfoResource
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.contrib.auth import logout
# from django.shortcuts import redirect
# from tablib import Dataset
# from import_export.formats.base_formats import XLSX

# from .templatetags import user_check_tag
# # Create your views here.
# def is_Superintendent(user):
#     return user.groups.filter(name='Superintendent').exists()
# def is_Hod(user):
#     return user.groups.filter(name='HOD').exists()
# def is_Faculty(user):
#     return user.groups.filter(name='Faculty').exists()
# def is_Co_ordinator(user):
#     return user.groups.filter(name='Co-ordinator').exists()
# def is_ExamStaff(user):
#     return user.groups.filter(name='ExamStaff').exists()



# def logout_request(request):
#     logout(request)
#     return redirect("main:homepage")


# @login_required(login_url="/login/")
# def sup_home(request):
#     return render(request,'SupExamDB/suphome.html')

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def btech_printing_home(request):
#     return render(request, 'SupExamDB/printinghome.html')


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def mtech_printing(request):
#     return render(request, 'SupExamDB/MTechPrinting.html')

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def phd_printing(request):
#     return render(request, 'SupExamDB/PhDPrinting.html')

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def get_programme_json(request):
#     programmeList = BTProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
#     progQS = list(programmeList.values())
#     return JsonResponse({'data': progQS }, safe=False)

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def test_view_name(request, dept):
#     deptExamEventsList = DepartmentExamEvents.objects.filter(Dept=int(dept))
#     deptExamEventsQS = list(deptExamEventsList.values())
#     return JsonResponse({'data': deptExamEventsQS}, safe=False)

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def get_programme_events_json(request, department):
#     deptExamEventsList = DepartmentExamEvents.objects.filter(Dept=int(department))
#     deptExamEventsQS = list(deptExamEventsList.values())
#     return JsonResponse({'data': deptExamEventsQS}, safe=False)


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def get_event_regNos(request, department, event):
#     #print('dept' + department + 'event:'+ event)
#     eventRegNosList = DeptExamEventStudents.objects.filter(Dept=department).filter(AYASBYBS=event)
#     eventRegNosQS = list(eventRegNosList.values())
#     return JsonResponse({'data':eventRegNosQS}, safe=False)

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def get_student_regno_grades(request, regno, ayasbybs):
#     studentGrades = BTStudentGradePoints.objects.filter(RegNo=int(regno)).filter(AYASBYBS=int(ayasbybs))
#     studentGradesQS = list(studentGrades.values())
#     return JsonResponse({'data':studentGradesQS}, safe=False)


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def get_student_rollno_grades(request, rollno, ayasbybs):
#     studInfo = BTStudentInfo.objects.filter(RollNo=int(rollno))
#     regNo = studInfo[0].RegNo
#     studentGrades = BTStudentGradePoints.objects.filter(RegNo=int(regNo)).filter(AYASBYBS=int(ayasbybs))
#     studentGradesQS = list(studentGrades.values())
#     return JsonResponse({'data':studentGradesQS,'regNo':regNo}, safe=False)


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def get_btech_ids(request, admissionYear, dept):
#     studentList = StudentAdmissionYearDetails.objects.filter(Dept=dept).filter(AdmissionYear=admissionYear)
#     if(studentList[0].RollNo):
#         studentListQS = list(studentList.order_by('RollNo').values())
#         flag=True
#     else:
#         studentListQS = list(studentList.order_by('RegNo').values())
#         flag = False
#     return JsonResponse({'data':studentListQS,'flag':flag }, safe=False)


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def get_student_cgpa(request, option, regno, ayasbybs):
#     if(option=='regno'):
#         eventStatus = StudentExamEvents.objects.filter(RegNo=int(regno)).filter(AYASBYBS=int(ayasbybs))
#         cgpa = StudentCGPAs.objects.filter(RegNo=int(regno)).filter(AYASBYBS_G=int(ayasbybs))
#     else:
#         studInfo = BTStudentInfo.objects.filter(RollNo=int(regno))
#         tRegNo = studInfo[0].RegNo
#         eventStatus = StudentExamEvents.objects.filter(RegNo=int(tRegNo)).filter(AYASBYBS=int(ayasbybs))
#         cgpa = StudentCGPAs.objects.filter(RegNo=int(tRegNo)).filter(AYASBYBS_G=int(ayasbybs))

#     cgpaQS = list(cgpa.values())
#     eventStatusQS = list(eventStatus.values())
#     return JsonResponse({'data':cgpaQS, 'status':eventStatusQS}) 


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def btech_printing_deptwise(request):
#     programmeList = BTProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
#     #progQS = list(programmeList.values())
#     #return JsonResponse({'data': progQS} , safe=False)
#     deptExamEventList = DepartmentExamEvents.objects.all()
#     deptExamEventStudentList = DeptExamEventStudents.objects.all()
#     return render(request, 'SupExamDB/BT-Dept-Wise.html',{
#                          'programmeList': programmeList,
#                          'deptExamEventList': deptExamEventList,
#                          'deptWiseExamEventStudentList': deptExamEventStudentList,
#                      })

# # @login_required(login_url="/login/")
# # @user_passes_test(is_Superintendent)
# # def btech_makeup_summary_info(request):
# #     print('SupGradesProcessing')
# #     makeupSummaryStats = MakeupSummaryStats.objects.all()  
# #     summaryStats = {}
# #     years = ['II B.Tech.','III B.Tech.','IV B.Tech.']
# #     programmeDetails = BTProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
# #     deptDetails = [ prog.Specialization for prog in programmeDetails]
    
# #     for dept in range(1,9):
# #         deptSummaryStats = {}
# #         for year in range(2,5):
# #             deptYearSummaryStats = makeupSummaryStats.filter(Dept=dept).filter(BYear=year)
# #             deptSummaryStats[years[year-2]] = deptYearSummaryStats
# #         summaryStats[deptDetails[dept-1]] = deptSummaryStats
# #     return render(request, 'SupExamDB/SupBTGradeProcessing.html',{'summaryStats': summaryStats,})

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def btech_printing_deptwise_paginated(request):
#     programmeList = BTProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
#     deptExamEventList = DepartmentExamEvents.objects.all()
#     deptExamEventStudentList = DeptExamEventStudents.objects.all()
#     return render(request, 'SupExamDB/BTech-Dept-Wise-Pagination.html',{
#                          'programmeList': programmeList,
#                          'deptExamEventList': deptExamEventList,
#                          'deptWiseExamEventStudentList': deptExamEventStudentList,
#                      })

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def btech_printing_dept_wise_studentpage(request, idtype, dept, event):
#     deptExamEventStudentList = DeptExamEventStudents.objects.filter(Dept=dept).filter(AYASBYBS=event)
#     if(idtype=="regno"):
#         deptExamEventStudentList = deptExamEventStudentList.order_by('RegNo')
#     else:
#         deptExamEventStudentList = deptExamEventStudentList.order_by('RollNo')
#     paginator = Paginator(deptExamEventStudentList,1)
#     page = request.GET.get('page')
#     try:
#         deptExamEventStudentPage = paginator.page(page)
#     except PageNotAnInteger:
#             # If page is not an integer deliver the first page
#         deptExamEventStudentPage = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range deliver last page of results
#         deptExamEventStudentPage = paginator.page(paginator.num_pages)
#     studentDetails = deptExamEventStudentPage.object_list[0]
#     studentGrades = BTStudentGradePoints.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS=event)
#     studentCGPA = StudentCGPAs.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS_G=event)[0]
#     heldInDetails = HeldIn.objects.filter(AYASBYBS=event)[0]
#     heldInStr = heldInDetails.HeldIn + ' ' + str(heldInDetails.AYear)
#     programmeDetails = BTProgrammeModel.objects.filter(Dept=dept).filter(ProgrammeName='B.Tech.')[0]
#     romans = {1:'I',2:'II',3:'III',4:'IV'}
#     yearSemStr = romans[heldInDetails.BYear] + ' Yr '+ romans[heldInDetails.BSem] + ' Sem'
#     eventStatus = StudentExamEvents.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS=event)[0]
#     print(eventStatus.IsRegular)
#     return render(request,'SupExamDB/BTech-Dept-Student-Grades.html',
#             {'page': page, 
#              'studentDetails': studentDetails,
#             'studentEventPage': deptExamEventStudentPage, 
#             'studentGrades' : studentGrades, 
#             'studentCGPA': studentCGPA,
#             'heldInStr': heldInStr,
#             'programmeDetails': programmeDetails,
#             'yearSemStr': yearSemStr,
#             'eventStatus': eventStatus})


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def btech_printing_studentpages(request, regNo):
#     StudentExamEventsList = StudentExamEvents.objects.filter(RegNo=regNo)
#     if(StudentExamEventsList.count()==0):
#         programmeList = BTProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
#         admissionYears = StudentAdmissionYearDetails.objects.values_list('AdmissionYear', flat=True).distinct()
#         return render(request, 'SupExamDB/BTech-Student-Wise.html',{ 'programmeList':programmeList, 'admissionYears': admissionYears,}  )

    
#     paginator = Paginator(StudentExamEventsList,1)
#     page = request.GET.get('page')
#     try:
#         studentGradePage = paginator.page(page)
#     except PageNotAnInteger:
#             # If page is not an integer deliver the first page
#         studentGradePage = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range deliver last page of results
#         studentGradePage = paginator.page(paginator.num_pages)

#     studentDetails = studentGradePage.object_list[0]
#     studentGrades = BTStudentGradePoints.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS=studentDetails.AYASBYBS)
#     studentCGPA = StudentCGPAs.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS_G=studentDetails.AYASBYBS)[0]
#     heldInDetails = HeldIn.objects.filter(AYASBYBS=studentDetails.AYASBYBS)[0]
#     heldInStr = heldInDetails.HeldIn + ' ' + str(heldInDetails.AYear)
#     deptExamEvent = DeptExamEventStudents.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS=studentDetails.AYASBYBS)[0]
#     programmeDetails = BTProgrammeModel.objects.filter(Dept=deptExamEvent.Dept).filter(ProgrammeName='B.Tech.')[0]
#     romans = {1:'I',2:'II',3:'III',4:'IV'}
#     yearSemStr = romans[heldInDetails.BYear] + ' Yr '+ romans[heldInDetails.BSem] + ' Sem'
#     eventStatus = StudentExamEvents.objects.filter(RegNo=studentDetails.RegNo).filter(AYASBYBS=studentDetails.AYASBYBS)[0]
#     print(eventStatus.IsRegular)
#     return render(request,'SupExamDB/BTech-Dept-Student-Grades.html',
#             {'page': page, 
#              'studentDetails': deptExamEvent,
#             'studentEventPage': studentGradePage, 
#             'studentGrades' : studentGrades, 
#             'studentCGPA': studentCGPA,
#             'heldInStr': heldInStr,
#             'programmeDetails': programmeDetails,
#             'yearSemStr': yearSemStr,
#             'eventStatus': eventStatus})


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def btech_printing_studentwise(request):
#     programmeList = BTProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
#     admissionYears = StudentAdmissionYearDetails.objects.values_list('AdmissionYear', flat=True).distinct()
#     return render(request, 'SupExamDB/BTech-Student-Wise.html',{ 'programmeList':programmeList, 'admissionYears': admissionYears,}  )

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def btech_printing_consolidated(request):
#     return render(request, 'SupExamDB/BTechConsolidated.html')

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)

# def get_heldin_info(request, ayasbybs):
#     heldInDetails = HeldIn.objects.filter(AYASBYBS=ayasbybs)
#     heldInDetailsQS = list(heldInDetails.values())
#     return JsonResponse({'data': heldInDetailsQS})


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def faculty_info_upload_error_handler(request):
#     return(render(request,'SupExamDB/FacultyInfoUploadErrorHandler.html'))

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def ca_import(request):
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         print('POST Success')
#         if form.is_valid():
#             file = request.FILES['file'] #form.cleaned_data['file']
#             data = bytes()
#             for chunk in file.chunks():
#                 data += chunk
#             dataset = XLSX().create_dataset(data)
#             print('IS VALID')
#             print(dataset)
#             faculty_resource = FacultyInfoResource()
#             result = faculty_resource.import_data(dataset, dry_run=True)
#             #df = pd.read_excel(file)

#             if not result.has_errors():
#                 faculty_resource.import_data(dataset, dry_run=False)
#                 return(render(request,'SupExamDB/FacultyInfoUploadSuccess.html'))
#             else:
#                 print(result.invalid_rows)
#                 print(result.row_errors()[0][1][0].error)
#                 errors = result.row_errors()
#                 print(errors)
#                 print(len(dataset))
#                 indices = set([i for i in range(len(dataset))])    
#                 errorIndices = set([i[0]-1 for i in errors])
#                 cleanIndices = indices.difference(errorIndices)
#                 cleanDataset = Dataset()
#                 for i in list(cleanIndices):
#                     cleanDataset.append(dataset[i])
#                 cleanDataset.headers = dataset.headers
#                 result1 = faculty_resource.import_data(cleanDataset, dry_run=True)
#                 if not result1.has_errors():
#                     faculty_resource.import_data(cleanDataset, dry_run=False)
#                 else:
#                     print('Something went wrong in plain import')
#                 for i in errorIndices:
#                     updateRow = dataset[i]
                   
#                 errorData = Dataset()
#                 for i in list(errorIndices):
#                     errorData.append(dataset[i])
#                 facultyRows = [ (errorData[i][0],errorData[i][1],errorData[i][2]) for i in range(len(errorData))]
                    

#                 #updateForm = FacultyUpdateForm(Options=facultyRows)
#                 request.session['facultyRows'] = facultyRows 
#                 return HttpResponseRedirect(reverse('FacultyInfoUploadErrorHandler' ))
#     else:
#         form = UploadFileForm()
#     return(render(request, 'SupExamDB/FacultyInfoUpload.html',{'form':form, }))

# def ca_fi_upload_error_handler(request):
#     facultyRows = request.session.get('facultyRows')
#     for row in facultyRows:
#         print(row[0])
#     if(request.method=='POST'):
#         form = FacultyUpdateForm(facultyRows,request.POST)
#         if(form.is_valid()):
#             for cIndex, fRow in enumerate(facultyRows):
#                 if(form.cleaned_data.get('Check'+fRow[0])):
#                     BTFacultyInfo.objects.filter(PhoneNumber=fRow[1]).update(Name=fRow[0],EmailID=fRow[2])
#             return render(request, 'SupExamDB/FacultyInfoUploadSuccess.html')
#     else:
#         form = FacultyUpdateForm(Options=facultyRows)



#     return(render(request, 'SupExamDB/FacultyInfoUploadErrorHandler.html',{'form':form}))



