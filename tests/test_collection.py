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
                                       resourceTypeId=resource_type_id,
                                       mediaTypeId=media_type_id))
        data = self.OK(response)
        resource_id = data['items'][0]['id']

        response = self.post('/v1/collection',
                             json=dict(
                                 title='HTML Beginner\'s Compilation',
                                 description='Not ready',
                                 domainId=1,
                                 resources=[resource_id],
                             ))
        data = self.OK(response)
        self.assertEqual(data['items'][0]['referenceds'][0]['id'], resource_id)

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
                                       resourceTypeId=resource_type_id,
                                       mediaTypeId=media_type_id))
        data = self.OK(response)
        resource_id = data['items'][0]['id']

        response = self.post(
            '/v1/collection',
            json=dict(
                title='HTML Beginner\'s Compilation',
                description='Not ready',
                domainId=1,
                resources=[resource_id, resource_id, resource_id],
            ))
        data = self.OK(response)
        referenceds = data['items'][0]['referenceds']
        self.assertEqual(len(referenceds), 1)
        self.assertEqual(referenceds[0]['id'], resource_id)

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
                                       resourceTypeId=resource_type_id,
                                       mediaTypeId=media_type_id))
        data = self.OK(response)
        resource_id = data['items'][0]['id']

        response = self.post('/v1/resource',
                             json=dict(title='HTML2 for beginner',
                                       url='https://github.com',
                                       external=True,
                                       free=True,
                                       resourceTypeId=resource_type_id,
                                       mediaTypeId=media_type_id))
        data = self.OK(response)
        resource2_id = data['items'][0]['id']

        response = self.post('/v1/resource',
                             json=dict(title='HTML3 for beginner',
                                       url='https://github.com',
                                       external=True,
                                       free=True,
                                       resourceTypeId=resource_type_id,
                                       mediaTypeId=media_type_id))
        data = self.OK(response)
        resource3_id = data['items'][0]['id']

        response = self.post('/v1/collection',
                             json=dict(
                                 title='HTML Beginner\'s Compilation',
                                 description='Not ready',
                                 domainId=1,
                                 resources=[resource_id, resource2_id],
                             ))
        data = self.OK(response)
        collection_id = data['items'][0]['id']
        referenceds = data['items'][0]['referenceds']

        self.assertEqual(referenceds[0]['id'], resource_id)
        self.assertEqual(referenceds[1]['id'], resource2_id)

        response = self.put('/v1/collection',
                            json=dict(
                                id=collection_id,
                                title='HTML Beginner\'s Compilation',
                                description='Not ready',
                                domainId=1,
                                resources=[resource3_id, resource2_id],
                            ))
        data = self.OK(response)
        referenceds = data['items'][0]['referenceds']
        self.assertEqual(referenceds[0]['id'], resource3_id)
        self.assertEqual(referenceds[1]['id'], resource2_id)

        self.logout()
