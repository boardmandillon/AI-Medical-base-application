from flask_mail import Message

from app import mail, celery


@celery.task(name='send_email')
def send_email(subject, sender, recipients, text_body, html_body):
    """Send an email asynchronously with the given subject, sender,
    recipients, text_body and html_body.
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
