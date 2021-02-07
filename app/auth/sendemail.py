from flask import render_template, current_app
from flask_jwt_extended import create_access_token

from app.emailtask import send_email

def create_password_reset_token(user):
    return create_access_token(
        identity={
            "user_id": user.id,
            "action": "password_reset"
        },
        fresh=True
    )

def send_password_reset_email(user):
    """Send email with password reset token to the given user."""
    token = create_password_reset_token(user)

    send_email.delay(
        '[Vulture] Reset Your Password',
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template(
            'emails/reset_password.txt', user=user, token=token),
        html_body=render_template(
            'emails/reset_password.html', user=user, token=token))
