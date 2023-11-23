from datetime import datetime, timedelta
from pytz import timezone

from django.test import TestCase

from common_instances.models import Airport, Airplane, Option
from ..forms import (
    CreateFlight, CreatePilot, CreateManager, CreatePlane,
    CreateOption, CreateDiscount, CheckInForm
)
from ..models import Pilot


class TestForms(TestCase):
    """Test forms validation."""

    def test_create_flight_form(self):
        """Check create flight form validation."""
        pilots = [
            ('Tom', 'Cruise', 'tomcruise@gmail.com'),
            ('Tom', 'Hanks', 'tomhanks@gmail.com')
        ]
        pilots = [
            Pilot.objects.create(
                first_name=pilot[0],
                last_name=pilot[1],
                category='ATP',
                email=pilot[2]
            ) for pilot in pilots
        ]
        airports = [('Borispil', 'KBP'), ('Zhuliany', 'IEV')]
        airports = [
            Airport.objects.create(
                name=airport[0],
                city='Kyiv',
                country='Ukraine',
                IATA_code=airport[1]
            ) for airport in airports
        ]
        airplane = Airplane.objects.create(number='testplane')
        form = CreateFlight(data={
            'number': 'test1234',
            'ticket_price': 50,
            'boarding_time': datetime.now(tz=timezone('EET')),
            'departure_time': (datetime.now(tz=timezone('EET')) +
                               timedelta(hours=1)),
            'arrival_time': (datetime.now(tz=timezone('EET')) +
                             timedelta(hours=2)),
            'distance': 200,
            'airplane': airplane,
            'pilots': pilots,
            'departure_airport': airports[0],
            'destination_airport': airports[1]
        })
        self.assertTrue(form.is_valid())

    def test_create_pilot_form(self):
        """Check create pilot form validation."""
        form = CreatePilot(data={
            'first_name': 'Yuki',
            'last_name': 'Tsunoda',
            'category': 'AT',
            'email': 'tsunoda@gmail.com'
        })
        self.assertTrue(form.is_valid())

    def test_create_manager_form(self):
        """Check create manager form validation."""
        form = CreateManager(data={
            'first_name': 'Max',
            'last_name': 'Verstappen',
            'email': 'verstappen@gmail.com',
            'username': 'maxverstappen',
            'role': 'gate_manager'
        })
        self.assertTrue(form.is_valid())

    def test_create_plane_form(self):
        """Check create plane form validation."""
        form = CreatePlane(data={
            'number': 'test1234',
            'economy_seat_rows': 2,
            'economy_seats_in_row': 6,
            'business_seat_rows': 2,
            'business_seats_in_row': 4
        })
        self.assertTrue(form.is_valid())

    def test_create_option_form(self):
        """Check create option form validation."""
        form = CreateOption(data={
            'name': 'Luggage',
            'price': 19
        })
        self.assertTrue(form.is_valid())

    def test_create_discount_form(self):
        """Check create discount form validation."""
        form = CreateDiscount(data={
            'name': 'test',
            'is_percentage': True,
            'amount': 15,
            'promo_code': 'test1234'
        })
        self.assertTrue(form.is_valid())

    def test_check_in_form(self):
        """Check check-in form validation."""
        option = Option.objects.create(
            name='Luggage',
            price=19
        )
        form = CheckInForm(data={
            'options': [option]
        })
        self.assertTrue(form.is_valid())
