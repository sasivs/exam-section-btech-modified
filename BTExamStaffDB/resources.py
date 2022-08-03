from import_export import resources
from BTExamStaffDB.models import BTStudentInfo, BTFacultyInfo


class StudentInfoResource(resources.ModelResource):
    class Meta:
        model = BTStudentInfo 

class FacultyInfoResource(resources.ModelResource):
    class Meta:
        model = BTFacultyInfo