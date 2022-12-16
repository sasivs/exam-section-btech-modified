from django.db import models
from simple_history.models import HistoricalRecords
# from ExamStaffDB.models import BTFacultyInfo
# from superintendent.models import BTRegistrationStatus, BTMarksDistribution
# from ExamStaffDB.models import BTStudentInfo



# Create your models here.


class BTSubjects_Staging(models.Model):
    RegEventId = models.ForeignKey('ADAUGDB.BTRegistrationStatus', on_delete=models.CASCADE)
    course = models.ForeignKey('ADAUGDB.BTCourses', on_delete=models.CASCADE, default=0)
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTSubjects_Staging'
        unique_together = ('course', 'RegEventId')
        managed = True


class BTSubjects(models.Model):
    RegEventId = models.ForeignKey('ADAUGDB.BTRegistrationStatus', on_delete=models.CASCADE)
    course = models.ForeignKey('ADAUGDB.BTCourses', on_delete=models.CASCADE, default=0)
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'BTSubjects'
        unique_together = ('course', 'RegEventId')
        managed = True



class BTRollLists(models.Model):
    CYCLE_CHOICES = (
        (10,'PHYSICS'),
        (9,'CHEMISTRY')
    )
    student = models.ForeignKey('BTExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('ADAUGDB.BTRegistrationStatus', on_delete=models.CASCADE)
    Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)
    Section = models.CharField(max_length=2, default='NA')
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTRollLists'
        unique_together = ('student', 'RegEventId')
        managed = True


    
class BTRollLists_Staging(models.Model):
    CYCLE_CHOICES = (
        (10,'PHYSICS'),
        (9,'CHEMISTRY')
    )
    student = models.ForeignKey('BTExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('ADAUGDB.BTRegistrationStatus', on_delete=models.CASCADE)
    Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)
    Section = models.CharField(max_length=2, default='NA')
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTRollLists_Staging'
        unique_together = ('student', 'RegEventId')
        managed = True


class BTRegulationChange(models.Model):
    RegEventId= models.ForeignKey('ADAUGDB.BTRegistrationStatus', on_delete=models.CASCADE)
    student = models.ForeignKey('BTExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    PreviousRegulation = models.FloatField()
    PresentRegulation = models.FloatField()
    history = HistoricalRecords()
    class Meta:
        db_table  = 'BTRegulationChange'
        managed = True



class BTNotRegistered(models.Model):
    RegEventId= models.ForeignKey('ADAUGDB.BTRegistrationStatus', on_delete=models.CASCADE)
    Student = models.ForeignKey('BTExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    Registered = models.BooleanField()
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTNotRegistered'
        unique_together = (('RegEventId', 'Student'))
        managed = True


class BTStudentRegistrations(models.Model):
    student = models.ForeignKey('BTco_ordinator.BTRollLists', on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('ADAUGDB.BTRegistrationStatus', db_column='RegEventId', on_delete=models.CASCADE)
    Mode = models.IntegerField()
    sub_id = models.ForeignKey('BTco_ordinator.BTSubjects', db_column='sub_id', on_delete=models.CASCADE)
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTStudentRegistrations'
        unique_together = (('student', 'RegEventId', 'sub_id'))
        managed = True

class BTStudentRegistrations_Staging(models.Model):
    student = models.ForeignKey('BTco_ordinator.BTRollLists_Staging', on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('ADAUGDB.BTRegistrationStatus', db_column='RegEventId', on_delete=models.CASCADE)
    Mode = models.IntegerField()
    sub_id = models.ForeignKey('BTco_ordinator.BTSubjects', db_column='sub_id', on_delete=models.CASCADE)
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTStudentRegistrations_Staging'
        unique_together = (('student', 'RegEventId', 'sub_id'))
        managed = True


class BTDroppedRegularCourses(models.Model):
    student = models.ForeignKey('BTExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    subject = models.ForeignKey('BTco_ordinator.BTSubjects', on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('ADAUGDB.BTRegistrationStatus', on_delete=models.CASCADE)
    Registered = models.BooleanField()
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTDroppedRegularCourses'
        unique_together = (('student', 'subject'))
        managed = True



class BTStudentBacklogs(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    sub_id = models.IntegerField()
    # Category = models.CharField(max_length=10, default='None')
    # Type = models.CharField(max_length=10, default='None')
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=50)
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Credits = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Grade = models.CharField(max_length=2)
    GP = models.IntegerField()
    Regulation = models.FloatField()
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
    # Category = models.CharField(max_length=10)
    # Type = models.CharField(max_length=10)
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Credits = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Grade = models.CharField(max_length=2)
    GP = models.IntegerField()
    Regulation = models.FloatField()
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
    Regulation = models.FloatField()
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
    Regulation = models.FloatField()
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
    Regulation = models.FloatField()
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
    Regulation = models.FloatField()
    RegisteredSubjects = models.CharField(max_length=300)
    class Meta:
        db_table = 'BTMakeupRegistrationSummaryV'
        managed = False


class BTNotPromoted(models.Model):
    AYear = models.IntegerField()
    BYear = models.IntegerField()
    Regulation = models.FloatField()
    student = models.ForeignKey('BTExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    PoA_sem1 = models.CharField(max_length=1) #S for Study Mode and R for Cancellation and Repeat
    PoA_sem2 = models.CharField(max_length=1, default='R') #S for Study Mode and R for Cancellation and Repeat
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTNotPromoted'
        unique_together=('AYear', 'BYear', 'Regulation', 'student')
        managed = True

class BTFacultyAssignment(models.Model):
    Subject = models.ForeignKey(BTSubjects, on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('ADAUGDB.BTRegistrationStatus', on_delete=models.CASCADE)
    Faculty = models.ForeignKey('BTExamStaffDB.BTFacultyInfo', on_delete=models.CASCADE, related_name='faculty_facultyInfo')
    Coordinator = models.ForeignKey('BTExamStaffDB.BTFacultyInfo', on_delete=models.CASCADE, related_name='co_ordinator_facultyInfo')
    Section = models.CharField(max_length=2, default='NA')
    MarksStatus = models.IntegerField(default=1)
    GradesStatus = models.IntegerField(default=1)
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTFacultyAssignment'
        unique_together = (
            # ('Subject', 'RegEventId', 'Coordinator', 'Section'), 
            ('Subject', 'RegEventId', 'Faculty', 'Section')
        )
        managed = True


class BTNPRStudentRegistrations(models.Model): # NPR=Not promoted repeat mode
    student_id = models.IntegerField()
    RegEventId_id = models.IntegerField()
    Mode = models.IntegerField()
    sub_id_id = models.IntegerField()
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTNPRStudentRegistrations'
        unique_together = (('student_id', 'RegEventId_id', 'sub_id_id'))
        managed = True


class BTNPRStudentGrades(models.Model):
    RegId= models.IntegerField()
    RegEventId = models.IntegerField()
    Regulation = models.FloatField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTNPRStudentGrades'
        constraints = [
            models.UniqueConstraint(fields=['RegId'], name='unique_BTNPR_StudentGrades_registration')
        ]
        managed = True

class BTNPRRollLists(models.Model):
    CYCLE_CHOICES = (
        (10,'PHYSICS'),
        (9,'CHEMISTRY')
    )
    student_id = models.IntegerField()
    RegEventId_id =models.IntegerField()
    Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)
    Section = models.CharField(max_length=2, default='NA')
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTNPRRollLists'
        unique_together = (('student_id', 'RegEventId_id'))
        managed = True

class BTNPRNotRegistered(models.Model):
    RegEventId_id = models.IntegerField()
    Student_id = models.IntegerField()
    Registered = models.BooleanField()
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTNPRNotRegistered'
        unique_together = (('RegEventId_id', 'Student_id'))
        managed = True

class BTNPRDroppedRegularCourses(models.Model):
    student_id = models.IntegerField()
    subject_id =models.IntegerField()
    RegEventId_id = models.IntegerField()
    Registered = models.BooleanField()
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTNPRDroppedRegularCourses'
        unique_together = (('student_id', 'subject_id'))
        managed = True

class BTNPRMarks(models.Model):
    Registration_id = models.IntegerField()
    Marks = models.TextField()
    TotalMarks = models.IntegerField()
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTNPRMarks'
        constraints = [
            models.UniqueConstraint(fields=['Registration_id'], name='unique_BTNPR_marks_registration')
        ]
        managed = True

    def get_total_marks(self):
        marks_dis = self.Marks.split(',')
        marks_dis = [mark.split('+') for mark in marks_dis]
        subject = BTSubjects.objects.filter(id=self.Registration.sub_id).first()
        ratio = subject.DistributionRatio.split(':')
        total_parts = 0
        for part in ratio:
            total_parts += int(part)
        total = 0
        for index in range(len(marks_dis)):
            marks_row = marks_dis[index]
            sub_total = 0
            for mark in marks_row:
                sub_total += int(mark)
            total = sub_total*int(ratio[index])
        return round(total/total_parts)