from import_export import resources
from ExamStaffDB.models import StudentInfo, FacultyInfo


class StudentInfoResource(resources.ModelResource):
    class Meta:
        model = StudentInfo 

class FacultyInfoResource(resources.ModelResource):
    class Meta:
        model = FacultyInfo