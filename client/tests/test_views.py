import re
from datetime import datetime
from pytz import timezone

from unittest.mock import patch

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

from client.models import User, Purchase
from client.tasks import (
    send_password_reset_email, send_email_with_receipt_and_ticket
)
from common_instances.models import (
    Airplane, Seat, SeatType, Airport, Flight, Ticket, Discount
)


class TestSignUpView(TestCase):
    """Test sign up view."""

    def test_get(self):
        """Test get method to a signup view."""
        response = self.client.get(reverse('client:signup'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/signup.html')
        self.assertContains(response, 'SignUp')

    def test_post(self):
        """Test post method. Try to create a user."""
        site = Site.objects.get(
            domain='example.com',
        )
        site.domain = '127.0.0.1:8000'
        site.name = '127.0.0.1:8000'
        site.save()
        social_app = SocialApp.objects.create(
            provider='google',
            name='test',
            client_id='test_id',
            secret='test_key'
        )
        social_app.sites.add(site)
        social_app.save()
        response = self.client.post(reverse('client:signup'), data={
            'username': 'testuser',
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'password': 'test_password',
            'confirm_password': 'test_password',
            'email': 'jacksparrow@gmail.com'
        })
        user = User.objects.get(username='testuser')
        self.assertEquals(user.first_name, 'Jack')
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('client:login'))

    def test_post_wrong_data(self):
        """Test post method with wrong data."""
        response = self.client.post(reverse('client:signup'), data={
            'username': 'testuser',
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'password': 'test_password',
            'confirm_password': 'test_password12',
            'email': 'jacksparrow@gmail.com'
        })
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/signup.html')
        self.assertContains(response, 'SignUp')


class TestLoginLogoutViews(TestCase):
    """Test login view."""

    def setUp(self):
        site = Site.objects.get(
            domain='example.com',
        )
        site.domain = '127.0.0.1:8000'
        site.name = '127.0.0.1:8000'
        site.save()
        social_app = SocialApp.objects.create(
            provider='google',
            name='test',
            client_id='test_id',
            secret='test_key'
        )
        social_app.sites.add(site)
        social_app.save()
        User.objects.create_user(username='testuser',
                                 password='testpassword')

    def test_get_login_view(self):
        """Test get method to a login view."""
        response = self.client.get(reverse('client:login'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/login.html')
        self.assertContains(response, 'Login')

    def test_post_login_view(self):
        """Try to post data and login."""
        response = self.client.post(reverse('client:login'), data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('client:home'))

    def test_post_wrong_data_to_login_view(self):
        """Try to post wrong data to login view."""
        response = self.client.post(reverse('client:login'), data={
            'username': 'testuser2',
            'password': 'testpassword2'
        })
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/login.html')
        self.assertContains(response,
                            'Username and password did not match.')

    def test_post_to_logout_view(self):
        """Check post method on logout view, and try to log out."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('client:logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('client:login'))


class TestUserProfileView(TestCase):
    """Test user profile view."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword',
                                             email='test@gmail.com')
        self.client.login(username='testuser', password='testpassword')

    def test_get_user_profile_view(self):
        """Try to get user profile view."""
        response = self.client.get(reverse('client:profile'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/profile.html')
        self.assertContains(response, self.user.username)

    @patch('client.tasks.send_password_reset_email.delay',
           send_password_reset_email)
    def test_post_to_user_profile_view(self):
        """Post password to profile view and try to send change
        password request."""
        response = self.client.post(reverse('client:profile'), data={
            'password': 'testpassword'
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('client:profile'))
        self.assertEquals(len(mail.outbox), 1)


class TestChangePasswordView(TestCase):
    """Test change password view."""

    @patch('client.tasks.send_password_reset_email.delay',
           send_password_reset_email)
    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword',
                                             email='test@gmail.com')
        self.client.login(username='testuser', password='testpassword')
        self.client.post(reverse('client:profile'), data={
            'password': 'testpassword'
        })
        self.change_password_link = re.search(
            "(?P<url>https?://[^\s]+)",
            mail.outbox[0].body
        ).group('url')

    def test_get_change_password_view(self):
        """Try to get change password view."""
        response = self.client.get(self.change_password_link)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/reset_password.html')
        self.assertContains(response, 'Reset password')

    def test_post_to_change_password_view(self):
        """Post password to change password view and try to change
        password."""
        response = self.client.post(self.change_password_link, data={
            'password': 'new_password',
            'confirm_password': 'new_password'
        })
        self.user.refresh_from_db()
        self.assertEquals(response.status_code, 302)
        self.assertTrue(self.user.check_password('new_password'))

    def test_post_wrong_data_to_change_password_view(self):
        """Try to post wrong data to change password view."""
        response = self.client.post(self.change_password_link, data={
            'password': 'new_password',
            'confirm_password': 'new_new_password'
        })
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/reset_password.html')
        self.assertContains(response, 'Reset password')


class TestOnlineCheckIn(TestCase):
    """Test online check-in view."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword',
                                             email='test@gmail.com')
        self.client.login(username='testuser', password='testpassword')
        plane = Airplane.objects.create(
            number='testplane'
        )
        seat_type = SeatType.objects.create(
            seat_type='Economy',
            price_multiplier=1
        )
        seat = Seat.objects.create(
            number='11',
            airplane=plane,
            seat_type=seat_type
        )
        airports = [('Borispil', 'KBP'), ('Zhuliany', 'IEV')]
        airports = [
            Airport.objects.create(
                name=airport[0],
                city='Kyiv',
                country='Ukraine',
                IATA_code=airport[1]
            ) for airport in airports
        ]
        flight = Flight.objects.create(
            number='testflight',
            ticket_price=50,
            boarding_time=datetime(
                2024, 2, 2, 11, tzinfo=timezone('EET')
            ),
            departure_time=datetime(
                2024, 2, 2, 12, tzinfo=timezone('EET')
            ),
            arrival_time=datetime(
                2024, 2, 2, 13, tzinfo=timezone('EET')
            ),
            distance=200,
            airplane=plane,
            departure_airport=airports[0],
            destination_airport=airports[1]
        )
        self.ticket = Ticket.objects.create(
            ticket_code='testticket',
            seat=seat,
            flight=flight
        )
        self.purchase = Purchase.objects.create(
            user=self.user
        )
        self.purchase.tickets.add(self.ticket)
        self.purchase.save()

    def test_get_online_check_in_view(self):
        """Try to get online check-in view."""
        response = self.client.get(reverse('client:online_checkin',
                                           args=[self.purchase.id]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/online_checkin.html')
        self.assertContains(response, 'Online Check-In')

    def test_post_to_online_check_in_view(self):
        """Post to online check-in view"""
        response = self.client.post(reverse('client:online_checkin',
                                            args=[self.purchase.id]))
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('client:profile'))
        self.ticket.refresh_from_db()
        self.assertTrue(self.ticket.checked_in)


class TestHomeAndFlightSearchViews(TestCase):
    """Test home and flight search views."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword',
                                             email='test@gmail.com')
        self.client.login(username='testuser', password='testpassword')
        airports = [('Borispil', 'KBP'), ('Zhuliany', 'IEV')]
        self.airports = [
            Airport.objects.create(
                name=airport[0],
                city='Kyiv',
                country='Ukraine',
                IATA_code=airport[1]
            ) for airport in airports
        ]
        self.flight_search_link = reverse('client:flights_search') + (
            f"?from={self.airports[0].id}"
            f"&to={self.airports[1].id}"
            f"&day=02"
            f"&month=02"
            f"&year=2024"
            f"&passengers=1"
        )

    def test_get_home_view(self):
        """Try to get home page."""
        response = self.client.get(reverse('client:home'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/home.html')
        self.assertContains(response, 'Find your flight')

    def test_post_to_home_view(self):
        """Post data to home page."""
        response = self.client.post(reverse('client:home'), data={
            'arriving': self.airports[0].id,
            'destination': self.airports[1].id,
            'date_month': '02',
            'date_day': '02',
            'date_year': '2024',
            'passengers': 1
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, self.flight_search_link)

    def test_get_flight_search_view(self):
        """Try to get flight search page."""
        plane = Airplane.objects.create(
            number='testplane'
        )
        Flight.objects.create(
            number='testflight',
            ticket_price=50,
            boarding_time=datetime(
                2024, 2, 2, 11, tzinfo=timezone('EET')
            ),
            departure_time=datetime(
                2024, 2, 2, 12, tzinfo=timezone('EET')
            ),
            arrival_time=datetime(
                2024, 2, 2, 13, tzinfo=timezone('EET')
            ),
            distance=200,
            airplane=plane,
            departure_airport=self.airports[0],
            destination_airport=self.airports[1]
        )
        response = self.client.get(self.flight_search_link)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/flights_search.html')
        self.assertContains(response, 'testflight')


class TestBuyTicketsAndCheckoutViews(TestCase):
    """Test buy tickets and checkout views."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword',
                                             email='test@gmail.com',
                                             email_is_verified=True)
        self.client.login(username='testuser', password='testpassword')
        self.plane = Airplane.objects.create(
            number='testplane'
        )
        airports = [('Borispil', 'KBP'), ('Zhuliany', 'IEV')]
        airports = [
            Airport.objects.create(
                name=airport[0],
                city='Kyiv',
                country='Ukraine',
                IATA_code=airport[1]
            ) for airport in airports
        ]
        self.flight = Flight.objects.create(
            number='testflight',
            ticket_price=50,
            boarding_time=datetime(
                2024, 2, 2, 11, tzinfo=timezone('EET')
            ),
            departure_time=datetime(
                2024, 2, 2, 12, tzinfo=timezone('EET')
            ),
            arrival_time=datetime(
                2024, 2, 2, 13, tzinfo=timezone('EET')
            ),
            distance=200,
            airplane=self.plane,
            departure_airport=airports[0],
            destination_airport=airports[1]
        )
        Discount.objects.create(
            name='test_discount',
            amount=10,
            promo_code='test_promo'
        )
        self.seat_type = SeatType.objects.create(
            seat_type='Economy',
            price_multiplier=1
        )
        seat = Seat.objects.create(
            number='11',
            airplane=self.plane,
            seat_type=self.seat_type
        )
        self.ticket = Ticket.objects.create(
            ticket_code='testticket',
            seat=seat,
            flight=self.flight
        )

    def test_get_buy_tickets_view(self):
        """Try to get buy tickets view."""
        response = self.client.get(reverse('client:buy_tickets',
                                           args=[self.flight.id]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/buy_tickets.html')
        self.assertContains(response, 'Buy tickets')

    def test_post_to_buy_tickets_view(self):
        """Post data to buy tickets view."""
        response = self.client.post(
            reverse('client:buy_tickets',
                    args=[self.flight.id]),
            data={
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "0",
                "form-0-first_name": "John",
                "form-0-last_name": "Doe",
                'form-0-passport_number': 'qw123456',
                'form-0-seat_class': self.seat_type.id,
                'form-0-options': [],
                'form-0-promo_code': 'test_promo'
            }
        )
        purchase = Purchase.objects.first()
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'client:checkout', args=[purchase.id]
        ))
        self.ticket.refresh_from_db()
        self.assertEquals(self.ticket.discount.name, 'test_discount')

    def test_checkout_view(self):
        """Try to get checkout page."""
        purchase = Purchase.objects.create(
            user=self.user
        )
        purchase.tickets.add(self.ticket)
        purchase.save()
        response = self.client.get(reverse(
            'client:checkout', args=[purchase.id]
        ))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/checkout.html')
        self.assertContains(response, 'testticket')


class TestPaymentViews(TestCase):
    """Test payment views."""
    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             password='testpassword',
                                             email='test@gmail.com',
                                             email_is_verified=True)
        self.client.login(username='testuser', password='testpassword')
        self.purchase = Purchase.objects.create(
            user=self.user
        )
        self.plane = Airplane.objects.create(
            number='testplane'
        )
        airports = [('Borispil', 'KBP'), ('Zhuliany', 'IEV')]
        airports = [
            Airport.objects.create(
                name=airport[0],
                city='Kyiv',
                country='Ukraine',
                IATA_code=airport[1]
            ) for airport in airports
        ]
        self.flight = Flight.objects.create(
            number='testflight',
            ticket_price=50,
            boarding_time=datetime(
                2024, 2, 2, 11, tzinfo=timezone('EET')
            ),
            departure_time=datetime(
                2024, 2, 2, 12, tzinfo=timezone('EET')
            ),
            arrival_time=datetime(
                2024, 2, 2, 13, tzinfo=timezone('EET')
            ),
            distance=200,
            airplane=self.plane,
            departure_airport=airports[0],
            destination_airport=airports[1]
        )
        Discount.objects.create(
            name='test_discount',
            amount=10,
            promo_code='test_promo'
        )
        self.seat_type = SeatType.objects.create(
            seat_type='Economy',
            price_multiplier=1
        )
        seat = Seat.objects.create(
            number='11',
            airplane=self.plane,
            seat_type=self.seat_type
        )
        self.ticket = Ticket.objects.create(
            ticket_code='testticket',
            seat=seat,
            flight=self.flight
        )
        self.purchase.tickets.add(self.ticket)

    def test_create_payment_view(self):
        """Try to get create payment view."""
        response = self.client.get(reverse(
            'client:create_payment', args=[self.purchase.id, 'paypal']
        ))
        self.assertEquals(response.status_code, 302)

    @patch('client.tasks.send_email_with_receipt_and_ticket.delay',
           send_email_with_receipt_and_ticket)
    def test_payment_success_view(self):
        """Try to get payment success view."""
        response = self.client.get(reverse(
            'client:payment_success', args=[self.purchase.id]
        ))
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('client:profile'))
        self.purchase.refresh_from_db()
        self.assertTrue(self.purchase.is_paid)
        self.assertEquals(len(mail.outbox), 1)

    def test_payment_failed_view(self):
        """Try to get payment failed view."""
        response = self.client.get(reverse(
            'client:payment_failed', args=[self.purchase.id]
        ))
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse(
            'client:checkout', args=[self.purchase.id]
        ))
