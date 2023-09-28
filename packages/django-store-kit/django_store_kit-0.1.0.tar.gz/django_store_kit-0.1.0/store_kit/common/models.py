from django.db import models


class BaseModel(models.Model):
    """
    Keep track of created time and modified time in models.
    """

    created_at = models.DateTimeField("created time", auto_now_add=True)
    updated_at = models.DateTimeField("modified time", auto_now=True)

    class Meta:
        abstract = True