from import_export import resources
from co_ordinator.models import Subjects_Staging, NotPromoted



class SubjectStagingResource(resources.ModelResource):
    class Meta:
        model = Subjects_Staging

class NotPromotedResource(resources.ModelResource):
    class Meta:
        model = NotPromoted