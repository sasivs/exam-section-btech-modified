from import_export import resources
from BTsuperintendent.models import BTGradePoints

class GradePointsResource(resources.ModelResource):
    class Meta:
        model = BTGradePoints