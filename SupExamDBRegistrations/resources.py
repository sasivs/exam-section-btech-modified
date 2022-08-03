from .models import Subjects_Staging, StudentInfo, FacultyInfo, StudentGrades_Staging, GradePoints, GradeChallenge, NotPromoted
from import_export import resources


# class StudentInfoResource(resources.ModelResource):
#     class Meta:
#         model = StudentInfo 

# class SubjectStagingResource(resources.ModelResource):
#     class Meta:
#         model = Subjects_Staging

# class FacultyInfoResource(resources.ModelResource):
#     class Meta:
#         model = FacultyInfo

class StudentGrades_StagingResource(resources.ModelResource):
    class Meta:
        model = StudentGrades_Staging

# class GradePointsResource(resources.ModelResource):
#     class Meta:
#         model = GradePoints

class GradeChallengeResource(resources.ModelResource):
    class Meta:
        model = GradeChallenge

# class NotPromotedResource(resources.ModelResource):
#     class Meta:
#         model = NotPromoted

