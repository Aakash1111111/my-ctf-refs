"""Register various types of users and store their login credentials."""

import random

import pymongo
from locust import HttpLocust, task, TaskSet
from locust.exception import StopLocust

from config import get_db, REGISTRATION_ENDPOINT
from demographics_generators import (
    get_affiliation,
    get_country_code,
    get_demographics,
    get_email,
    get_password,
    get_user_type,
    get_username,
)


def generate_user():
    """Generate a set of valid demographics for the given user type."""
    user_fields = {
        "username": get_username(),
        "password": "password",
        "email": get_email(),
        "affiliation": get_affiliation(),
        "country": get_country_code(),
        "usertype": get_user_type(),
        "demo": get_demographics(),
    }
    return user_fields


def register_and_expect_failure(l, user_demographics):
    """Attempt to register an invalid account, expecting a 400 response."""
    with l.client.post(
        REGISTRATION_ENDPOINT, json=user_demographics, catch_response=True
    ) as res:
        if res.status_code == 400:
            res.success()
        else:
            res.failure(
                "Registration not caught as invalid: parameters={}, status={}".format(
                    str(user_demographics), str(res.status_code)
                )
            )


class RegistrationTasks(TaskSet):
    """Tasks for both successful and failed registrations."""

    @task(weight=10)
    def successfully_register(l):
        """Register a valid test user and store credentials in DB."""
        user_demographics = generate_user()
        with l.client.post(
            REGISTRATION_ENDPOINT, json=user_demographics, catch_response=True
        ) as res:
            if res.status_code == 201:
                user_document = user_demographics.copy()
                user_document["rand_id"] = [random.random(), 0]
                get_db().users.insert_one(user_document)
                res.success()
            else:
                res.failure("Failed to register user")
        raise StopLocust  # Terminate after successful registration

    @task(weight=1)
    class RegistrationErrorTasks(TaskSet):
        """Tasks which fail registration for various reasons."""

        @task
        def missing_field_error(l):
            """Fail registration due to a missing required field."""
            user_demographics = generate_user()
            to_delete = random.choice(
                [
                    "username",
                    "password",
                    "email",
                    "affiliation",
                    "country",
                    "usertype",
                    "demo",
                ]
            )
            del user_demographics[to_delete]
            register_and_expect_failure(l, user_demographics)
            l.interrupt()

        @task
        def username_error(l):
            """Fail registration due to an invalid username."""
            user_demographics = generate_user()
            user_demographics["username"] = ""
            register_and_expect_failure(l, user_demographics)
            l.interrupt()

        @task
        def password_error(l):
            """Fail registration due to an invalid password."""
            user_demographics = generate_user()
            user_demographics["password"] = "oo"
            register_and_expect_failure(l, user_demographics)
            l.interrupt()

        @task
        def email_error(l):
            """Fail registration due to an invalid email address."""
            user_demographics = generate_user()
            user_demographics["email"] = "invalid_email_address"
            register_and_expect_failure(l, user_demographics)
            l.interrupt()

        @task
        def affiliation_error(l):
            """Fail registration due to an invalid affiliation."""
            user_demographics = generate_user()
            user_demographics["affiliation"] = ""
            register_and_expect_failure(l, user_demographics)
            l.interrupt()

        @task
        def country_error(l):
            """Fail registration due to an invalid country."""
            user_demographics = generate_user()
            user_demographics["country"] = "invalid_country_code"
            register_and_expect_failure(l, user_demographics)
            l.interrupt()

        @task
        def usertype_error(l):
            """Fail registration due to an invalid user type."""
            user_demographics = generate_user()
            user_demographics["usertype"] = "invalid_user_type"
            register_and_expect_failure(l, user_demographics)
            l.interrupt()

        @task
        def demo_error(l):
            """Fail registration due to invalid demographics."""
            user_demographics = generate_user()
            user_demographics["demo"]["age"] = "invalid_age"
            register_and_expect_failure(l, user_demographics)
            l.interrupt()

        @task
        def require_parent_email_error(l):
            """Fail registration due to an invalid parent email."""
            user_demographics = generate_user()
            user_demographics["demo"]["age"] = "13-17"
            user_demographics["demo"]["parentemail"] = "invalid_email"
            register_and_expect_failure(l, user_demographics)
            l.interrupt()


class RegistrationLocust(HttpLocust):
    """Main locust class. Defines the task set and wait interval limits."""

    task_set = RegistrationTasks
    min_wait = 1000
    max_wait = 4000

    def setup(l):
        """Make sure random index exists in MongoDB."""
        get_db().users.create_index([("rand_id", pymongo.GEO2D)])
