from flask import current_app

from tests.base import BaseTestCase

class MainTestCase(BaseTestCase):

    def test_get_category_groups(self):
        self.login()
        response = self.get('/v1/category_groups')
        self.OK(response)
        data = response.get_json()
        self.assertEqual(len(data["items"]), 4)
        self.assertEqual(data["items"][0]["title"], "媒介")
        self.assertEqual(data["items"][0]["categories"][0]["category"], "文章")