import datetime
from io import BytesIO

from reportlab.lib.colors import white, black
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, TableStyle, Table, Spacer, PageBreak, Paragraph
)


def page_template(canvas, doc):
    """Page template."""
    canvas.saveState()
    canvas.setFillColorRGB(0.05078125, 0.4296875, 0.98828125)
    canvas.rect(-5, 800, 620, 42, stroke=1, fill=1)
    canvas.setFillColor(white)
    canvas.setFont('Helvetica', 16)
    canvas.drawString(12, 815, 'DjangoAIR')
    canvas.setFillColorRGB(0, 0, 0)
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch, "DjangoAIR")
    canvas.restoreState()


def create_receipt_pdf(purchase):
    """Create and return pdf file with receipt for completed purchase.
    :param purchase:
    :return:
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    head_table_style = TableStyle([
        ('FONTSIZE', (0, 0), (0, 0), 18),
        ('FONTSIZE', (0, 1), (0, 1), 10),
        ('ALIGNMENT', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ])
    # Receipt header with date of payment.
    story = [
        Table([
            ['Receipt'],
            [datetime.datetime.now().strftime('%d/%m/%Y %H:%M')]
        ], style=head_table_style),
        Spacer(1, 10)
    ]
    # List with receipt rows
    receipt = [
        ['Name:' + ' ' * 80, 'Price:']
    ]
    table_style = TableStyle([
        ('LINEBELOW', (0, 0), (-1, -2), 1, black),
        ('LINEBEFORE', (1, 0), (1, -1), 1, black),
        ('ALIGNMENT', (0, -1), (0, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ALIGNMENT', (-1, 1), (-1, -1), 'RIGHT'),
    ])
    for ticket in purchase.tickets.all():
        # append row with information about type of seat and passenger
        # and price for it
        receipt.append([
            f'{ticket.seat.seat_type} ticket - {ticket.passenger}',
            f'{ticket.price()} EUR'
        ])
        for option in ticket.options.all():
            # append row with name and price of option
            receipt.append([f'  - {option.name.lower()}',
                            f'{option.price} EUR'])
        # check if the ticket have discount
        if ticket.discount:
            # check if there is a percentage discount
            if ticket.discount.is_percentage:
                # append discount to receipt
                receipt.append(['Discount:',
                                f'{ticket.discount.amount}%'])
                # and add styles for row with discount
                table_style.add('ALIGNMENT', (0, len(receipt) - 1),
                                (0, len(receipt) - 1), 'RIGHT')
            else:
                # append discount to receipt
                receipt.append(['Discount:',
                                f'{ticket.discount.amount} EUR'])
                # and add styles for row with discount
                table_style.add('ALIGNMENT', (0, len(receipt) - 1),
                                (0, len(receipt) - 1), 'RIGHT')
        # append total ticket price to receipt
        receipt.append(['  Total ticket price:',
                        f'{ticket.full_price()} EUR'])
        # and add styles for row with total ticket price
        table_style.add('ALIGNMENT', (0, len(receipt) - 1),
                        (0, len(receipt) - 1), 'RIGHT')
    # append total purchase price to receipt
    receipt.append(['Total:', f"{purchase.total_bill()} EUR"])
    # create a table and add table to story
    table = Table(receipt, style=table_style)
    story.append(table)
    # build pdf with story
    doc.build(story, onFirstPage=page_template)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def create_ticket_pdf(purchase):
    """Create and return pdf file with ticket or tickets depends on
    tickets in purchase.
    :param purchase:
    :return:
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    story = []
    for ticket in purchase.tickets.all():
        ticket_data = [
            ['Boarding pass', ticket.ticket_code, ticket.seat.seat_type],
            ['Passenger name', 'Date', 'Time'],
            [ticket.passenger,
             ticket.flight.departure_time.strftime('%d/%m/%Y'),
             ticket.flight.departure_time.strftime('%H:%M')],
            ['From', 'Flight', 'Seat'],
            [ticket.flight.departure_airport,
             ticket.flight, ticket.seat],
            ['To', '', 'Boarding'],
            [ticket.flight.destination_airport,
             '', ticket.flight.boarding_time.strftime('%H:%M')]
        ]
        table_style = TableStyle([
            ('FONTSIZE', (0, 0), (2, 0), 20),
            ('RIGHTPADDING', (0, 1), (2, 1), 105),
            ('BOTTOMPADDING', (0, 0), (2, 0), 25),
            ('BOTTOMPADDING', (0, 1), (2, 1), 0),
            ('BOTTOMPADDING', (0, 2), (2, 2), 20),
            ('BOTTOMPADDING', (0, 3), (2, 3), 0),
            ('BOTTOMPADDING', (0, 4), (2, 4), 20),
            ('BOTTOMPADDING', (0, 5), (2, 5), 0),
            ('BOTTOMPADDING', (0, 6), (2, 6), 20),
            ('FONTSIZE', (0, 2), (2, 2), 14),
            ('FONTSIZE', (0, 4), (2, 4), 14),
            ('FONTSIZE', (0, 6), (2, 6), 14),
            ('TEXTCOLOR', (0, 1), (2, 1), 'GRAY'),
            ('TEXTCOLOR', (0, 3), (2, 3), 'GRAY'),
            ('TEXTCOLOR', (0, 5), (2, 5), 'GRAY'),
            ('BACKGROUND', (0, 0), (2, 0), 'ORANGE'),
        ])
        table = Table(data=ticket_data, style=table_style)
        story.append(table)
        story.append(PageBreak())
    doc.build(story, onFirstPage=page_template, onLaterPages=page_template)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
