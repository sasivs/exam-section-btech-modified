from django.db import models
from MTsuperintendent.constants import DEPARTMENTS, YEARS, SEMS
from MTco_ordinator.models import MTStudentRegistrations

# Create your models here.

class MTRegistrationStatus(models.Model):
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    MYear = models.IntegerField()
    MSem = models.IntegerField()
    Regulation = models.IntegerField()
    Dept = models.IntegerField()
    Mode = models.CharField(max_length=1) # R for Regular B for Backlog
    Status = models.IntegerField()
    RollListStatus = models.IntegerField()
    RollListFeeStatus = models.IntegerField(default=0)
    RegistrationStatus = models.IntegerField()
    MarksStatus = models.IntegerField()
    GradeStatus = models.IntegerField()
    class Meta:
        db_table = 'MTRegistration_Status'
        constraints=[
            models.UniqueConstraint(fields=['AYear','ASem','MYear','MSem','Regulation','Dept','Mode'],name='unique_MTRegistration_status')
        ]
        managed = True
    def __str__(self):
        name =  str(DEPARTMENTS[self.Dept-1]) + ':' + str(YEARS[self.MYear]) + ':' + str(SEMS[self.MSem]) + ':' + \
            str(self.AYear) + ':' + str(self.ASem) + ':' + str(self.Regulation) + ':' + str(self.Mode)
        return name

class MTGradeChallenge(models.Model):
    Registration = models.ForeignKey(MTStudentRegistrations, on_delete=models.CASCADE)
    prev_marks = models.TextField()
    updated_marks = models.TextField()
    prev_grade = models.CharField(max_length=2)
    updated_grade = models.CharField(max_length=2)

    class Meta:
        db_table = 'MTGradeChallenge'
        managed = True