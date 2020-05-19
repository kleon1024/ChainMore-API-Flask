from flask import current_app

from tests.base import BaseTestCase


class AuthTestCase(BaseTestCase):
    def test_login(self):
        self.OK(self.login())

    def test_logout(self):
        self.login()
        self.OK(self.logout())
