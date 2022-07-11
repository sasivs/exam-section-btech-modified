from import_export import resources
from hod.models import FacultyInfo


class FacultyInfoResource(resources.ModelResource):
    class Meta:
        model = FacultyInfo