from flask import current_app

from tests.base import BaseTestCase


class GroupTestCase(BaseTestCase):
    def test_action(self):
        self.login()

