from datetime import datetime, timedelta
from pytz import timezone

from django.core import mail
from django.test import TestCase
from unittest.mock import patch

from common_instances.models import (
    Airplane, Airport, Flight, Discount, SeatType, Seat, Ticket
)
from client.models import Purchase, User
from client.tasks import (
    send_email_with_receipt_and_ticket, send_password_reset_email,
    send_flight_reminder, flight_client_reminder, check_purchase_is_paid
)


class TestTasks(TestCase):
    """Tests for tasks."""

    def setUp(self):
        self.user = dict(username='testuser', password='testpassword',
                         email='test@gmail.com', email_is_verified=True)
        self.plane = dict(number='testplane')
        self.airports = [('Borispil', 'KBP'), ('Zhuliany', 'IEV')]
        self.flight = dict(
            number='testflight',
            ticket_price=50,
            boarding_time=datetime.now(tz=timezone('EET')),
            departure_time=datetime.now(
                tz=timezone('EET')) + timedelta(hours=2),
            arrival_time=datetime.now(tz=timezone('EET')),
            distance=200,
        )
        self.discount = dict(
            name='test_discount', amount=10, promo_code='test_promo'
        )
        self.seat_type = dict(seat_type='Economy', price_multiplier=1)
        self.seat = dict(number='11')
        self.ticket = dict(ticket_code='testticket')
        self.fill_db()

    def fill_db(self):
        self.user = User.objects.create_user(**self.user)
        self.purchase = Purchase.objects.create(user=self.user)
        plane = Airplane.objects.create(
            number='testplane'
        )
        airports = [
            Airport.objects.create(
                name=airport[0],
                city='Kyiv',
                country='Ukraine',
                IATA_code=airport[1]
            ) for airport in self.airports
        ]
        self.flight = Flight.objects.create(
            airplane=plane,
            departure_airport=airports[0],
            destination_airport=airports[1],
            **self.flight
        )
        Discount.objects.create(**self.discount)
        seat_type = SeatType.objects.create(**self.seat_type)
        seat = Seat.objects.create(airplane=plane, seat_type=seat_type,
                                   **self.seat)
        ticket = Ticket.objects.create(seat=seat, flight=self.flight,
                                       **self.ticket)
        self.purchase.tickets.add(ticket)
        self.purchase.save()

    def test_send_email_with_receipt_and_ticket_task(self):
        """Test send_email_with_receipt_and_ticket task. Check whether
         it sends the letter."""
        send_email_with_receipt_and_ticket(self.purchase.id)
        self.purchase.refresh_from_db()
        self.assertTrue(self.purchase.is_paid)
        self.assertEquals(len(mail.outbox), 1)

    def test_send_password_reset_email_task(self):
        """Test send_password_reset_email task. Check whether
         it sends the letter."""
        send_password_reset_email('test_domain', False, self.user.id)
        self.assertEquals(len(mail.outbox), 1)

    def test_send_flight_reminder_task(self):
        """Test send_flight_reminder task. Check whether
         it sends the letter."""
        send_flight_reminder(self.purchase.id)
        self.purchase.refresh_from_db()
        self.assertTrue(self.purchase.reminder_is_sent)
        self.assertEquals(len(mail.outbox), 1)

    @patch('client.tasks.send_flight_reminder.delay',
           send_flight_reminder)
    def test_flight_client_reminder_task(self):
        """Check whether it finds the closest flight and send a
        reminder."""
        flight_client_reminder()
        self.purchase.refresh_from_db()
        self.assertTrue(self.purchase.reminder_is_sent)
        self.assertEquals(len(mail.outbox), 1)

    def test_filter_flight_client_reminder_task(self):
        """Check whether it skips the flight if it is not a time to
        send reminder."""
        self.flight.departure_time = (datetime.now(tz=timezone('EET')) +
                                      timedelta(hours=6, minutes=30))
        self.flight.save()
        flight_client_reminder()
        self.purchase.refresh_from_db()
        self.assertFalse(self.purchase.reminder_is_sent)
        self.assertEquals(len(mail.outbox), 0)

    def test_check_purchase_is_paid_no_deletes_task(self):
        """Check whether it skips non paid purchase if it is not a time to
        delete one."""
        check_purchase_is_paid()
        purchase = Purchase.objects.all()
        self.assertTrue(purchase.exists())

    def test_check_purchase_is_paid_deletes_task(self):
        """Check whether it delete non paid purchase if it is a time to
        delete one."""
        self.purchase.created = (
                datetime.now(tz=timezone('EET')) -
                timedelta(minutes=16)
        )
        self.purchase.save()
        check_purchase_is_paid()
        purchase = Purchase.objects.all()
        self.assertFalse(purchase.exists())
