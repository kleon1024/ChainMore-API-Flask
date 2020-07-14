from flask import current_app

from tests.base import BaseTestCase


class MainTestCase(BaseTestCase):

    def test_get_types(self):
        self.login()
        response = self.get('/v1/type')
        data = self.OK(response)
        self.logout()