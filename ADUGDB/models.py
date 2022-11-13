from django.db import models
from BTsuperintendent.constants import DEPARTMENTS, SEMS, YEARS

# Create your models here.

class BTRegistrationStatus(models.Model):
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Regulation = models.IntegerField()
    Dept = models.IntegerField()
    Mode = models.CharField(max_length=1) # R for Regular B for Backlog
    Status = models.IntegerField()
    RollListStatus = models.IntegerField()
    RollListFeeStatus = models.IntegerField()
    OERollListStatus = models.IntegerField()
    OERegistartionStatus = models.IntegerField()
    RegistrationStatus = models.IntegerField()
    MarksStatus = models.IntegerField()
    GradeStatus = models.IntegerField()
    class Meta:
        db_table = 'BTRegistration_Status'
        constraints = [
            models.UniqueConstraint(fields=['AYear', 'ASem', 'BYear', 'BSem', 'Regulation', 'Dept', 'Mode'], name='unique_BTRegistrationstatus')
        ]
        managed = True

    def __str__(self):
        name =  str(DEPARTMENTS[self.Dept-1]) + ':' + str(YEARS[self.BYear]) + ':' + str(SEMS[self.BSem]) + ':' + \
            str(self.AYear) + ':' + str(self.ASem) + ':' + str(self.Regulation) + ':' + str(self.Mode)
        return name


class BTGradeChallenge(models.Model):
    Registration = models.ForeignKey('BTco_ordinator.BTStudentRegistrations', on_delete=models.CASCADE)
    prev_marks = models.TextField()
    updated_marks = models.TextField()
    prev_grade = models.CharField(max_length=2)
    updated_grade = models.CharField(max_length=2)

    class Meta:
        db_table = 'BTGradeChallenge'
        managed = True