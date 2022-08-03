from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
# from MTExamStaffDB.models import MTFacultyInfo
User = get_user_model()


class MTFaculty_user(models.Model):
    User= models.ForeignKey(User, on_delete=models.CASCADE)
    Faculty = models.ForeignKey('MTExamStaffDB.MTFacultyInfo', on_delete=models.CASCADE)
    AssignDate = models.DateTimeField(auto_now_add=True)
    RevokeDate = models.DateTimeField(null=True)
    class Meta:
        db_table = 'MTFaculty_user'
        unique_together=(('User','Faculty','AssignDate','RevokeDate'))
        managed = True


class MTCoordinator(models.Model):
    User= models.ForeignKey(User, on_delete=models.CASCADE)
    Faculty = models.ForeignKey('MTExamStaffDB.MTFacultyInfo', on_delete=models.CASCADE)
    Dept = models.IntegerField()
    MYear = models.IntegerField()
    AssignDate = models.DateTimeField(auto_now_add=True)
    RevokeDate = models.DateTimeField(null=True)
    class Meta:
        db_table = 'MTFaculty_Coordinator'
        unique_together=(('User','Faculty','AssignDate','RevokeDate'))
        managed = True

