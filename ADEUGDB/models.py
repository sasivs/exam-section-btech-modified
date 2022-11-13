from io import open_code
from django.db import models
from django.contrib.auth import get_user_model
from BTco_ordinator.models import BTSubjects
# from ExamStaffDB.models import BTFacultyInfo
from ADEUGDB.constants import DEPARTMENTS, YEARS, SEMS
from BTco_ordinator.models import BTStudentRegistrations


User = get_user_model()

class BTBranchChanges(models.Model):
    student = models.ForeignKey('BTExamStaffDB.BTStudentInfo', on_delete=models.CASCADE)
    CurrentDept = models.IntegerField()
    NewDept = models.IntegerField()
    AYear = models.IntegerField()
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

    class Meta:
        db_table = 'BTGradeChallenge'
        managed = True


class BTYearMandatoryCredits(models.Model):
    Regulation = models.IntegerField()
    Dept = models.IntegerField()
    BYear = models.IntegerField()
    Credits = models.IntegerField()
    class Meta:
        db_table = 'BTYearMandatoryCredits'
        unique_together = (('Regulation', 'Dept', 'BYear'))
        managed = True



