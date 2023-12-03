from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User model for staff side. Standard User model supplemented
    with field role which will give permissions for users."""
    ROLES = [
        ('customer', 'Customer'),
        ('gate_manager', 'Gate manager'),
        ('check_in_manager', 'Check-in manager'),
        ('supervisor', 'Supervisor')
    ]
    role = models.CharField(choices=ROLES, default='customer',
                            max_length=30)
    email_is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Pilot(models.Model):  # staff
    """Pilot model. Have a first name, last name, email and category."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    email = models.EmailField()
    flights = models.ManyToManyField('common_instances.Flight',
                                     related_name='pilots')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
