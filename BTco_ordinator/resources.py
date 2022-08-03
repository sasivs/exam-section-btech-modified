from import_export import resources
from BTco_ordinator.models import BTSubjects_Staging, BTNotPromoted



class SubjectStagingResource(resources.ModelResource):
    class Meta:
        model = BTSubjects_Staging

class NotPromotedResource(resources.ModelResource):
    class Meta:
        model = BTNotPromoted