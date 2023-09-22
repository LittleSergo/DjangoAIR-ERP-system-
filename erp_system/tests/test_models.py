import random
from datetime import datetime, timedelta

from django.test import TestCase

from ..models import (
    User, Flight, Pilot, Airport, Purchase, Passenger, Ticket, Seat,
    Airplane, Option, Discount, SeatType
)


class ModelsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')

        airports = [('Borispil', 'KBP'), ('Zhuliany', 'IEV')]
        self.airports = [
            Airport.objects.create(
                name=airport[0],
                city='Kyiv',
                country='Ukraine',
                IATA_code=airport[1]
            ) for airport in airports
        ]

        pilots = [
            ('Tom', 'Cruise', 'tomcruise@gmail.com'),
            ('Tom', 'Hanks', 'tomhanks@gmail.com')
        ]
        self.pilots = [
            Pilot.objects.create(
                first_name=pilot[0],
                last_name=pilot[1],
                category='ATP',
                email=pilot[2]
            ) for pilot in pilots
        ]

        seat_types = [('Economy', 1.0), ('Business', 2.5)]
        self.seat_types = [
            SeatType.objects.create(
                seat_type=seat_type[0],
                price_multiplier=seat_type[1]
            ) for seat_type in seat_types
        ]

        self.airplane = Airplane.objects.create(number='testplane')

        for seat_number in range(1, 11):
            Seat.objects.create(
                number=str(seat_number),
                seat_type=random.choice(self.seat_types),
                airplane=self.airplane
            )

        self.flight = Flight.objects.create(
            number='testflight',
            ticket_price=30,
            boarding_time=datetime.now() + timedelta(hours=1),
            departure_time=datetime.now() + timedelta(hours=2),
            arrival_time=datetime.now() + timedelta(hours=3),
            distance=80,
            airplane=self.airplane,
            created_by=self.user,
            departure_airport=self.airports[0],
            destination_airport=self.airports[1],
        )
        self.flight.pilots.set(self.pilots)
        self.flight.save()

    def test_user_model(self):
        """Get created User object and check data."""
        user = User.objects.get(username='testuser')
        self.assertEquals(user.role, 'customer')

    def test_airport_model(self):
        """Get created airport object and check."""
        airport = Airport.objects.get(name='Borispil')
        self.assertEquals(airport.IATA_code, 'KBP')

    def test_pilot_model(self):
        """Get created pilot object and check."""
        pilot = Pilot.objects.get(last_name='Hanks')
        self.assertEquals(pilot.email, 'tomhanks@gmail.com')

    def test_seat_type_model(self):
        """Get created seat type object and check."""
        seat_type = SeatType.objects.get(seat_type='Economy')
        self.assertEquals(seat_type.price_multiplier, 1.0)

    def test_airplane_model(self):
        """Get created airplane model and check."""
        plane = Airplane.objects.filter(number='testplane')
        self.assertTrue(plane.exists())

    def test_seat_model(self):
        """Get created seat model and check."""
        seat = Seat.objects.filter(number='1')
        self.assertTrue(seat.exists())

    def test_flight_model(self):
        """Get created flight model and check."""
        flight = Flight.objects.get(number='testflight')
        self.assertEquals(flight.ticket_price, 30)

    def test_discount_model(self):
        """Create and get discount object and check."""
        Discount.objects.create(
            name='testdiscount',
            is_percentage=True,
            amount=15,
            promo_code='testpromo'
        )

        discount = Discount.objects.get(name='testdiscount')
        self.assertTrue(discount.is_percentage)

    def test_option_model(self):
        """Create and get option object and check."""
        Option.objects.create(
            name='Lunch',
            price=15
        )

        option = Option.objects.get(name='Lunch')
        self.assertEquals(option.price, 15)

    def test_passenger_model(self):
        """Create and get passenger object and check."""
        Passenger.objects.create(
            first_name='Jim',
            last_name='Carrey',
            passport_number='testnumber'
        )

        passenger = Passenger.objects.get(passport_number='testnumber')
        self.assertEquals(passenger.first_name, 'Jim')

    def test_purchase_model(self):
        """Create and get purchase object and check."""
        Purchase.objects.create(user=self.user)

        purchase = Purchase.objects.get(user=self.user)
        self.assertFalse(purchase.is_paid)

    def test_ticket_model(self):
        """Create and get ticket object and check."""
        for seat in self.flight.airplane.seats.all():
            Ticket.objects.create(
                ticket_code=f"ticket{seat.airplane}-{seat.number}",
                seat=seat,
                flight=self.flight
            )

        ticket = Ticket.objects.get(ticket_code='tickettestplane-4')
        self.assertTrue(ticket.is_available)
