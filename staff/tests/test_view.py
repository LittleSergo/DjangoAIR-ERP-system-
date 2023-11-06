import re
from datetime import datetime, timedelta

from django.core import mail
from pytz import timezone

from django.db import transaction
from django.test import TestCase
from django.urls import reverse

from common_instances.models import Flight, Airport, Airplane, SeatType, Option, Discount, Ticket, Seat
from staff.models import User, Pilot


class TestViews(TestCase):
    """Test case for views."""

    def setUp(self):
        with transaction.atomic():
            airports = [('Borispil', 'KBP'), ('Zhuliany', 'IEV')]
            self.airports = [
                Airport.objects.create(
                    name=airport[0],
                    city='Kyiv',
                    country='Ukraine',
                    IATA_code=airport[1]
                ) for airport in airports
            ]
            seat_types = [('Economy', 1.0), ('Business', 2.5)]
            self.seat_types = [
                SeatType.objects.create(
                    seat_type=seat_type[0],
                    price_multiplier=seat_type[1]
                ) for seat_type in seat_types
            ]
            self.airplane = Airplane.objects.create(number='testplane')
            self.flight = Flight.objects.create(
                number='testflight',
                ticket_price=30,
                boarding_time=datetime.now(
                    tz=timezone('EET')) + timedelta(hours=1),
                departure_time=datetime.now(
                    tz=timezone('EET')) + timedelta(hours=2),
                arrival_time=datetime.now(
                    tz=timezone('EET')) + timedelta(hours=3),
                distance=80,
                airplane=self.airplane,
                departure_airport=self.airports[0],
                destination_airport=self.airports[1],
            )
            self.user = User.objects.create_user(
                username='testuser',
                password='testuser'
            )
            self.supervisor = User.objects.create_user(
                username='supervisor',
                password='supervisor',
                role='supervisor',
                email='supervisor@gmail.com'
            )
            self.seat = Seat.objects.create(
                number='A1',
                seat_type=self.seat_types[0],
                airplane=self.airplane
            )
            self.ticket = Ticket.objects.create(
                ticket_code='test1234',
                flight=self.flight,
                seat=self.seat
            )

    def test_get_page_logged_out(self):
        """Get page where login is required and check redirect."""
        response = self.client.get(reverse('staff:staff_flights'))
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse('staff:log_in') + '?next=/staff/flights/'
        )

    def test_staff_flights_view(self):
        """Get staff flights page and check data."""
        self.client.login(username='testuser', password='testuser')
        response = self.client.get(reverse('staff:staff_flights'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/staff_flights.html')
        self.assertContains(response, 'testflight')

    def test_create_flight_view_GET(self):
        """Get create flight view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:create_flight'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/create_flight.html')
        self.assertContains(response, 'Create flight')

    def test_create_flight_view_POST(self):
        """Post to create flight view and check data."""
        pilot = Pilot.objects.create(
            first_name='Tom',
            last_name='Cruise',
            category='ATP',
            email='tomcruise@gmail.com'
        )
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.post(reverse('staff:create_flight'), data={
            'number': 'test1234',
            'ticket_price': 30,
            'boarding_time': datetime(2023, 2, 15, 14, 30),
            'departure_time': datetime(2023, 2, 15, 15, 30),
            'arrival_time': datetime(2023, 2, 15, 16, 30),
            'distance': 80,
            'airplane': self.airplane.id,
            'departure_airport': self.airports[0].id,
            'destination_airport': self.airports[1].id,
            'pilots': [pilot.id, ]
        })
        flight = Flight.objects.get(number='test1234')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(flight.distance, 80)
        self.assertRedirects(response, reverse('staff:staff_flights'))
        self.assertEquals(len(mail.outbox), 1)

    def test_staff_airplanes_view(self):
        """Get staff airplanes view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:staff_planes'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/staff_airplanes.html')
        self.assertContains(response, 'Airplanes')

    def test_create_airplane_view_GET(self):
        """Get create airplane view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:create_airplane'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/create_airplane.html')
        self.assertContains(response, 'Create airplane')

    def test_create_airplane_view_POST(self):
        """Post to create airplane view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.post(reverse('staff:create_airplane'),
                                    data={
                                        'number': 'TEST1234',
                                        'economy_seat_rows': 4,
                                        'economy_seats_in_row': 6,
                                        'business_seat_rows': 2,
                                        'business_seats_in_row': 4
                                    })
        plane = Airplane.objects.get(number='TEST1234')
        seat = plane.seats.filter(number='A1')
        self.assertEquals(response.status_code, 302)
        self.assertTrue(plane)
        self.assertTrue(seat)
        self.assertRedirects(response, reverse('staff:staff_planes'))

    def test_staff_pilots_view(self):
        """Get staff pilots view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:staff_pilots'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/staff_pilots.html')
        self.assertContains(response, 'Pilots')

    def test_create_pilot_view_GET(self):
        """Get create pilot view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:create_pilot'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/create_pilot.html')
        self.assertContains(response, 'Create pilot')

    def test_create_pilot_view_POST(self):
        """Post to create pilot view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.post(reverse('staff:create_pilot'), {
            'first_name': 'Tom',
            'last_name': 'Cruise',
            'category': 'ATP',
            'email': 'tomcruise@gmail.com'
        })
        pilot = Pilot.objects.get(last_name='Cruise')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(pilot.first_name, 'Tom')
        self.assertRedirects(response, reverse('staff:staff_pilots'))

    def test_staff_managers_view(self):
        """Get staff managers view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:staff_pilots'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/staff_pilots.html')
        self.assertContains(response, 'Managers')

    def test_create_manager_view_GET(self):
        """Get create manager view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:create_manager'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/create_manager.html')
        self.assertContains(response, 'Create manager')

    def test_create_manager_view_POST(self):
        """Post to create manager view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.post(reverse('staff:create_manager'), {
            'first_name': 'Ron',
            'last_name': 'Weasley',
            'username': 'weasleyron',
            'email': 'weasleyron@gmail.com',
            'role': 'gate_manager'
        })
        manager = User.objects.get(last_name='Weasley')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(manager.first_name, 'Ron')
        self.assertRedirects(response, reverse('staff:staff_managers'))
        self.assertEquals(len(mail.outbox), 1)

    def test_staff_options_view(self):
        """Get staff options view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:staff_options'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/staff_options.html')
        self.assertContains(response, 'Options')

    def test_create_option_view_GET(self):
        """Get create option view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:create_option'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/create_option.html')
        self.assertContains(response, 'Create option')

    def test_create_option_view_POST(self):
        """Post to create option view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.post(reverse('staff:create_option'), {
            'name': 'Luggage',
            'price': 19,
        })
        option = Option.objects.get(name='Luggage')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(option.price, 19)
        self.assertRedirects(response, reverse('staff:staff_options'))

    def test_staff_discounts_view(self):
        """Get staff discounts view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:staff_discounts'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/staff_discounts.html')
        self.assertContains(response, 'Discounts')

    def test_create_discount_view_GET(self):
        """Get create discount view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:create_discount'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/create_discount.html')
        self.assertContains(response, 'Create discount')

    def test_create_discount_view_POST(self):
        """Post to create discount view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.post(reverse('staff:create_discount'), {
            'name': 'test_discount',
            'is_percentage': True,
            'amount': 15,
            'promo_code': 'Test_promo',
        })
        discount = Discount.objects.get(name='test_discount')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(discount.amount, 15)
        self.assertRedirects(response, reverse('staff:staff_discounts'))

    def test_check_in_manager_menu_view_GET(self):
        """Get check in manager menu view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:check_in_menu'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/check_in_menu.html')
        self.assertContains(response, 'Check-in menu')

    def test_check_in_manager_menu_view_POST(self):
        """Post to check in manager menu view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.post(reverse('staff:check_in_menu'), {
            'ticket_code': 'test1234',
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('staff:ticket_check_in',
                                               args=[self.ticket.id]))

    def test_ticket_check_in_view_GET(self):
        """Get ticket check in view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:ticket_check_in',
                                           args=[self.ticket.id]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/ticket_check-in.html')
        self.assertContains(response, 'Check-in')

    def test_ticket_check_in_view_POST(self):
        """Post to ticket check in view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        option = Option.objects.create(
            name='Luggage',
            price=19
        )
        response = self.client.post(reverse('staff:ticket_check_in',
                                            args=[self.ticket.id]), {
                                        'options': [option.id, ]
                                    })
        self.ticket.refresh_from_db()
        self.assertEquals(response.status_code, 302)
        self.assertTrue(self.ticket.checked_in)
        self.assertTrue(option in self.ticket.options.all())
        self.assertRedirects(response, reverse('staff:check_in_menu'))

    def test_boarding_menu_view_GET(self):
        """Get boarding menu view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:boarding_menu'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/boarding_menu.html')
        self.assertContains(response, 'Boarding menu')

    def test_boarding_menu_view_POST(self):
        """Post to boarding menu view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.post(reverse('staff:boarding_menu'), {
            'ticket_code': 'test1234',
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('staff:passenger_boarding',
                                               args=[self.ticket.id]))

    def test_boarding_passenger_view_GET(self):
        """Get boarding passenger view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:passenger_boarding',
                                           args=[self.ticket.id]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/boarding_passenger.html')
        self.assertContains(response, 'Boarding')

    def test_boarding_passenger_view_POST(self):
        """Post to boarding passenger view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.post(reverse('staff:passenger_boarding',
                                            args=[self.ticket.id]))
        self.ticket.refresh_from_db()
        self.assertEquals(response.status_code, 302)
        self.assertTrue(self.ticket.is_on_board)
        self.assertRedirects(response, reverse('staff:boarding_menu'))

    def test_login_user_view_GET(self):
        """Get login user view and check data."""
        response = self.client.get(reverse('staff:log_in'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/login.html')
        self.assertContains(response, 'Login')

    def test_login_user_view_POST(self):
        """Login user via post to login user page."""
        response = self.client.post(reverse('staff:log_in'), data={
            'username': 'supervisor',
            'password': 'supervisor'
        })
        self.assertEqual(int(self.client.session.get('_auth_user_id',
                                                     None)),
                         self.supervisor.id)
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('staff:staff_flights'))

    def test_logout_user_view(self):
        """Post to log out view and check log out"""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.post(reverse('staff:log_out'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('staff:log_in'))

    def test_profile_view_GET(self):
        """Get profile view and check data."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.get(reverse('staff:profile',
                                           args=[self.supervisor.id]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/profile.html')
        self.assertContains(response, self.supervisor.username)

    def test_profile_view_POST(self):
        """Try to request change users password via post to profile
        view."""
        self.client.login(username='supervisor', password='supervisor')
        response = self.client.post(reverse(
            'staff:profile', args=[self.supervisor.id]), data={
            'password': 'supervisor'
        })
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'staff/profile.html')
        self.assertContains(response, 'Email with instructions was '
                                      'sent on your email.')
        self.assertEquals(len(mail.outbox), 1)

    def test_change_password_view_GET(self):
        """Get link for changing password from email and get changing
        password page through that link, and check data."""
        self.client.login(username='supervisor', password='supervisor')
        self.client.post(reverse(
            'staff:profile', args=[self.supervisor.id]), data={
            'password': 'supervisor'
        })
        activate_link = re.search("(?P<url>https?://[^\s]+)",
                                  mail.outbox[0].body).group('url')
        response = self.client.get(activate_link)
        self.assertContains(response, 'Reset password')
        self.assertEquals(response.status_code, 200)

    def test_change_password_view_POST(self):
        """Change password sending new password to
        change password page."""
        self.client.login(username='supervisor', password='supervisor')
        self.client.post(reverse(
            'staff:profile', args=[self.supervisor.id]), data={
            'password': 'supervisor'
        })
        activate_link = re.search("(?P<url>https?://[^\s]+)",
                                  mail.outbox[0].body).group('url')
        response = self.client.post(activate_link, data={
            'password': 'newsupervisor',
            'confirm_password': 'newsupervisor'
        })
        self.supervisor.refresh_from_db()
        self.assertTrue(self.supervisor.check_password('newsupervisor'))
        self.assertEquals(response.status_code, 302)
