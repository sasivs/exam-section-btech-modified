from import_export import resources
from BTco_ordinator.models import BTSubjects_Staging, BTNotPromoted
from BTsuperintendent.models import BTCourseStructure



class SubjectStagingResource(resources.ModelResource):
    class Meta:
        model = BTSubjects_Staging

class NotPromotedResource(resources.ModelResource):
    class Meta:
        model = BTNotPromoted

class CourseStructureResource(resources.ModelResource):
    class Meta:
        model = BTCourseStructure