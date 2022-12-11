from io import open_code
from django.db import models
from django.contrib.auth import get_user_model
from BTco_ordinator.models import BTSubjects
# from ExamStaffDB.models import BTFacultyInfo
from ADEUGDB.constants import DEPARTMENTS, YEARS, SEMS
from BTco_ordinator.models import BTStudentRegistrations
from simple_history.models import HistoricalRecords


User = get_user_model()

class BTHeldIn(models.Model):
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    AYASBYBS = models.IntegerField()
    HeldInMonth = models.CharField(max_length=10)
    HeldInYear = models.IntegerField()
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'BTHeldIn'
        constraints = [
            models.UniqueConstraint(fields=['AYASBYBS'], name='unique_ayasbybs_btheldin')
        ]
        managed = True

class BTBranchChanges(models.Model):
    student = models.ForeignKey('BTExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    CurrentDept = models.IntegerField()
    NewDept = models.IntegerField()
    AYear = models.IntegerField()
    history = HistoricalRecords()
    
    class Meta:
        db_table = 'BTBranchChanges'
        constraints = [
            models.UniqueConstraint(fields=['AYear', 'student'], name='unique_BTbranch_change')
        ]
        managed = True


class BTGradeChallenge(models.Model):
    Registration = models.ForeignKey('BTco_ordinator.BTStudentRegistrations', on_delete=models.CASCADE)
    prev_marks = models.TextField()
    updated_marks = models.TextField()
    prev_grade = models.CharField(max_length=2)
    updated_grade = models.CharField(max_length=2)
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTGradeChallenge'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique_BTGradeChallenge_Registration')
        ] 
        managed = True


class BTYearMandatoryCredits(models.Model):
    Regulation = models.IntegerField()
    Dept = models.IntegerField()
    BYear = models.IntegerField()
    Credits = models.IntegerField()
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTYearMandatoryCredits'
        unique_together = (('Regulation', 'Dept', 'BYear'))
        managed = True



