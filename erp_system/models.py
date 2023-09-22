from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """User model. Standard User model supplemented with field role which
    will give permissions for users."""
    ROLES = [
        ('customer', 'Customer'),
        ('gate_manager', 'Gate manager'),
        ('check_in_manager', 'Check-in manager'),
        ('supervisor', 'Supervisor')
    ]
    role = models.CharField(choices=ROLES, default='customer',
                            max_length=30)

    def __str__(self):
        return self.username


class Airport(models.Model):
    """Airport model. Contains name of airport, location data and
    IATA code."""
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    IATA_code = models.CharField(max_length=4)

    def __str__(self):
        return self.name


class Pilot(models.Model):
    """Pilot model. Have a first name, last name, email and category."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class SeatType(models.Model):
    """Represents the seat type and the multiplier that determines how
    much more the ticket will cost."""
    seat_type = models.CharField(max_length=100)
    price_multiplier = models.FloatField()

    def __str__(self):
        return self.seat_type


class Airplane(models.Model):
    """Represents the plane that will be assigned to the flights"""
    number = models.CharField(max_length=100)

    def __str__(self):
        return self.number


class Seat(models.Model):
    """Represents a seat that belongs to a specific aircraft and will
    be reserved by passengers."""
    number = models.CharField(max_length=100)
    seat_type = models.ForeignKey(SeatType, on_delete=models.CASCADE,
                                  related_name='seats')
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE,
                                 related_name='seats')

    def __str__(self):
        return self.number


class Flight(models.Model):
    """Model that represents flights."""
    number = models.CharField(max_length=100)
    ticket_price = models.IntegerField()
    boarding_time = models.DateTimeField()
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    distance = models.IntegerField()
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE,
                                 related_name='flights')
    pilots = models.ManyToManyField(Pilot, related_name='flights')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='flights')
    departure_airport = models.ForeignKey(Airport,
                                          on_delete=models.CASCADE,
                                          related_name='departing_lights')
    destination_airport = models.ForeignKey(Airport,
                                            on_delete=models.CASCADE,
                                            related_name='arriving_flights')

    def __str__(self):
        return self.number


class Discount(models.Model):
    """Represents discount that can reduce the price of ticket."""
    name = models.CharField(max_length=100)
    is_percentage = models.BooleanField(default=False)
    amount = models.IntegerField()
    promo_code = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Option(models.Model):
    """Represents additional services during the flight."""
    name = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return self.name


class Passenger(models.Model):
    """Represents passenger who will fly at the flight."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Purchase(models.Model):
    """Performs the function of checking whether payment for
    tickets has been made"""
    is_paid = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='purchases')
    created = models.DateTimeField(auto_now_add=True)


class Ticket(models.Model):
    """Represents ticket that will allow people to check in and fly
    on particular flight."""
    ticket_code = models.CharField(max_length=100)
    checked_in = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE,
                                 blank=True, null=True)
    options = models.ManyToManyField(Option, blank=True)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE,
                                  related_name='tickets', blank=True,
                                  null=True)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE,
                                 related_name='tickets', blank=True,
                                 null=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE,
                               related_name='tickets')
