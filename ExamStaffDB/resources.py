from import_export import resources
from ExamStaffDB.models import BTStudentInfo, BTFacultyInfo


class StudentInfoResource(resources.ModelResource):
    class Meta:
        model = BTStudentInfo 

class FacultyInfoResource(resources.ModelResource):
    class Meta:
        model = BTFacultyInfo