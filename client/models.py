from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """User model for client side."""
    ROLES = [
        ('customer', 'Customer')
    ]
    role = models.CharField(choices=ROLES, default='customer',
                            max_length=30)
    email_is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Purchase(models.Model):
    """Performs the function of checking whether payment for
    tickets has been made"""
    is_paid = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='purchases')
    created = models.DateTimeField(auto_now_add=True)
    tickets = models.ManyToManyField('common_instances.Ticket')

    def total_bill(self):
        """Return the price for all tickets."""
        return sum([ticket.full_price() for ticket in self.tickets.all()])
