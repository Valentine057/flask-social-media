import os

from flask import url_for
from flask_mail import Message


ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


def send_password_change_email(mail, user_email, first_name):

    msg = Message(
        subject="Password Changed Successfully",
        recipients=[user_email]
    )

    msg.body = f"""
Hello {first_name},

Your password has been successfully changed.

If you did not make this change, please reset your password immediately.

Regards,
Flask Social Media Team
"""

    mail.send(msg)


def get_avatar_url_for_user_id(folder, uid):
    for ext in ALLOWED_EXT:
        candidate = os.path.join(folder, f"user_{uid}.{ext}")
        if os.path.exists(candidate):
            return url_for('static', filename=f"images/avatars/user_{uid}.{ext}")
    return None


def send_signup_email(mail, user_email, first_name):
    msg = Message(
        subject = "Welcome to Our Social Media App",
        recipients = [user_email]
    )

    msg.body = f"""
Hello {first_name},

Your account has been successfully created.

Welcome to our social media platform.
We are excited to have you!

Regards,
Social Media Team
"""

    mail.send(msg)
