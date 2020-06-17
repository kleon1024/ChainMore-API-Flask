from flask import current_app

from tests.base import BaseTestCase


class DomainTestCase(BaseTestCase):
    def test_create_domain(self):
        self.login()
        response = self.post('/v1/domain',
                             json=dict(title='Education',
                                       dependeds=[1],
                                       aggregators=[1]))
        data = self.OK(response)
        domain_id = data['items'][0]['id']
        self.assertEqual(data['items'][0]['title'], 'Education')

        response = self.get('/v1/domain', query_string=dict(id=domain_id))
        data = self.OK(response)
        self.assertEqual(data['items'][0]['title'], 'Education')

        self.logout()

    def test_aggregate_domain(self):
        self.login()
        # Root
        # |  |
        # a0 a1
        response = self.post('/v1/domain',
                             json=dict(title='Agg0',
                                       dependeds=[1],
                                       aggregators=[1]))
        data = self.OK(response)
        a0_id = data['items'][0]['id']
        response = self.post('/v1/domain',
                             json=dict(title='Agg1',
                                       dependeds=[1],
                                       aggregators=[1]))
        data = self.OK(response)
        a1_id = data['items'][0]['id']

        response = self.get('/v1/domain/aggregators', query_string=dict(id=1))
        data = self.OK(response)
        self.assertEqual(len(data['items']), 1)
        for item in data['items']:
            self.assertEqual(item['ancestor']['id'], 1)
            self.assertEqual(item['descendant']['id'], 1)
            self.assertEqual(item['distance'], 0)

        response = self.get('/v1/domain/aggregateds', query_string=dict(id=1))
        data = self.OK(response)
        self.assertEqual(len(data['items']), 3)
        for item in data['items']:
            self.assertEqual(item['ancestor']['id'], 1)
            if item['descendant']['id'] == 1:
                self.assertEqual(item['distance'], 0)
            elif item['descendant']['id'] == a0_id:
                self.assertEqual(item['distance'], 1)
            elif item['descendant']['id'] == a1_id:
                self.assertEqual(item['distance'], 1)

        self.logout()

    def test_depend_domain(self):
        self.login()
        # Root
        # |  |
        # a0 a1
        response = self.post('/v1/domain',
                             json=dict(title='Dep0',
                                       dependeds=[1],
                                       aggregators=[1]))
        data = self.OK(response)
        a0_id = data['items'][0]['id']
        response = self.post('/v1/domain',
                             json=dict(title='Dep1',
                                       dependeds=[1],
                                       aggregators=[1]))
        data = self.OK(response)
        a1_id = data['items'][0]['id']

        response = self.get('/v1/domain/dependeds', query_string=dict(id=1))
        data = self.OK(response)
        self.assertEqual(len(data['items']), 1)
        for item in data['items']:
            self.assertEqual(item['ancestor']['id'], 1)
            self.assertEqual(item['descendant']['id'], 1)
            self.assertEqual(item['distance'], 0)

        response = self.get('/v1/domain/dependants', query_string=dict(id=1))
        data = self.OK(response)
        self.assertEqual(len(data['items']), 3)
        for item in data['items']:
            self.assertEqual(item['ancestor']['id'], 1)
            if item['descendant']['id'] == 1:
                self.assertEqual(item['distance'], 0)
            elif item['descendant']['id'] == a0_id:
                self.assertEqual(item['distance'], 1)
            elif item['descendant']['id'] == a1_id:
                self.assertEqual(item['distance'], 1)

        self.logout()

    # def test_put_domain(self):
    #     self.login()
    #     response = self.post('/v1/domain',
    #                          json=dict(title="测试", depended=1, aggregator=1))
    #     response = self.put('/v1/domain',
    #                         json=dict(
    #                             domain=3,
    #                             title="测试2",
    #                             depended=2,
    #                             aggregator=2,
    #                         ))
    #     self.OK(response)
    #     response = self.get('/v1/domain', query_string=dict(id=3))
    #     self.OK(response)
    #     data = response.get_json()
    #     print(data["item"])
    #     self.assertEqual(data["item"]["title"], "测试2")

    # def test_create_roadmap(self):
    #     self.login()
    #     response = self.post('/v1/domain/roadmap',
    #                          json=dict(title="Python入门方案",
    #                                    description="适合0基础的孩子",
    #                                    heads=[2]))
    #     self.OK(response)
    #     response = self.get('/v1/domain/roadmap', query_string=dict(roadmap=1))
    #     data = response.get_json()
    #     self.assertEqual(data["roadmap"]["title"], "Python入门方案")

    # def test_put_roadmap(self):
    #     self.login()
    #     response = self.post('/v1/domain/roadmap',
    #                          json=dict(title="Python入门方案",
    #                                    description="适合0基础的孩子",
    #                                    heads=[2]))
    #     response = self.put('/v1/domain/roadmap',
    #                         json=dict(title="Python基础", roadmap=1))
    #     response = self.get('/v1/domain/roadmap', query_string=dict(roadmap=1))
    #     data = response.get_json()
    #     self.assertEqual(data["roadmap"]["title"], "Python入门方案")

    # def test_learn_roadmap(self):
    #     self.login()
    #     response = self.post('/v1/domain/roadmap',
    #                          json=dict(title="Python入门方案",
    #                                    description="适合0基础的孩子",
    #                                    heads=[2]))
    #     response = self.post('/v1/domain/roadmap/learn',
    #                          query_string=dict(roadmap=1))
    #     self.OK(response)
    #     response = self.delete('/v1/domain/roadmap/learn',
    #                            query_string=dict(roadmap=1))
    #     self.OK(response)
