from import_export import resources
from MTsuperintendent.models import MTGradePoints

class GradePointsResource(resources.ModelResource):
    class Meta:
        model = MTGradePoints