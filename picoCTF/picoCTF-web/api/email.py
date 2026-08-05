"""Module for email related functionality."""

import socket

from flask import current_app
from flask_mail import Mail, Message

import api
from api import PicoException

# Socket timeout - applies to SMTP connections
socket.setdefaulttimeout(10)

mail = Mail()


def refresh_email_settings():
    """
    Load the current app context mail settings.

    Called to make sure that the current thread/worker has the newest
    email settings from the database.
    """
    with current_app.app_context():
        settings = api.config.get_settings()
        if settings["email"]["enable_email"]:
            current_app.config["MAIL_SUPPRESS_SEND"] = False
            current_app.config["MAIL_SERVER"] = settings["email"]["smtp_url"]
            current_app.config["MAIL_PORT"] = settings["email"]["smtp_port"]
            current_app.config["MAIL_USERNAME"] = settings["email"]["email_username"]
            current_app.config["MAIL_PASSWORD"] = settings["email"]["email_password"]
            current_app.config["MAIL_DEFAULT_SENDER"] = settings["email"]["from_addr"]
            if settings["email"]["smtp_security"] == "TLS":
                current_app.config["MAIL_USE_TLS"] = True
                current_app.config["MAIL_USE_SSL"] = False
            elif settings["email"]["smtp_security"] == "SSL":
                current_app.config["MAIL_USE_TLS"] = False
                current_app.config["MAIL_USE_SSL"] = True
        else:
            # Use a testing configuration
            current_app.config["MAIL_SUPPRESS_SEND"] = True
            current_app.config["MAIL_DEFAULT_SENDER"] = "testing@picoctf.com"
    mail.init_app(current_app)


def request_password_reset(username):
    """
    Email a user a link to reset their password.

    Args:
        username: the username of the account

    Raises:
        PicoException: if provided username not found

    """
    refresh_email_settings()
    user = api.user.get_user(name=username)
    if user is None:
        raise PicoException("Username not found", 404)

    token_value = api.token.set_token({"uid": user["uid"]}, "password_reset")

    settings = api.config.get_settings()

    body = settings["email"]["reset_password_body"].format(  # noqa:E501
        competition_name=settings["competition_name"],
        competition_url=settings["competition_url"],
        username=username,
        token_value=token_value,
    )

    subject = "{} Password Reset".format(settings["competition_name"])

    message = Message(body=body, recipients=[user["email"]], subject=subject)
    mail.send(message)


def send_user_verification_email(username):
    """
    Email the user a link to verify their account.

    If email_verification is enabled in the config then the user
    won't be able to login until this step is completed.
    """
    refresh_email_settings()
    settings = api.config.get_settings()
    db = api.db.get_conn()

    user = api.user.get_user(name=username)

    # The number of verification attempts is stored in the key
    # along with the uid.

    key_query = {
        "$and": [{"uid": user["uid"]}, {"email_verification_count": {"$exists": True}}]
    }
    previous_key = api.token.find_key(key_query)

    if previous_key is None:
        token_value = api.token.set_token(
            {"uid": user["uid"], "email_verification_count": 1}, "email_verification"
        )
    else:
        previous_count = previous_key["email_verification_count"]
        if previous_count < settings["email"]["max_verification_emails"]:
            token_value = previous_key["tokens"]["email_verification"]
            db.tokens.find_and_modify(
                key_query, {"$inc": {"email_verification_count": 1}}
            )
        else:
            raise PicoException(
                "User has been sent the maximum number of verification " + "emails.",
                422,
            )

    verification_link = "{}/api/v1/user/verify?uid={}&token={}".format(
        settings["competition_url"], user["uid"], token_value
    )

    body = settings["email"]["verification_body"].format(
        competition_name=settings["competition_name"],
        verification_link=verification_link,
        user_name=username,
    )  # noqa (79char)

    subject = "{} Account Verification".format(settings["competition_name"])

    verification_message = Message(
        body=body, recipients=[user["email"]], subject=subject
    )

    bulk = [verification_message]

    # Also send parent verification email if neccessary
    if (
        settings["email"]["parent_verification_email"]
        and previous_key is None
        and user["demo"]["age"] == "13-17"
    ):
        body = settings["email"]["verification_parent_body"].format(
            competition_name=settings["competition_name"],
            competition_url=settings["competition_url"],
            admin_email=settings["admin_email"],
        )

        subject = "{} Parent Account Verification for {}".format(
            settings["competition_name"], user["email"]
        )
        recipients = [user["demo"]["parentemail"]]
        parent_email = Message(body=body, recipients=recipients, subject=subject)

        bulk.append(parent_email)

    with mail.connect() as conn:
        for msg in bulk:
            conn.send(msg)


def send_email_invite(gid, email, teacher=False):
    """
    Send an email registration link that will automatically join into a group.

    This link will bypass the email filter.
    """
    refresh_email_settings()
    settings = api.config.get_settings()
    group = api.group.get_group(gid=gid)

    token_value = api.token.set_token(
        {"gid": group["gid"], "email": email, "teacher": teacher}, "registration_token"
    )

    registration_link = "{}/#g={}&r={}".format(
        settings["competition_url"], group["gid"], token_value
    )

    body = settings["email"]["invite_body"].format(
        competition_name=settings["competition_name"],
        group_name=group["name"],
        registration_link=registration_link,
    )  # noqa (79char)

    subject = "{} Registration".format(settings["competition_name"])

    message = Message(body=body, recipients=[email], subject=subject)
    mail.send(message)


def send_deletion_notification(username, email, delete_reason):
    """
    Send an email to notify that an account has been deleted.
    """
    refresh_email_settings()
    settings = api.config.get_settings()

    body = settings["email"]["deletion_notification_body"].format(
        competition_name=settings["competition_name"],
        username=username,
        delete_reason=delete_reason,
    )

    subject = "{} Account Deletion".format(settings["competition_name"])

    message = Message(body=body, recipients=[email], subject=subject)
    mail.send(message)
