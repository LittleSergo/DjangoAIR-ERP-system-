from io import StringIO
from django.core.management import call_command
from django.test import TestCase


class FakeDataTest(TestCase):
    def test_command_output(self):
        """Check the expected output.
        :return:
        """
        out = StringIO()
        call_command('fake_data', stdout=out)
        self.assertIn('Successfully created.', out.getvalue())
