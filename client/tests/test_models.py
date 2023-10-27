from django.test import TestCase

from ..models import User, Purchase


class ModelsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')

    def test_user_model(self):
        """Get created User object and check data."""
        user = User.objects.get(username='testuser')
        self.assertFalse(user.email_is_verified)

    def test_purchase_model(self):
        """Create purchase object and check."""
        Purchase.objects.create(user=self.user)
        purchase = Purchase.objects.get(user=self.user)
        self.assertFalse(purchase.is_paid)
