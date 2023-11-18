from datetime import timedelta, datetime
from pytz import timezone

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from client.models import Purchase, User
from client.pdf_templates import create_receipt_pdf, create_ticket_pdf
from django_air.celery import app

PASSWORD_RESET_TOKEN_GENERATOR = PasswordResetTokenGenerator()


@app.task
def send_email_with_receipt_and_ticket(purchase_id):
    """Send email with receipt and ticket."""
    purchase = Purchase.objects.get(id=purchase_id)
    purchase.is_paid = True
    purchase.save()
    mail_subject = "DjangoAIR - your tickets."
    message = render_to_string("client/letters/successful_purchase.html", {
        'user': purchase.user,
    })
    mail = EmailMessage(mail_subject, message, to=[purchase.user.email])
    mail.attach('receipt.pdf', create_receipt_pdf(purchase),
                'application/pdf')
    mail.attach('tickets.pdf', create_ticket_pdf(purchase),
                'application/pdf')
    mail.send()


@app.task
def send_password_reset_email(domain, request_is_secure: bool, user_id):
    """Send an email with instructions for password changing.
    :param domain:
    :param request_is_secure:
    :param user_id:
    :return:
    """
    user = User.objects.get(id=user_id)
    mail_subject = "Reset password."
    message = render_to_string("client/letters/reset_password_letter.html", {
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user_id)),
        'token': PASSWORD_RESET_TOKEN_GENERATOR.make_token(user),
        'protocol': 'https' if request_is_secure else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[user_id.email])
    email.send()


@app.task
def send_flight_reminder(purchase_id):
    """Remind the client about coming flight via email."""
    purchase = Purchase.objects.get(id=purchase_id)
    mail_subject = "DjangoAIR - flight reminder."
    message = render_to_string("client/letters/flight_reminder.html", {
        'purchase': purchase,
    })
    mail = EmailMessage(mail_subject, message, to=[purchase.user.email])
    if mail.send():
        purchase.reminder_is_sent = True
        purchase.save()


@app.task
def flight_client_reminder():
    """Find coming flights and send email remind to the clients."""
    purchases = Purchase.objects.filter(reminder_is_sent=False)
    for purchase in purchases:
        if purchase.tickets.first().flight.departure_time - \
                timedelta(hours=6) < datetime.now(tz=timezone('EET')):
            send_flight_reminder.delay(purchase.id)


@app.task
def check_purchase_is_paid():
    """Delete Purchase if it isn't paid in 15 minutes after created."""
    purchases = Purchase.objects.filter(is_paid=False)
    for purchase in purchases:
        if purchase.created + timedelta(minutes=15) < \
                datetime.now(tz=timezone('EET')):
            for ticket in purchase.tickets.all():
                ticket.passenger = None
                ticket.is_available = True
            purchase.delete()
