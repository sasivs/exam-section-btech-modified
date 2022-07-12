# from operator import itemgetter
# from django.shortcuts import render
# from SupExamDBRegistrations.forms import BacklogRegistrationForm, StudentCancellationForm, StudentSemesterCancellationForm
# from SupExamDBRegistrations.models import CancelledStudentInfo, NotPromoted, StudentBacklogs, StudentCancellation, StudentGradePoints, StudentGrades, StudentInfo,StudentRegistrations, CancelledStudentInfo, Subjects_Staging
# from .home import is_Superintendent
# from django.contrib.auth.decorators import login_required, user_passes_test 
# from django.contrib.auth import logout 
# from django.db.models import F

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def cancellation_home(request):
#     return render(request,'SupExamDBRegistrations/registrationcancellation.html')    

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def seat_cancellation(request):
#     studentInfo = []
#     if(request.method=='POST'):
#         form = StudentCancellationForm(request.POST)
#         if(form.is_valid()):
#             print(request.POST)
#             regno = int(form.cleaned_data['RegNo'])
#             studentInfo = StudentInfo.objects.filter(RegNo=regno)
#             context = {'form':form}
#             if(len(studentInfo)!=0):
#                 if studentInfo[0].RollNo:
#                     context['RollNo'] = studentInfo[0].RollNo
#                 else:
#                     context['RegNo'] = studentInfo[0].RegNo
#                 context['Name'] = studentInfo[0].Name
#             entries = StudentGrades.objects.filter(RegNo=regno).values()
#             for entry in entries:
#                 newRow = StudentCancellation(RegNo=entry['RegNo'],AYear=entry['AYear'],ASem=entry['ASem'],SubCode=entry['SubCode'],OfferedYear=entry['OfferedYear'],Dept=entry['Dept'],Regulation=entry['Regulation'],Grade=entry['Grade'],AttGrade=entry['AttGrade'])
#                 newRow.save()
#             StudentGrades.objects.filter(RegNo=regno).delete()
#             newRow = CancelledStudentInfo(RegNo = StudentInfo[0].RegNo,RollNo = StudentInfo[0].RollNo,Name = StudentInfo[0].Name,Regulation = StudentInfo[0].Regulation,Dept = StudentInfo[0].Dept,Gender = StudentInfo[0].Gender,Category = StudentInfo[0].Category,GaurdianName = StudentInfo[0].GaurdianName,Phone = StudentInfo[0].Phone,email = StudentInfo[0].email,Address1 = StudentInfo[0].Address1,Address2 = StudentInfo[0].Address2)
#             newRow.save()
#             StudentInfo.objects.filter(RegNo = regno).delete()
#             return render(request,'SupExamDBRegistrations/BTStudentCancellation.html',context)
#         else:
#             print('form validation failed')
#     else:
#         form = StudentCancellationForm()
#     context = {'form':form}
#     return render(request,'SupExamDBRegistrations/BTStudentCancellation.html',context)

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def semester_cancellation(request):
#     studentInfo = []
#     if(request.method=='POST'):
#         form = StudentSemesterCancellationForm(request.POST)
#         context = {'form':form}
#         if ('RegNo' in request.POST.keys()):
#             pass
#         if('RegNo' in request.POST.keys() and 'BYeay' in request.POST.keys()):
#             pass
#         if('RegNo' in request.POST.keys() and 'BYear' in request.POST.keys() and ('BSem' in request.POST.keys() or 'Cycle' in request.POST.keys())):
#             print(request.POST)
#             regno = int(request.POST['RegNo'])
#             byear = int(request.POST['BYear'])
#             studentInfo = StudentInfo.objects.filter(RegNo=regno)
#             if(len(studentInfo)!=0):
#                 if studentInfo[0].RollNo:
#                     context['RollNo'] = studentInfo[0].RollNo
#                 else:
#                     context['RegNo'] = studentInfo[0].RegNo
#                 context['Name'] = studentInfo[0].Name
#             entries = StudentGrades.objects.filter(RegNo=regno).values()
#             dept = entries.filter(RegNo = regno).values('Dept').distinct()
#             print(dept)
#             dept = dept[0]['Dept']
#             if 'BSem' in request.POST.keys():
#                 bsem = int(request.POST['BSem'])
#                 context['BSem']=bsem
#                 SubCodes = Subjects_Staging.objects.filter( BYear=byear, BSem=bsem, Dept=dept).values('SubCode').distinct()
#                 #print(entries)
#             elif 'Cycle' in request.POST.keys():
#                 dept = int(request.POST['Cycle'])
#                 context['BSem']= dept
#                 SubCodes = Subjects_Staging.objects.filter( BYear=byear, Dept=dept).values('SubCode').distinct()   
#             print(SubCodes)
#             context['SubCodes']=SubCodes
#             context['BYear']=byear
#         if(form.is_valid() and 'RegNo' in request.POST.keys() and 'BYear' in request.POST.keys() and 'Submit' in request.POST.keys() and ('BSem' in request.POST.keys() or 'Cycle' in request.POST.keys())):
#             print(request.POST)
#             # for entry in entries:
#             #     newRow = StudentCancellation(RegNo=entry['RegNo'],AYear=entry['AYear'],ASem=entry['ASem'],SubCode=entry['SubCode'],OfferedYear=entry['OfferedYear'],Dept=entry['Dept'],Regulation=entry['Regulation'],Grade=entry['Grade'],AttGrade=entry['AttGrade'])
#             #     newRow.save()
#             for sub in SubCodes:
#                 # StudentGrades.objects.filter(RegNo=regno,SubCode=sub['SubCode']).delete()
#                 l = StudentGrades.objects.filter(RegNo=regno,SubCode=sub['SubCode']).values()
#                 print(l)
#             # NotPromoted.objects.filter(RegNo = regno).update(PoA = 'R')
            
#             return render(request,'SupExamDBRegistrations/BTStudentSemesterCancellationSuccess.html',context)
#         else:
#             print('form validation failed')
#         return render(request,'SupExamDBRegistrations/BTStudentSemesterCancellation.html',context)
#     else:
#         form = StudentSemesterCancellationForm()
#         context = {'form':form}
#     return render(request,'SupExamDBRegistrations/BTStudentSemesterCancellation.html',context)
