from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from model_utils import Choices

from common.model_utils import TimestampedModel, AuditModel


class User(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    # set username to None and change the default username field to the email
    username = None

    # For login, we have to use email because username is set to None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Todo(TimestampedModel, AuditModel):
    COMPLETED = "completed"
    INPROGRESS = "inprogress"
    STATUS = Choices((COMPLETED, COMPLETED), (INPROGRESS, INPROGRESS))
    status = models.CharField(choices=STATUS, default=INPROGRESS, max_length=20)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=now)
    is_bookmarked = models.BooleanField(default=False)
    owner = models.ForeignKey(User, related_name='set_owner', on_delete=models.CASCADE)
    editors = models.ManyToManyField(User, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title
