from datetime import datetime, timedelta, date
from pytz import timezone

from django.test import TestCase

from client.forms import (
    SignupForm, OnlineCheckIn, SearchForFlightsForm, BuyTicketForm
)
from common_instances.models import (
    Ticket, Seat, Option, Passenger, Airplane,
    SeatType, Airport, Flight, Discount
)


class TestForms(TestCase):
    """Test forms validation."""

    def setUp(self):
        airports = [('Borispil', 'KBP'), ('Zhuliany', 'IEV')]
        self.airports = [
            Airport.objects.create(
                name=airport[0],
                city='Kyiv',
                country='Ukraine',
                IATA_code=airport[1]
            ) for airport in airports
        ]
        self.seat_type = SeatType.objects.create(
            seat_type='Economy',
            price_multiplier=1
        )
        self.option = Option.objects.create(
            name='Lunch',
            price=15
        )

    def test_signup_form(self):
        """Check sign up form validation."""
        form = SignupForm(data={
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
            'email': 'johndoe@gmail.com'
        })
        self.assertTrue(form.is_valid())

    def test_signup_invalid_form(self):
        """Check sign up form validation with different passwords."""
        form = SignupForm(data={
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'testpassword',
            'confirm_password': 'testpassword1',
            'email': 'johndoe@gmail.com'
        })
        self.assertFalse(form.is_valid())

    def test_online_check_in_form(self):
        """Check sign up form validation."""
        plane = Airplane.objects.create(
            number='testplane'
        )
        seat = Seat.objects.create(
            number='11',
            airplane=plane,
            seat_type=self.seat_type
        )
        passenger = Passenger.objects.create(
            first_name='John',
            last_name='Doe',
            passport_number='qw123456'
        )
        flight = Flight.objects.create(
            number='testflight',
            ticket_price=50,
            boarding_time=datetime.now(tz=timezone('EET')),
            departure_time=datetime.now(tz=timezone('EET')) + timedelta(hours=1),
            arrival_time=datetime.now(tz=timezone('EET')) + timedelta(hours=2),
            distance=200,
            airplane=plane,
            departure_airport=self.airports[0],
            destination_airport=self.airports[1]
        )
        ticket = Ticket.objects.create(
            ticket_code='testticket',
            seat=seat,
            passenger=passenger,
            flight=flight
        )
        ticket.options.set([self.option, ])
        form = OnlineCheckIn(data={
            'passenger': passenger.id,
            'seat': seat.id,
            'options': [self.option.id, ]
        }, instance=ticket)
        self.assertTrue(form.is_valid())

    def test_search_for_flight_form(self):
        """Check search for flight form validation."""
        form = SearchForFlightsForm(data={
            'arriving': self.airports[0],
            'destination': self.airports[1],
            'date': date.today(),
            'passengers': 2
        })
        self.assertTrue(form.is_valid())

    def test_search_for_flight_invalid_form(self):
        """Check search for flight form validation with same airports."""
        form = SearchForFlightsForm(data={
            'arriving': self.airports[0],
            'destination': self.airports[0],
            'date': date.today(),
            'passengers': 2
        })
        self.assertFalse(form.is_valid())

    def test_buy_ticket_form(self):
        """Check buy ticket form validation."""
        Discount.objects.create(
            name='test_discount',
            is_percentage=False,
            amount=10,
            promo_code='test_promo'
        )
        form = BuyTicketForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'passport_number': 'qw123456',
            'seat_class': self.seat_type.id,
            'options': [self.option.id, ],
            'promo_code': 'test_promo'
        })
        self.assertTrue(form.is_valid())

    def test_buy_ticket_invalid_form(self):
        """Check buy ticket form validation with wrong promo code."""
        form = BuyTicketForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'passport_number': 'qw123456',
            'seat_class': self.seat_type.id,
            'options': [self.option.id, ],
            'promo_code': 'wrong_promo'
        })
        self.assertFalse(form.is_valid())
