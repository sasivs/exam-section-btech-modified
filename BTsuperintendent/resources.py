from import_export import resources
from BTsuperintendent.models import BTGradePoints,BTOpenElectiveRollLists

class GradePointsResource(resources.ModelResource):
    class Meta:
        model = BTGradePoints

class BTOpenElectiveRollListsResource(resources.ModelResource):
    class Meta:
        model = BTOpenElectiveRollLists