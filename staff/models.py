from django.db import models


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
