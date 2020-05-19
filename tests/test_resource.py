from flask import current_app

from tests.base import BaseTestCase


class ResourceTestCase(BaseTestCase):
    def test_create_resource(self):
        self.login()
        response = self.post('/v1/resource',
                             json=dict(title='HTML入门资料',
                                       url='https://github.com',
                                       external=True,
                                       free=True,
                                       resourceTypeId=1,
                                       mediaTypeId=1))
        self.OK(response)
        response = self.get('/v1/resource', query_string=dict(id=1))
        self.OK(response)
        data = response.get_json()
        self.assertEqual(data['items'][0]['title'], 'HTML入门资料')
