from import_export import resources
from superintendent.models import GradePoints

class GradePointsResource(resources.ModelResource):
    class Meta:
        model = GradePoints