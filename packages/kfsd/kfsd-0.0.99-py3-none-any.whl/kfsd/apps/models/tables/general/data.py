from django.db import models

from kfsd.apps.models.constants import MAX_LENGTH
from kfsd.apps.models.tables.base import BaseModel


class Data(BaseModel):
    name = models.CharField(max_length=MAX_LENGTH)
    is_template = models.BooleanField(default=False)
    is_json = models.BooleanField(default=True)
    txt_body = models.TextField(blank=True, null=True)
    json_body = models.JSONField(default=dict)

    def save(self, *args, **kwargs):
        self.identifier = ",".join(
            [
                "{}={}".format("DATA", self.name),
            ]
        )
        return super().save(*args, **kwargs)

    class Meta:
        app_label = "models"
        verbose_name = "Data"
        verbose_name_plural = "Data"
