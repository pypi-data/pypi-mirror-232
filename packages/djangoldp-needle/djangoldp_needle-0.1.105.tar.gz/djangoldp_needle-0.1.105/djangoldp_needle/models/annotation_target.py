from django.db import models
from djangoldp.models import Model

from ..permissions import AnnotationTargetPermissions


class AnnotationTarget(Model):
    target = models.CharField(max_length=4096)
    image = models.CharField(max_length=4096, null=True)
    title = models.CharField(max_length=4096, null=True)
    publication_date = models.DateTimeField(null=True)
    annotation_target_date = models.DateTimeField(null=True)

    class Meta(Model.Meta):
        rdf_type = 'hd:annotation_target'
        anonymous_perms = []
        authenticated_perms = ['view', 'add']
        constraints = [
            models.UniqueConstraint(
                fields=["target"], name="unique_target_url"
            )
        ]
        permission_classes = [AnnotationTargetPermissions]

    def __str__(self):
        return self.target
