from import_export import resources
from BTsuperintendent.models import BTGradePoints, BTCourses

class GradePointsResource(resources.ModelResource):
    class Meta:
        model = BTGradePoints

class BTCoursesResource(resources.ModelResource):
    class Meta:
        model = BTCourses