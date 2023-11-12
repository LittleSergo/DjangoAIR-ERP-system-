import paypalrestsdk

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

from client.models import Purchase


def paypal_payment(request, purchase_id):
    """Create payment object and redirect to PayPal payment page if
    that object crated, else redirect to payment failed page.
    :param request:
    :param purchase_id:
    :return:
    """
    purchase = Purchase.objects.get(id=purchase_id)
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse(
                'client:execute_payment', args=[purchase_id]
            )),
            "cancel_url": request.build_absolute_uri(reverse(
                'client:payment_failed', args=[purchase_id]
            )),
        },
        "transactions": [
            {
                "amount": {
                    "total": str(purchase.total_bill()),
                    "currency": "EUR",
                },
                "description": "Payment for flight tickets",
            }
        ],
    })

    if payment.create():
        return redirect(payment.links[1].href)  # Redirect to PayPal for payment
    messages.error(request, f'Purchase failed. Try again.\n'
                            f'{payment.error}')
    return redirect('client:payment_failed')
