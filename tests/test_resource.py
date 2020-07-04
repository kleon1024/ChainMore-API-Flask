from flask import current_app

from tests.base import BaseTestCase


class ResourceTestCase(BaseTestCase):
    def test_create_resource(self):
        self.login()
        response = self.get('/v1/resource/media_type',
                            query_string=dict(name='text'))
        data = self.OK(response)
        self.assertEqual(data['items'][0]['name'], 'text')
        media_type_id = data['items'][0]['id']

        response = self.get('/v1/resource/resource_type',
                            query_string=dict(name='article'))
        data = self.OK(response)
        self.assertEqual(data['items'][0]['name'], 'article')
        resource_type_id = data['items'][0]['id']

        response = self.post('/v1/resource',
                             json=dict(title='HTML入门资料',
                                       url='https://github.com',
                                       external=True,
                                       free=True,
                                       resource_type_id=resource_type_id,
                                       media_type_id=media_type_id))
        data = self.OK(response)
        self.assertEqual(data['items'][0]['title'], 'HTML入门资料')
        resource_id = data['items'][0]['id']

        response = self.get('/v1/resource', query_string=dict(id=resource_id))
        data = self.OK(response)
        self.assertEqual(data['items'][0]['title'], 'HTML入门资料')

        response = self.delete('/v1/resource',
                               query_string=dict(id=resource_id))
        self.OK(response)
        self.logout()
