from import_export import resources
from MTExamStaffDB.models import MTStudentInfo, MTFacultyInfo


class StudentInfoResource(resources.ModelResource):
    class Meta:
        model = MTStudentInfo 

class FacultyInfoResource(resources.ModelResource):
    class Meta:
        model = MTFacultyInfo