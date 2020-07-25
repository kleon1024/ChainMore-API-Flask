from flask import current_app

from tests.base import BaseTestCase


class CollectionTestCase(BaseTestCase):
    def test_create_collection(self):
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
                             json=dict(title='HTML for beginner',
                                       url='https://github.com',
                                       external=True,
                                       free=True,
                                       resource_type_id=resource_type_id,
                                       media_type_id=media_type_id))
        data = self.OK(response)
        resource_id = data['items'][0]['id']

        response = self.post('/v1/collection',
                             json=dict(
                                 title='HTML Beginner\'s Compilation',
                                 description='Not ready',
                                 domain_id=1,
                                 resources=[resource_id],
                             ))
        data = self.OK(response)

        self.logout()

    def test_collection_duplicate_resource(self):
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
                             json=dict(title='HTML for beginner',
                                       url='https://github.com',
                                       external=True,
                                       free=True,
                                       resource_type_id=resource_type_id,
                                       media_type_id=media_type_id))
        data = self.OK(response)
        resource_id = data['items'][0]['id']

        response = self.post(
            '/v1/collection',
            json=dict(
                title='HTML Beginner\'s Compilation',
                description='Not ready',
                domain_id=1,
                resources=[resource_id, resource_id, resource_id],
            ))
        data = self.OK(response)
        self.logout()

    def test_collection_ordered_resource(self):
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
                             json=dict(title='HTML for beginner',
                                       url='https://github.com',
                                       external=True,
                                       free=True,
                                       resource_type_id=resource_type_id,
                                       media_type_id=media_type_id))
        data = self.OK(response)
        resource_id = data['items'][0]['id']

        response = self.post('/v1/resource/exist',
                            json=dict(url='https://github.com'))
        data = self.OK(response)
        self.assertEqual(data['items'][0]['id'], resource_id)

        response = self.post('/v1/resource',
                             json=dict(title='HTML2 for beginner',
                                       url='https://github2.com',
                                       external=True,
                                       free=True,
                                       resource_type_id=resource_type_id,
                                       media_type_id=media_type_id))
        data = self.OK(response)
        resource2_id = data['items'][0]['id']

        response = self.post('/v1/resource',
                             json=dict(title='HTML3 for beginner',
                                       url='https://github3.com',
                                       external=True,
                                       free=True,
                                       resource_type_id=resource_type_id,
                                       media_type_id=media_type_id))
        data = self.OK(response)
        resource3_id = data['items'][0]['id']

        response = self.post('/v1/collection',
                             json=dict(
                                 title='HTML Beginner\'s Compilation',
                                 description='Not ready',
                                 domain_id=1,
                                 resources=[resource_id, resource2_id],
                             ))
        data = self.OK(response)
        collection_id = data['items'][0]['id']

        response = self.put('/v1/collection',
                            json=dict(
                                id=collection_id,
                                title='HTML Beginner\'s Compilation',
                                description='Not ready',
                                domain_id=1,
                                resources=[resource3_id, resource2_id],
                            ))
        data = self.OK(response)

        self.logout()
