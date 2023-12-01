from django.test import SimpleTestCase
from django.urls import reverse, resolve

from .. import views


class TestUrls(SimpleTestCase):
    """Tests for urls. Check for binding of functions with urls."""
    def test_signup_url_resolves(self):
        """Check for sign up url.
        :return:
        """
        url = reverse('client:signup')
        self.assertEquals(resolve(url).func, views.signup)

    def test_login_url_resolves(self):
        """Check for login url.
        :return:
        """
        url = reverse('client:login')
        self.assertEquals(resolve(url).func, views.login_view)

    def test_logout_url_resolves(self):
        """Check for logout url.
        :return:
        """
        url = reverse('client:logout')
        self.assertEquals(resolve(url).func, views.logout_user)

    def test_profile_url_resolves(self):
        """Check for profile url.
        :return:
        """
        url = reverse('client:profile')
        self.assertEquals(resolve(url).func, views.user_profile)

    def test_change_password_url_resolves(self):
        """Check for change password url.
        :return:
        """
        url = reverse('client:change_password', args=['ts', 11])
        self.assertEquals(resolve(url).func, views.change_password)

    def test_online_checkin_url_resolves(self):
        """Check for online checkin url.
        :return:
        """
        url = reverse('client:online_checkin', args=[1, ])
        self.assertEquals(resolve(url).func, views.online_checkin)

    def test_home_url_resolves(self):
        """Check for home url.
        :return:
        """
        url = reverse('client:home')
        self.assertEquals(resolve(url).func, views.home)

    def test_flights_search_url_resolves(self):
        """Check for flights search url.
        :return:
        """
        url = reverse('client:flights_search')
        self.assertEquals(resolve(url).func, views.flights_search)

    def test_buy_tickets_url_resolves(self):
        """Check for buy tickets url.
        :return:
        """
        url = reverse('client:buy_tickets', args=[1])
        self.assertEquals(resolve(url).func, views.buy_tickets)

    def test_checkout_url_resolves(self):
        """Check for checkout url.
        :return:
        """
        url = reverse('client:checkout', args=[1])
        self.assertEquals(resolve(url).func, views.checkout_view)

    def test_create_payment_url_resolves(self):
        """Check for create payment url.
        :return:
        """
        url = reverse('client:create_payment', args=[1, 'paypal'])
        self.assertEquals(resolve(url).func, views.create_payment)

    def test_execute_payment_url_resolves(self):
        """Check for execute payment url.
        :return:
        """
        url = reverse('client:execute_payment', args=[1])
        self.assertEquals(resolve(url).func, views.execute_payment)

    def test_payment_success_url_resolves(self):
        """Check for payment success url.
        :return:
        """
        url = reverse('client:payment_success', args=[1])
        self.assertEquals(resolve(url).func, views.payment_success)

    def test_payment_failed_url_resolves(self):
        """Check for payment failed url.
        :return:
        """
        url = reverse('client:payment_failed', args=[1])
        self.assertEquals(resolve(url).func, views.payment_failed)
