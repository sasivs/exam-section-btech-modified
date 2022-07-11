from import_export import resources
from ExamStaffDB.models import StudentInfo


class StudentInfoResource(resources.ModelResource):
    class Meta:
        model = StudentInfo 