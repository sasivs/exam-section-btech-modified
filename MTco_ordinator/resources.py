from import_export import resources
from MTco_ordinator.models import MTSubjects_Staging


class SubjectStagingResource(resources.ModelResource):
    class Meta:
        model = MTSubjects_Staging

