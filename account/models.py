from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    name = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'