from django.db import models
# from MTExamStaffDB.models import MTFacultyInfo
# from MTsuperintendent.models import MTRegistrationStatus, MTMarksDistribution
# from MTExamStaffDB.models import MTStudentInfo


class MTSubjects_Staging(models.Model):
    SubCode = models.CharField(max_length=10) 
    SubName= models.CharField(max_length=100)
    Creditable = models.IntegerField()
    Credits = models.IntegerField()
    OfferedBy = models.IntegerField(default=0)
    Type = models.CharField(max_length=10)
    Category = models.CharField(max_length=10)
    RegEventId = models.ForeignKey('MTsuperintendent.MTRegistrationStatus', on_delete=models.CASCADE)
    ProgrammeCode = models.IntegerField()
    MarkDistribution = models.ForeignKey('MTsuperintendent.MTMarksDistribution', on_delete=models.CASCADE)
    DistributionRatio = models.TextField()

    class Meta:
        db_table = 'MTSubjects_Staging'
        unique_together = ('SubCode', 'RegEventId')
        managed = True

class MTSubjects(models.Model):
    SubCode = models.CharField(max_length=10) 
    SubName= models.CharField(max_length=100)
    Creditable = models.IntegerField()
    Credits = models.IntegerField()
    OfferedBy = models.IntegerField(default=0)
    Type = models.CharField(max_length=10)
    Category = models.CharField(max_length=10)
    RegEventId = models.ForeignKey('MTsuperintendent.MTRegistrationStatus', on_delete=models.CASCADE)
    ProgrammeCode = models.IntegerField()
    MarkDistribution = models.ForeignKey('MTsuperintendent.MTMarksDistribution', on_delete=models.CASCADE)
    DistributionRatio = models.TextField()

    class Meta:
        db_table = 'MTSubjects'
        unique_together = ('SubCode', 'RegEventId')
        managed = True



class MTRollLists_Staging(models.Model):
   
    student = models.ForeignKey('MTExamStaffDB.MTStudentInfo', on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('MTsuperintendent.MTRegistrationStatus', on_delete=models.CASCADE)
    class Meta:
        db_table = 'MTRollLists_Staging'
        unique_together=(('student','RegEventId'))
        managed = True

class MTRollLists(models.Model):
   
    student = models.ForeignKey('MTExamStaffDB.MTStudentInfo', on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('MTsuperintendent.MTRegistrationStatus', on_delete=models.CASCADE)
    class Meta:
        db_table = 'MTRollLists'
        unique_together=(('student','RegEventId'))
        managed = True

class MTRegulationChange(models.Model):
    RegEventId= models.ForeignKey('MTsuperintendent.MTRegistrationStatus', on_delete=models.CASCADE)
    student = models.ForeignKey('MTExamStaffDB.MTStudentInfo', on_delete=models.CASCADE)
    PreviousRegulation = models.IntegerField()
    PresentRegulation = models.IntegerField()
    class Meta:
        db_table  = 'MTRegulationChange'
        managed = True

class MTNotRegistered(models.Model):
    RegEventId= models.ForeignKey('MTsuperintendent.MTRegistrationStatus', on_delete=models.CASCADE)
    Student = models.ForeignKey('MTExamStaffDB.MTStudentInfo', on_delete=models.CASCADE)
    Registered = models.BooleanField()
    class Meta:
        db_table = 'MTNotRegistered'
        unique_together = (('RegEventId', 'Student'))
        managed = True


class MTStudentRegistrations(models.Model):
    RegNo = models.IntegerField()
    RegEventId=models.IntegerField()
    Mode = models.IntegerField() # 0 is exam mode and 1 is study mode
    sub_id=models.IntegerField()
    class Meta:
        db_table = 'MTStudentRegistrations'
        unique_together = (('RegNo', 'RegEventId', 'sub_id'))
        managed = True

class MTStudentRegistrations_Staging(models.Model):
    RegNo = models.IntegerField()
    RegEventId=models.IntegerField()
    Mode = models.IntegerField() # 0 is exam mode and 1 is study mode
    sub_id=models.IntegerField()
    class Meta:
        db_table = 'MTStudentRegistrations_Staging'
        unique_together = (('RegNo', 'RegEventId', 'sub_id'))
        managed =True

class MTStudentBacklogs(models.Model):
    RegNo = models.IntegerField()
    sub_id=models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=50)
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Credits = models.IntegerField()
    MYear = models.IntegerField()
    MSem = models.IntegerField()
    Grade = models.CharField(max_length=2)
    Regulation = models.IntegerField()
    AYASMYMS = models.IntegerField()
    class Meta:
        db_table = 'MTStudentBacklogsMV'
        managed = False
    def __str__(self):        
        return f'{self.SubName} ({self.SubCode})'

class MTStudentMakeups(models.Model):
    RegNo = models.IntegerField()
    sub_id = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=50)
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Credits = models.IntegerField()
    MYear = models.IntegerField()
    MSem = models.IntegerField()
    Grade = models.CharField(max_length=2)
    GP = models.IntegerField()
    Regulation = models.IntegerField()
    AYASMYMS = models.IntegerField()
    class Meta:
        db_table = 'MTStudentMakeupBacklogsMV'
        managed = False


class MTStudentGradePoints(models.Model):
    RegNo = models.IntegerField()
    sub_id = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=100)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    MYear = models.IntegerField()
    MSem = models.IntegerField()
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    Regulation = models.IntegerField()
    Creditable = models.IntegerField()
    Credits = models.IntegerField()
    Type = models.CharField(max_length=10)
    Category = models.CharField(max_length=10)
    Points = models.IntegerField()
    GP = models.IntegerField()
    AYASMYMS = models.IntegerField()
    class Meta:
        db_table = 'MTStudentGradePointsMV'
        managed = False




class MTRegularRegistrationSummary(models.Model):
    RegNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    MYear = models.IntegerField()
    MSem = models.IntegerField()
    Dept = models.IntegerField()
    Regulation = models.IntegerField()
    RegisteredSubjects = models.CharField(max_length=300)
    class Meta:
        db_table = 'MTRegularRegistrationSummaryV'
        managed = False

class MTBacklogRegistrationSummary(models.Model):
    RegNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    MYear = models.IntegerField()
    MSem = models.IntegerField()
    Dept = models.IntegerField()
    Regulation = models.IntegerField()
    RegisteredSubjects = models.CharField(max_length=300)
    class Meta:
        db_table = 'MTBacklogRegistrationSummaryV'
        managed = False

class MTMakeupRegistrationSummary(models.Model):
    RegNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    MYear = models.IntegerField()
    MSem = models.IntegerField()
    Dept = models.IntegerField()
    Regulation = models.IntegerField()
    RegisteredSubjects = models.CharField(max_length=300)
    class Meta:
        db_table = 'MTMakeupRegistrationSummaryV'
        managed = False

class MTGradeChallenge(models.Model):
    Registration = models.ForeignKey(MTStudentRegistrations, on_delete=models.CASCADE)
    prev_marks = models.TextField()
    updated_marks = models.TextField()
    prev_grade = models.CharField(max_length=2)
    updated_grade = models.CharField(max_length=2)

    class Meta:
        db_table = 'MTGradeChallenge'
        managed = True

class MTFacultyAssignment(models.Model):
    Subject = models.ForeignKey(MTSubjects, on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('MTsuperintendent.MTRegistrationStatus', on_delete=models.CASCADE)
    Faculty = models.ForeignKey('MTExamStaffDB.MTFacultyInfo', on_delete=models.CASCADE, related_name='faculty_facultyInfo', default=0)
    Coordinator = models.ForeignKey('MTExamStaffDB.MTFacultyInfo', on_delete=models.CASCADE, related_name='co_ordinator_facultyInfo', default=0)
    MarksStatus = models.IntegerField(default=1)

    class Meta:
        db_table = 'MTFacultyAssignment'
        unique_together = (
            # ('Subject', 'RegEventId', 'Coordinator', 'Section'), 
            ('Subject', 'RegEventId', 'Faculty')
        )
        managed = True

