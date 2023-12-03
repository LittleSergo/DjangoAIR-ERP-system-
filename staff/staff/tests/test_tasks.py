from datetime import datetime, timedelta
from unittest.mock import patch

from pytz import timezone

from django.core import mail
from django.test import TestCase

from common_instances.models import Flight, Airport, Airplane
from staff.models import User, Pilot
from staff.tasks import (
    send_manager_assigning_letter, send_pilot_assigning_letter,
    send_password_reset_email, send_flight_reminder_to_pilot,
    flight_pilot_reminder
)


class TestTasks(TestCase):
    """Tests for tasks."""

    def setUp(self):
        self.user = dict(username='testuser', password='testpassword',
                         email='test@gmail.com', email_is_verified=True)
        self.airports = [('Borispil', 'KBP'), ('Zhuliany', 'IEV')]
        self.plane = dict(number='testplane')
        self.pilot = dict(
            first_name='Tom', last_name='Cruise',
            category='ATP', email='tomcruise@gmail.com'
        )
        self.flight = dict(
            number='testflight',
            ticket_price=50,
            boarding_time=datetime.now(tz=timezone('EET')),
            departure_time=datetime.now(
                tz=timezone('EET')) + timedelta(hours=2),
            arrival_time=datetime.now(tz=timezone('EET')),
            distance=200,
        )
        self.fill_db()

    def fill_db(self):
        self.user = User.objects.create_user(**self.user)
        airports = [
            Airport.objects.create(
                name=airport[0],
                city='Kyiv',
                country='Ukraine',
                IATA_code=airport[1]
            ) for airport in self.airports
        ]
        plane = Airplane.objects.create(**self.plane)
        self.pilot = Pilot.objects.create(**self.pilot)
        self.flight = Flight.objects.create(
            airplane=plane,
            departure_airport=airports[0],
            destination_airport=airports[1],
            **self.flight
        )
        self.flight.pilots.add(self.pilot)
        self.flight.save()

    def test_send_manager_assigning_letter_task(self):
        """Check whether function send_manager_assigning_letter
        sending assigning letter."""
        send_manager_assigning_letter(self.user.id, 'test_password')
        self.assertEquals(len(mail.outbox), 1)

    def test_send_pilot_assigning_letter_task(self):
        """Check whether function send_pilot_assigning_letter
        sending assigning letter."""
        send_pilot_assigning_letter(self.flight.id)
        self.assertEquals(len(mail.outbox), 1)

    def test_send_password_reset_email_task(self):
        """Test send_password_reset_email task. Check whether
         it sends the letter."""
        send_password_reset_email('test_domain', False, self.user.id)
        self.assertEquals(len(mail.outbox), 1)

    def test_send_flight_reminder_to_pilot_task(self):
        """Test send_flight_reminder_to_pilot task. Check whether
         it sends the letter."""
        send_flight_reminder_to_pilot(self.pilot.id, self.flight.id)
        self.assertEquals(len(mail.outbox), 1)

    @patch('staff.tasks.send_flight_reminder_to_pilot.delay',
           send_flight_reminder_to_pilot)
    def test_flight_pilot_reminder_task(self):
        """Check whether it finds the closest flight and send a
        reminder."""
        flight_pilot_reminder()
        self.flight.refresh_from_db()
        self.assertTrue(self.flight.pilots_reminder_is_sent)
        self.assertEquals(len(mail.outbox), 1)

    def test_filter_flight_pilot_reminder_task(self):
        """Check whether it skips the flight if it is not a time to
        send reminder."""
        self.flight.departure_time = (datetime.now(tz=timezone('EET')) +
                                      timedelta(hours=6, minutes=30))
        self.flight.save()
        flight_pilot_reminder()
        self.flight.refresh_from_db()
        self.assertFalse(self.flight.pilots_reminder_is_sent)
        self.assertEquals(len(mail.outbox), 0)
