from django.db import models
from django.conf import settings

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ("AD", "Admin"),
        ("IN", "Instructor"),
        ("ST", "Student"),
        ("SP", "Sponsor")
    ]

    role = models.CharField(max_length=2, choices=ROLE_CHOICES, default="ST")
    