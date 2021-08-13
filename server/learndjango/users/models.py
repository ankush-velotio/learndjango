from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    # set username to None and change the default username field to the email
    username = None

    # For login, we have to use email because username is set to None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
