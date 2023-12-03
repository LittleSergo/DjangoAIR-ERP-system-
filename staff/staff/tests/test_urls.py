from django.test import SimpleTestCase
from django.urls import reverse, resolve

from .. import views


class TestUrls(SimpleTestCase):
    """Tests for urls. Check for binding of functions with urls."""
    def test_flights_url_resolves(self):
        """Check for staff flights url.
        :return:
        """
        url = reverse('staff:staff_flights')
        self.assertEquals(resolve(url).func, views.staff_flights)

    def test_create_flight_url_resolves(self):
        """Check for create flight url.
        :return:
        """
        url = reverse('staff:create_flight')
        self.assertEquals(resolve(url).func, views.create_flight)

    def test_planes_url_resolves(self):
        """Check for staff planes url.
        :return:
        """
        url = reverse('staff:staff_planes')
        self.assertEquals(resolve(url).func, views.staff_airplanes)

    def test_create_plane_url_resolves(self):
        """Check for create plane url.
        :return:
        """
        url = reverse('staff:create_airplane')
        self.assertEquals(resolve(url).func, views.create_plane_view)

    def test_pilots_url_resolves(self):
        """Check for staff pilots url.
        :return:
        """
        url = reverse('staff:staff_pilots')
        self.assertEquals(resolve(url).func, views.staff_pilot)

    def test_create_pilot_url_resolves(self):
        """Check for create pilot url.
        :return:
        """
        url = reverse('staff:create_pilot')
        self.assertEquals(resolve(url).func, views.create_pilot)

    def test_managers_url_resolves(self):
        """Check for staff managers url.
        :return:
        """
        url = reverse('staff:staff_managers')
        self.assertEquals(resolve(url).func, views.staff_managers)

    def test_create_manager_url_resolves(self):
        """Check for create manager url.
        :return:
        """
        url = reverse('staff:create_manager')
        self.assertEquals(resolve(url).func, views.create_manager)

    def test_options_url_resolves(self):
        """Check for staff options url.
        :return:
        """
        url = reverse('staff:staff_options')
        self.assertEquals(resolve(url).func, views.staff_options)

    def test_create_option_url_resolves(self):
        """Check for create option url.
        :return:
        """
        url = reverse('staff:create_option')
        self.assertEquals(resolve(url).func, views.create_option)

    def test_discounts_url_resolves(self):
        """Check for staff discounts url.
        :return:
        """
        url = reverse('staff:staff_discounts')
        self.assertEquals(resolve(url).func, views.staff_discounts)

    def test_create_discount_url_resolves(self):
        """Check for create discount url.
        :return:
        """
        url = reverse('staff:create_discount')
        self.assertEquals(resolve(url).func, views.create_discount)

    def test_check_in_menu_url_resolves(self):
        """Check for check-in menu url.
        :return:
        """
        url = reverse('staff:check_in_menu')
        self.assertEquals(resolve(url).func, views.check_in_manager_menu)

    def test_ticket_check_in_url_resolves(self):
        """Check for ticket check-in url.
        :return:
        """
        url = reverse('staff:ticket_check_in', args=[1])
        self.assertEquals(resolve(url).func, views.ticket_check_in)

    def test_boarding_menu_url_resolves(self):
        """Check for boarding menu url.
        :return:
        """
        url = reverse('staff:boarding_menu')
        self.assertEquals(resolve(url).func, views.boarding_menu)

    def test_passenger_boarding_url_resolves(self):
        """Check for passenger boarding url.
        :return:
        """
        url = reverse('staff:passenger_boarding', args=[1])
        self.assertEquals(resolve(url).func, views.boarding_passenger)

    def test_login_url_resolves(self):
        """Check for login url.
        :return:
        """
        url = reverse('staff:log_in')
        self.assertEquals(resolve(url).func, views.login_user)

    def test_logout_url_resolves(self):
        """Check for logout url.
        :return:
        """
        url = reverse('staff:log_out')
        self.assertEquals(resolve(url).func, views.logout_user)

    def test_profile_url_resolves(self):
        """Check for profile url.
        :return:
        """
        url = reverse('staff:profile', args=[1])
        self.assertEquals(resolve(url).func, views.profile)

    def test_change_password_url_resolves(self):
        """Check for change password url.
        :return:
        """
        url = reverse('staff:change_password', args=[1, 'afw2'])
        self.assertEquals(resolve(url).func, views.change_password)
