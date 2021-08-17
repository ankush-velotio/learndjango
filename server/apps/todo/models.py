from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.timezone import now
from model_utils import Choices
from timestampedmodel import TimestampedModel

from ..users.models import User


class Todo(TimestampedModel):
    COMPLETED = "completed"
    INPROGRESS = "inprogress"
    STATUS = Choices((COMPLETED, COMPLETED), (INPROGRESS, INPROGRESS))
    status = models.CharField(choices=STATUS, default=INPROGRESS, max_length=20)
    owner = models.CharField(max_length=100)
    created_by = models.CharField(max_length=100)
    updated_by = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=now)
    is_bookmarked = models.BooleanField(default=False)
    editors = models.ManyToManyField(User)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title
