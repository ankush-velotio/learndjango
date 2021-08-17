from django.db import models
from django.utils.timezone import now
from model_utils import Choices
from ..common.mode_utils import TimestampedModel, CreatorInfoModel

from ..users.models import User


class Todo(TimestampedModel, CreatorInfoModel):
    COMPLETED = "completed"
    INPROGRESS = "inprogress"
    STATUS = Choices((COMPLETED, COMPLETED), (INPROGRESS, INPROGRESS))
    status = models.CharField(choices=STATUS, default=INPROGRESS, max_length=20)
    owner = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=now)
    is_bookmarked = models.BooleanField(default=False)
    editors = models.ManyToManyField(User)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title
