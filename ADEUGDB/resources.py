from import_export import resources
from ADAUGDB.models import BTGradePoints, BTCourses, BTOpenElectiveRollLists

class GradePointsResource(resources.ModelResource):
    class Meta:
        model = BTGradePoints

class BTCoursesResource(resources.ModelResource):
    class Meta:
        model = BTCourses

class BTOpenElectiveRollListsResource(resources.ModelResource):
    class Meta:
        model = BTOpenElectiveRollLists
