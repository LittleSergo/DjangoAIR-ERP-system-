from django.db import models
from decimal import Decimal


class Airport(models.Model):
    """Airport model. Contains name of airport, location data and
    IATA code."""
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    IATA_code = models.CharField(max_length=4)

    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"


class Airplane(models.Model):
    """Represents the plane that will be assigned to the flights"""
    number = models.CharField(max_length=100)

    def __str__(self):
        return self.number


class SeatType(models.Model):
    """Represents the seat type and the multiplier that determines how
    much more the ticket will cost."""
    seat_type = models.CharField(max_length=100)
    price_multiplier = models.FloatField()

    def __str__(self):
        return self.seat_type


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
    pilots_reminder_is_sent = models.BooleanField(default=False)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE,
                                 related_name='flights')
    departure_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name='departing_lights'
    )
    destination_airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name='arriving_flights'
    )

    def __str__(self):
        return self.number

    def available_business_tickets(self):
        """Return how much business class tickets is available."""
        return self.tickets.filter(is_available=True,
                                   seat__seat_type=2).count()

    def available_economy_tickets(self):
        """Return how much economy class tickets is available."""
        return self.tickets.filter(is_available=True,
                                   seat__seat_type=1).count()

    def business_class_ticket_price(self):
        """Return a price of business class ticket."""
        multiplier = SeatType.objects.get(
            seat_type='Business').price_multiplier
        return round(self.ticket_price * multiplier, 2)


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


class Ticket(models.Model):
    """Represents ticket that will allow people to check in and fly
    on particular flight."""
    ticket_code = models.CharField(max_length=100)
    checked_in = models.BooleanField(default=False)
    is_on_board = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount, on_delete=models.CASCADE,
                                 blank=True, null=True)
    options = models.ManyToManyField(Option, blank=True)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE,
                                  related_name='tickets', blank=True,
                                  null=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE,
                               related_name='tickets')

    def price(self):
        """Return price of the ticket depends on seat type."""
        return Decimal(
            self.flight.ticket_price * self.seat.seat_type.
            price_multiplier
        )

    def full_price(self):
        """Return full price considering the seat type and the options"""
        price = self.price()
        for option in self.options.all():
            price += option.price
        if self.discount:
            if self.discount.is_percentage:
                return round(
                    price - (price / 100 * self.discount.amount), 2
                )
            price -= self.discount.amount
        return round(price, 2)
