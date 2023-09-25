from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    password = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    fio = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['username', 'fio']
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email