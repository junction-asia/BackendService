from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    first_name = None
    last_name = None
    username = None
    login_id = models.CharField(max_length=20, unique=True)

    USERNAME_FIELD = 'login_id'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.id} {self.login_id}"
