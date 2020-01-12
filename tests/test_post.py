from flask import current_app

from tests.base import BaseTestCase

class PostTestCase(BaseTestCase):

    def test_post_post(self):
        self.login()
        response = self.post('/v1/post', json=dict(
            title = "测试",
            domain = 1,
            url = "https://google.com",
            description = "测试文本",
            categories = [1]
        ))
        self.OK(response)

    def test_get_post(self):
        self.login()
        self.post('/v1/post', json=dict(
            title = "测试",
            domain = 1,
            url = "https://google.com",
            description = "测试文本",
            categories = [1]
        ))
        response = self.get('/v1/post', query_string=dict(
            id = 1
        ))
        self.OK(response)
        data = response.get_json()
        self.assertEqual(data["item"]["id"], 1)

    def test_put_post(self):
        self.login()
        self.post('/v1/post', json=dict(
            title = "测试",
            domain = 1,
            url = "https://google.com",
            description = "测试文本",
            categories = [1]
        ))
        response = self.put('/v1/post', json=dict(
            id = 1,
            categories = [2]
        ))
        self.OK(response)
