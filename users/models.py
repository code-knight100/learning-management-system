from django.db import models
from django.contrib.auth.models import AbstractUser



# Create your models here.

# custom user model: 
class User(AbstractUser):
    ROLE_CHOICES = [
        ("AD", "Admin"),
        ("IN", "Instructor"),
        ("ST", "Student"),
        ("SP", "Sponsor")
    ]

    role = models.CharField(max_length=2, choices=ROLE_CHOICES, default="ST")
    
    def __str__(self):
        return f"{self.username} - ({self.role})"
    