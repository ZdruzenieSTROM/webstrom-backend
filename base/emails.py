from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string


def send_bulk_html_emails(emails, template, subject, context):
    messages = []

    for email in emails:
        ctx = context

        text = render_to_string(f"{template}.txt", ctx)
        html = render_to_string(f"{template}.html", ctx)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=None,
            to=[email],
        )
        msg.attach_alternative(html, "text/html")
        messages.append(msg)

    # open **one connection** for efficiency
    connection = get_connection()
    connection.send_messages(messages)
