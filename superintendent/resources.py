from import_export import resources
from superintendent.models import BTGradePoints

class GradePointsResource(resources.ModelResource):
    class Meta:
        model = BTGradePoints