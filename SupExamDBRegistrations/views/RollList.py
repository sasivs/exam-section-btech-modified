from typing import Set
# from click import option
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.shortcuts import redirect
from django.urls import reverse
# from requests import options

from SupExamDBRegistrations.forms import RollListStatusForm, RollListRegulationDifferanceForm,RollListErrorHandlerForm,\
     RollListFinalizeForm, GenerateRollListForm, RollListsCycleHandlerForm
from SupExamDBRegistrations.models import Regulation, RegulationChange, RollLists_Staging, StudentInfo, StudentInfoResource, NotPromoted, RollLists,\
    RegistrationStatus,StudentRegistrations_Staging
from .home import is_Superintendent
from tablib import Dataset
from import_export.formats.base_formats import XLSX
# from datetime import date

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def generateRollList(request):
    if request.method == 'POST':
        if 'Regulation_change' in request.POST:
            (ayear,asem,byear,bsem,regulation)=request.session.get('ayasbybsr')
            print(ayear,asem,byear,bsem,regulation)
            if(byear ==1):
                not_promoted_regno = request.session.get('not_promoted_regno_firstyear')  
            else:
                not_promoted_regno = request.session.get('not_promoted_regno')
                
            ayasbybsr = (ayear,asem,byear,bsem,regulation)
            
            not_promoted_regnos =[]
            ayasbybsr = (ayear,asem,byear,bsem,regulation)
            form = RollListRegulationDifferanceForm((not_promoted_regno,regulation),request.POST)
           
            if(form.is_valid()):
        
                for cIndex, sReg in enumerate(not_promoted_regno):
                    print(cIndex,sReg)
                    if(form.cleaned_data.get('RadioMode'+str(sReg))):
                        choice = form.cleaned_data.get('RadioMode'+str(sReg))
                        
                        s_info = StudentInfo.objects.get(RegNo=sReg)
                        roll = RollLists_Staging(RegNo=sReg, Dept=s_info.Dept, AYear=ayear, BYear=byear, Cycle=s_info.Cycle, Regulation=regulation)
                        if(choice == 'YES'):
                            if(byear ==1):
                                not_promoted_regnos.append(sReg)
                            else:
                                roll = RollLists_Staging.objects.filter(RegNo=sReg, Dept=s_info.Dept, AYear=ayear, BYear=byear, Cycle=s_info.Cycle, Regulation=regulation)
                                if(len(roll) ==0):
                                    roll.save()
                            prev_regulation  = s_info.Regulation
                            s_info.Regulation = regulation
                            s_info.save()
                            if(prev_regulation != regulation):
                                currentRegEventId = request.session.get('currentRegEventId')
                                regu_change = RegulationChange(RegEventId = currentRegEventId, StudentId= s_info.id, \
                                    PreviousRegulation=prev_regulation ,PresentRegulation=regulation)
                                regu_change.save()
                        #else:
                
                if(len(not_promoted_regnos)!=0 and byear ==1 ):
                        request.session['not_promoted_regno'] = (not_promoted_regnos)
                        return HttpResponseRedirect(reverse('FirstYearRollListsCycleHandler' ))
                return (render(request, 'SupExamDBRegistrations/RollListGenerateSuccess.html')) 
            
        else:
            form = GenerateRollListForm(request.POST)
            print(request.POST)
            if(form.is_valid()):
                depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
                years = {1:'I',2:'II',3:'III',4:'IV'}
                deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
                rom2int = {'I':1,'II':2,'III':3,'IV':4}
                # print(form.cleaned_data['regID'])
                if(form.cleaned_data['regID']!='--Choose Event--'):
                    strs = form.cleaned_data['regID'].split(':')
                    dept = deptDict[strs[0]]
                    ayear = int(strs[3])
                    asem = int(strs[4])
                    byear = rom2int[strs[1]]
                    bsem = rom2int[strs[2]]
                    regulation = int(strs[5])
                    ayasbybsr = (ayear,asem,byear,bsem,regulation)
                    mode = strs[6]
                    currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                        Dept=dept,Mode=mode,Regulation=regulation)
                    currentRegEventId = currentRegEventId[0].id
                    request.session['currentRegEventId'] = currentRegEventId
                    
                    if(byear==1):
                        reg_rgs = StudentInfo.objects.filter(AdmissionYear=ayear,Cycle=dept,Regulation=regulation)
                        reg_rgs = [(row.RegNo,row.Dept,row.Cycle) for row in reg_rgs]
                        not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1,BYear=1, PoA='R')

                        not_prom_regs = [row.RegNo for row in not_prom_regs]
                    
                        final_not_prom_regs = []
                        for row in reg_rgs:
                            roll = RollLists_Staging.objects.filter(RegNo=row[0], Dept=row[1], AYear=ayear,BYear=byear, Cycle=row[2], Regulation=regulation)
                            if(len(roll) ==0):
                                roll = RollLists_Staging(RegNo=row[0], Dept=row[1], AYear=ayear,BYear=byear, Cycle=row[2], Regulation=regulation)
                                roll.save()
                    
                        for reg in not_prom_regs:
                            s_info = StudentInfo.objects.get(RegNo=reg)
                            if(s_info.Cycle==dept):
                                final_not_prom_regs.append(reg)   
                        not_prom_regs = final_not_prom_regs
                        if(len( not_prom_regs) !=0):
                            form = RollListRegulationDifferanceForm(Options = (not_prom_regs,regulation))
                            if(len(not_prom_regs)!=0):
                                request.session['not_promoted_regno_firstyear'] = not_prom_regs
                                request.session['ayasbybsr'] = ayasbybsr
                            return render(request, 'SupExamDBRegistrations/RollListNotPromotedRegulation.html',{'form':form})
                        return (render(request, 'SupExamDBRegistrations/RollListGenerateSuccess.html'))
                            
                   
                    # for row in not_prom_regs:
                    #     roll = RollLists_Staging.objects.get(RegNo=row[0], Dept=row[1], AYear=ayear,BYear=byear, Cycle=row[2], Regulation=regulation)
                    #     if(len(roll) != 0):
                    #         roll.delete()
                        

                    # print(not_prom_regs)
                    # if(len(not_prom_regs)!=0):
                    #     request.session['not_prom_regs'] = (not_prom_regs,ayasbybsr)
                    #     return HttpResponseRedirect(reverse('FirstYearRollListsCycleHandler' )) 
                    # print(reg_rgs)
                    # print("here")
                    # print(not_prom_regs)
                       
                    else:
                        reg_rgs = RollLists_Staging.objects.filter(AYear=ayear-1,Dept=dept,BYear=byear-1,Regulation=regulation)
                        reg_rgs = [(row.RegNo,row.Dept,row.Cycle) for row in reg_rgs]
                        pres_not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1,BYear=byear)
                        present_not_prom_regs=[]
                        not_promoted_regno=[]
                        for reg in pres_not_prom_regs:
                            not_promoted_regno.append(reg.RegNo)

                        present_not_prom_regs = [row.RegNo for row in present_not_prom_regs]
                        prev_not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1, BYear=byear-1)
                        prev_not_prom_regs = [row.RegNo for row in prev_not_prom_regs]
                        final_regs = []
                        not_prom_prev_prev_bmode = NotPromoted.objects.filter(AYear = ayear-2, BYear= 1, PoA='B')
                        not_prom_prev_prev_bmode = [row.RegNo for row in not_prom_prev_prev_bmode]
                        not_promoted_prev_bmode =  NotPromoted.objects.filter(AYear = ayear-1, BYear= 1, PoA='B')
                        not_promoted_prev_bmode = [row.RegNo for row in not_promoted_prev_bmode]
                        for reg in not_prom_prev_prev_bmode:
                            if(reg not in  not_promoted_prev_bmode):
                                not_promoted_regno.append(reg)
                            
                        for reg in reg_rgs:
                            if(reg not in prev_not_prom_regs):
                                final_regs.append(reg)
                        # for reg in present_not_prom_regs:
                        #     s_info = StudentInfo.objects.get(RegNo=reg)
                        #     if(s_info.Regulation==regulation):
                        #         final_regs.append(reg)
                        for row in final_regs:
                            roll = RollLists_Staging.objects.filter(RegNo=row[0], Dept=row[1], AYear=ayear,BYear=byear, Cycle=row[2], Regulation=regulation)
                            if(len(roll) ==0):
                                roll = RollLists_Staging(RegNo=row[0], Dept=row[1], AYear=ayear,BYear=byear, Cycle=row[2], Regulation=regulation)
                                roll.save()
                        for row in prev_not_prom_regs:
                            roll = RollLists_Staging.objects.filter(RegNo=row[0], Dept=row[1], AYear=ayear,BYear=byear, Cycle=row[2], Regulation=regulation)
                            if(len(roll) != 0):
                                roll.delete()
                            #also remove from registrations staging table.
                            StudentRegistrations_Staging.objects.filter(RegNo=row[0],RegEventId=currentRegEventId).delete()  
                        if(len(not_promoted_regno) != 0):
                            request.session['not_promoted_regno'] = not_promoted_regno
                            request.session['ayasbybsr'] = ayasbybsr
                            form = RollListRegulationDifferanceForm(Options = (not_promoted_regno,regulation))
                            return render(request, 'SupExamDBRegistrations/RollListNotPromotedRegulation.html',{'form':form})

                        return (render(request, 'SupExamDBRegistrations/RollListGenerateSuccess.html'))
    else:
        form = GenerateRollListForm()
    return  render(request, 'SupExamDBRegistrations/generateRollList.html',{'form':form})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def first_year_rollLists_cycle_handler(request):
    not_prom_regs = request.session.get('not_promoted_regno')
    (ayear,asem,byear,bsem,regulation)=request.session.get('ayasbybsr')
    print(ayear)
    if(request.method == 'POST'):
        form = RollListsCycleHandlerForm(not_prom_regs,request.POST)
        print("In post")
        if(form.is_valid()):
            print("valid")
            for cIndex, sReg in enumerate(not_prom_regs):
                print(cIndex,sReg)
                if(form.cleaned_data.get('RadioMode'+str(sReg))):
                    cycle = form.cleaned_data.get('RadioMode'+str(sReg))
                    s_info = StudentInfo.objects.get(RegNo=sReg)
                    roll = RollLists_Staging(RegNo=sReg, Dept=s_info.Dept, AYear=ayear, BYear=byear, Cycle=cycle, Regulation=regulation)
                    s_info.Cycle=cycle
                    print(s_info.Dept)
                    s_info.save()
                    roll.save()
                    print(roll.Dept,roll.RegNo,roll.AYear,roll.BYear, roll.Cycle)
        return (render(request, 'SupExamDBRegistrations/RollListGenerateSuccess.html'))
    else:
        form = RollListsCycleHandlerForm(Options=not_prom_regs)
    return (render(request, 'SupExamDBRegistrations/RollListsCycleHandlerForm.html',{'form':form}))


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def rolllist_finalize(request):
    if request.method == 'POST':
        print(request.FILES, request.POST)
        form = RollListFinalizeForm(request.POST,request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            regEvent = form.cleaned_data['regID']
            strs = regEvent.split(':')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset = XLSX().create_dataset(data)
            errorRolls = []
            for i in range(len(dataset)):
                row = dataset[i]
                roll = RollLists_Staging.objects.filter(RegNo=row[0], AYear=ayear, Dept=dept, BYear=byear, Regulation=regulation)
                if len(roll) != 0:
                    checkRoll = RollLists.objects.filter(RegNo=roll[0].RegNo, AYear=roll[0].AYear, Dept=roll[0].Dept, \
                        BYear=roll[0].BYear, Cycle=roll[0].Cycle, Regulation=roll[0].Regulation)
                    if len(checkRoll) == 0:
                        finalRoll = RollLists(RegNo=roll[0].RegNo, AYear=roll[0].AYear, Dept=roll[0].Dept, \
                            BYear=roll[0].BYear, Cycle=roll[0].Cycle, Regulation=roll[0].Regulation )
                        finalRoll.save()
                else:
                    newRow = (row[0])
                    errorRolls.append(newRow)
            # if len(errorRolls) != 0:
            #     request.session['rollListErrRows'] = errorRolls
            #     request.session['currentRegEventId'] = currentRegEventId
            #     return redirect('FinalizeRollListErrorHandler')
            return render(request, 'SupExamDBRegistrations/FianlizeRollListsSuccess.html', {'errRows':errorRolls})
        else:
            print("Not valid")
            print(form.errors.as_data())
        return HttpResponse('Hi')
    else:
        form = RollListFinalizeForm()
    return render(request, 'SupexamDBRegistrations/RollListsFinalize.html', {'form':form})


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def RollList_Status(request):
    if request.method == 'POST':
        form = RollListStatusForm([],request.POST)
        if(form.is_valid):
            ayear=int(request.POST.get('aYear'))
            byear=int(request.POST.get('bYear'))
            dept=int(request.POST.get('dept'))
            print(ayear, byear, dept)
            if(byear==1):
                total_regs =[]
                reg_rgs = StudentInfo.objects.filter(AdmissionYear=ayear,Cycle=dept)
                reg_rgs = [row.RegNo for row in reg_rgs]
                total_regs += reg_rgs
                not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1,BYear=1, PoA='R')

                not_prom_regs = [row.RegNo for row in not_prom_regs]
                    
                final_not_prom_regs = []
                       
                for reg in not_prom_regs:
                    s_info = StudentInfo.objects.get(RegNo=reg)
                    if(s_info.Cycle==dept):
                            final_not_prom_regs.append(reg)   
                not_prom_regs = final_not_prom_regs
                if(len( not_prom_regs) !=0):
                    total_regs += not_prom_regs
                Option =[]
                for reg in total_regs:
                    roll = RollLists_Staging.objects.filter(RegNo=reg,AYear=ayear,BYear=byear)
                    if(len(roll)!=0):
                        Option.append((reg,roll[0].AYear,roll[0].BYear,roll[0].Regulation))
                    else:
                        Option =[(reg,'','','')] + Option
                form = RollListStatusForm(Option,request.POST )
                return (render(request, 'SupExamDBRegistrations/RollListStatus.html',{'form': form}))            
            else:
                        total_regs =[]
                        reg_rgs = RollLists_Staging.objects.filter(AYear=ayear-1,Dept=dept,BYear=byear-1)
                        reg_rgs = [row.RegNo for row in reg_rgs]
                        pres_not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1,BYear=byear)
                        present_not_prom_regs=[]
                        not_promoted_regno=[]
                        for reg in pres_not_prom_regs:
                            not_promoted_regno.append(reg.RegNo)

                        present_not_prom_regs = [row.RegNo for row in present_not_prom_regs]
                        prev_not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1, BYear=byear-1)
                        prev_not_prom_regs = [row.RegNo for row in prev_not_prom_regs]
                        final_regs = []
                        not_prom_prev_prev_bmode = NotPromoted.objects.filter(AYear = ayear-2, BYear= 1, PoA='B')
                        not_prom_prev_prev_bmode = [row.RegNo for row in not_prom_prev_prev_bmode]
                        not_promoted_prev_bmode =  NotPromoted.objects.filter(AYear = ayear-1, BYear= 1, PoA='B')
                        not_promoted_prev_bmode = [row.RegNo for row in not_promoted_prev_bmode]
                        for reg in not_prom_prev_prev_bmode:
                            if(reg not in  not_promoted_prev_bmode):
                                not_promoted_regno.append(reg)
                            
                        for reg in reg_rgs:
                            if(reg not in prev_not_prom_regs):
                                final_regs.append(reg)
                        total_regs += final_regs
                        print(total_regs) 
                        total_regs += not_promoted_regno
                        print(total_regs)
                        Option =[]
                        for reg in total_regs:
                            roll = RollLists_Staging.objects.filter(RegNo=reg,AYear=ayear,BYear=byear)
                            if(len(roll)!=0):
                                Option.append((reg,roll[0].AYear,roll[0].BYear,roll[0].Regulation))
                            else:
                                Option =[(reg,'','','')] + Option
                        form = RollListStatusForm(Option,request.POST)
                        return (render(request, 'SupExamDBRegistrations/RollListStatus.html',{'form': form}))            
    else:
        Option=[]
        form = RollListStatusForm(Options=Option)
        return render(request, 'SupexamDBRegistrations/RollListStatus.html', {'form':form})


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def regulation_differance_handler(request):
#     not_promoted_regno = request.session.get('not_promoted_regno')[0]
#     (ayear,asem,byear,bsem,regulation)= request.session.get('not_promoted_regno')[1]
#     if(request.method == 'POST'):
#         form = RollistRegulationDifferanceForm(not_promoted_regno,regulation,request.POST)
#         if(form.is_valid()):
#             for cIndex, sReg in enumerate(not_promoted_regno):
#                 print(cIndex,sReg)
#                 if(form.cleaned_data.get('RadioMode'+str(sReg))):
#                     choice = form.cleaned_data.get('RadioMode'+str(sReg))
#                     s_info = StudentInfo.objects.get(RegNo=sReg)
#                     roll = RollLists_Staging(RegNo=sReg, Dept=s_info.Dept, AYear=ayear, BYear=byear, Cycle=s_info.Cycle, Regulation=regulation)
#                     if(choice == 'YES'):
#                         roll.save()
#                         s_info.Regulation = regulation
#                         s_info.save()
#                     #else:

#         return (render(request, 'SupExamDBRegistrations/RollListGenerateSuccess.html'))
#     else:
#         form = RollistRegulationDifferanceForm(Options = (not_promoted_regno,regulation))
#         return (render(request, 'SupExamDBRegistrations/RollListNotPromotedRegulation.html',{'form':form}))








# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def rolllist_finalize_error_handler(request):
#     errRolls = request.session.get('rollListErrRows')
#     currentRegEventId = request.session.get('currentRegEventId')
#     if request.method == 'POST':
#         form = RollListErrorHandlerForm(errRolls, request.POST)
#         if form.is_valid():
#             for i in len(errRolls):
#                 if form.cleaned_data['Check'+str(errRolls[i])]:
#                     addRoll = RollLists(RegNo=errRolls[i])