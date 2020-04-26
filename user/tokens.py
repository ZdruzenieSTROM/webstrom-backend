from datetime import datetime

from django.conf import settings
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36


class EmailVerificationTokenGenerator:
    """Vykradnutý PasswordResetTokenGenerator a upravený pre naše potreby"""

    key_salt = 'user.tokens.EmailVerifactionTokenGenerator'
    secret = settings.SECRET_KEY

    def make_token(self, user):
        return self._make_token_with_timestamp(user, self._num_seconds(self._now()))

    def check_token(self, user, token):
        if not (user and token):
            return False

        try:
            timestamp_b36, _ = token.split("-")
        except ValueError:
            return False

        try:
            timestamp = base36_to_int(timestamp_b36)
        except ValueError:
            return False

        if not constant_time_compare(self._make_token_with_timestamp(user, timestamp), token):
            return False

        if (self._num_seconds(self._now()) - timestamp) > settings.EMAIL_VERIFICATION_TIMEOUT:
            return False

        return True

    def _make_token_with_timestamp(self, user, timestamp):
        timestamp_b36 = int_to_base36(timestamp)
        hash_string = salted_hmac(
            self.key_salt,
            self._make_hash_value(user, timestamp),
            secret=self.secret
        ).hexdigest()[::2]
        return "%s-%s" % (timestamp_b36, hash_string)

    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(user.verified_email) + str(timestamp)

    def _num_seconds(self, dt):
        return int((dt - datetime(2001, 1, 1)).total_seconds())

    def _now(self):
        return datetime.now()


email_verification_token_generator = EmailVerificationTokenGenerator()
