from django.db import models
# from ExamStaffDB.models import BTFacultyInfo
# from superintendent.models import BTRegistrationStatus, BTMarksDistribution
# from ExamStaffDB.models import BTStudentInfo



# Create your models here.


class BTSubjects_Staging(models.Model):
    SubCode = models.CharField(max_length=10) 
    SubName= models.CharField(max_length=100)
    Creditable = models.IntegerField()
    Credits = models.IntegerField()
    OfferedBy=models.IntegerField()
    Type = models.CharField(max_length=10)
    Category = models.CharField(max_length=10)
    OfferedBy = models.IntegerField()
    RegEventId = models.ForeignKey('superintendent.BTRegistrationStatus', on_delete=models.CASCADE)
    MarkDistribution = models.ForeignKey('superintendent.BTMarksDistribution', on_delete=models.CASCADE)
    DistributionRatio = models.TextField()

    class Meta:
        db_table = 'BTSubjects_Staging'
        unique_together = ('SubCode', 'RegEventId')
        managed = True


class BTSubjects(models.Model):
    SubCode = models.CharField(max_length=10) 
    SubName= models.CharField(max_length=100)
    Creditable = models.IntegerField()
    Credits = models.IntegerField()
    OfferedBy=models.IntegerField()
    Type = models.CharField(max_length=10)
    Category = models.CharField(max_length=10)
    OfferedBy = models.IntegerField()
    RegEventId = models.ForeignKey('superintendent.BTRegistrationStatus', on_delete=models.CASCADE)
    MarkDistribution = models.ForeignKey('superintendent.BTMarksDistribution', on_delete=models.CASCADE)
    DistributionRatio = models.TextField()
    
    class Meta:
        db_table = 'BTSubjects'
        unique_together = ('SubCode', 'RegEventId')
        managed = True



class BTRollLists(models.Model):
    CYCLE_CHOICES = (
        (10,'PHYSICS'),
        (9,'CHEMISTRY')
    )
    student = models.ForeignKey('ExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('superintendent.BTRegistrationStatus', on_delete=models.CASCADE)
    Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)
    Section = models.CharField(max_length=2, default='NA')
    class Meta:
        db_table = 'BTRollLists'
        unique_together = ('student', 'RegEventId')
        managed = True


    
class BTRollLists_Staging(models.Model):
    CYCLE_CHOICES = (
        (10,'PHYSICS'),
        (9,'CHEMISTRY')
    )
    student = models.ForeignKey('ExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('superintendent.BTRegistrationStatus', on_delete=models.CASCADE)
    Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)
    Section = models.CharField(max_length=2, default='NA')
    class Meta:
        db_table = 'BTRollLists_Staging'
        unique_together = ('student', 'RegEventId')
        managed = True


class BTRegulationChange(models.Model):
    RegEventId= models.ForeignKey('superintendent.BTRegistrationStatus', on_delete=models.CASCADE)
    student = models.ForeignKey('ExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    PreviousRegulation = models.IntegerField()
    PresentRegulation = models.IntegerField()
    class Meta:
        db_table  = 'BTRegulationChange'
        managed = True



class BTNotRegistered(models.Model):
    RegEventId= models.ForeignKey('superintendent.BTRegistrationStatus', on_delete=models.CASCADE)
    Student = models.ForeignKey('ExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    Registered = models.BooleanField()
    class Meta:
        db_table = 'BTNotRegistered'
        unique_together = (('RegEventId', 'Student'))
        managed = True


class BTStudentRegistrations(models.Model):
    RegNo = models.IntegerField()
    RegEventId = models.IntegerField()
    Mode = models.IntegerField()
    sub_id = models.IntegerField()
    class Meta:
        db_table = 'BTStudentRegistrations'
        unique_together = (('RegNo', 'RegEventId', 'sub_id'))
        managed = True

class BTStudentRegistrations_Staging(models.Model):
    RegNo = models.IntegerField()
    RegEventId = models.IntegerField()
    Mode = models.IntegerField()
    sub_id = models.IntegerField()
    class Meta:
        db_table = 'BTStudentRegistrations_Staging'
        unique_together = (('RegNo', 'RegEventId', 'sub_id'))
        managed = True


class BTDroppedRegularCourses(models.Model):
    student = models.ForeignKey('ExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    subject = models.ForeignKey(BTSubjects, on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('superintendent.BTRegistrationStatus', on_delete=models.CASCADE)
    Registered = models.BooleanField()
    class Meta:
        db_table = 'BTDroppedRegularCourses'
        unique_together = (('student', 'subject'))
        managed = True



class BTStudentBacklogs(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    sub_id = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=50)
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Credits = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Grade = models.CharField(max_length=2)
    GP = models.IntegerField()
    Regulation = models.IntegerField()
    AYASBYBS = models.IntegerField()
    class Meta:
        db_table = 'BTStudentBacklogsMV'
        managed = False
    def __str__(self):        
        return f'{self.SubName} ({self.SubCode})'


class BTStudentMakeups(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    sub_id = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=50)
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Credits = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Grade = models.CharField(max_length=2)
    GP = models.IntegerField()
    Regulation = models.IntegerField()
    AYASBYBS = models.IntegerField()
    class Meta:
        db_table = 'BTStudentMakeupBacklogsMV'
        managed = False


class BTStudentGradePoints(models.Model):
    RegNo = models.IntegerField()
    sub_id = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=100)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
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
    AYASBYBS = models.IntegerField()
    class Meta:
        db_table = 'BTStudentGradePointsMV'
        managed = False


class BTRegularRegistrationSummary(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Dept = models.IntegerField()
    Regulation = models.IntegerField()
    RegisteredSubjects = models.CharField(max_length=300)
    class Meta:
        db_table = 'BTRegularRegistrationSummaryV'
        managed = False

class BTBacklogRegistrationSummary(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Dept = models.IntegerField()
    Regulation = models.IntegerField()
    RegisteredSubjects = models.CharField(max_length=300)
    class Meta:
        db_table = 'BTBacklogRegistrationSummaryV'
        managed = False

class BTMakeupRegistrationSummary(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Dept = models.IntegerField()
    Regulation = models.IntegerField()
    RegisteredSubjects = models.CharField(max_length=300)
    class Meta:
        db_table = 'BTMakeupRegistrationSummaryV'
        managed = False


class BTGradeChallenge(models.Model):
    Registration = models.ForeignKey(BTStudentRegistrations, on_delete=models.CASCADE)
    prev_marks = models.TextField()
    updated_marks = models.TextField()
    prev_grade = models.CharField(max_length=2)
    updated_grade = models.CharField(max_length=2)

    class Meta:
        db_table = 'BTGradeChallenge'
        managed = True

class BTNotPromoted(models.Model):
    AYear = models.IntegerField()
    BYear = models.IntegerField()
    Regulation = models.IntegerField()
    student = models.ForeignKey('ExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    PoA = models.CharField(max_length=1) #S for Study Mode and R for Cancellation and Repeat
    class Meta:
        db_table = 'BTNotPromoted'
        unique_together=('AYear', 'BYear', 'Regulation', 'student')
        managed = True

class BTFacultyAssignment(models.Model):
    Subject = models.ForeignKey(BTSubjects, on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('superintendent.BTRegistrationStatus', on_delete=models.CASCADE)
    Faculty = models.ForeignKey('ExamStaffDB.BTFacultyInfo', on_delete=models.CASCADE, related_name='faculty_facultyInfo')
    Coordinator = models.ForeignKey('ExamStaffDB.BTFacultyInfo', on_delete=models.CASCADE, related_name='co_ordinator_facultyInfo')
    Section = models.CharField(max_length=2, default='NA')
    MarksStatus = models.IntegerField(default=1)

    class Meta:
        db_table = 'BTFacultyAssignment'
        unique_together = (
            # ('Subject', 'RegEventId', 'Coordinator', 'Section'), 
            ('Subject', 'RegEventId', 'Faculty', 'Section')
        )
        managed = True
