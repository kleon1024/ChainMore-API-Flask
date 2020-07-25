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

    def test_gen_depends_domain(self):
        self.login()
        # Root
        # |  |
        # a0 a1
        #
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

        response = self.get('/v1/domain/depends',
                            query_string=dict(id=a1_id))
        data = self.OK(response)
        self.assertEqual(len(data['items']), 2)
        self.assertEqual(data['items'][0]['id'], 1)
        self.assertEqual(data['items'][1]['id'], a1_id)

    def test_mark_domain(self):
        self.login()
        response = self.post('/v1/domain',
                             json=dict(title='DEP0',
                                       dependeds=[1],
                                       aggregators=[1]))
        data = self.OK(response)
        id = data['items'][0]['id']
        response = self.post('/v1/domain/mark',
                             json=dict(id=id))
        data = self.OK(response)
        self.assertEqual(data['items'][0]['id'], id)

        response = self.get('/v1/domain/marked')
        data = self.OK(response)
        self.assertEqual(len(data['items']), 2)
    
    def test_learn_domain(self):
        self.login()
        '''
        infinity 1
        |      |
        DEP0 2 DEP1 3
        |      |
        DEP2 4 -
        |
        DEP3 5
        '''
        response = self.post('/v1/domain',
                             json=dict(title='DEP0',
                                       dependeds=[1],
                                       aggregators=[1]))
        data = self.OK(response)
        dep0_id = data['items'][0]['id']
        response = self.post('/v1/domain',
                             json=dict(title='DEP1',
                                       dependeds=[1],
                                       aggregators=[1]))
        data = self.OK(response)
        dep1_id = data['items'][0]['id']        
        response = self.post('/v1/domain',
                             json=dict(title='DEP2',
                                       dependeds=[dep0_id, dep1_id],
                                       aggregators=[1]))
        data = self.OK(response)
        dep2_id = data['items'][0]['id']
        response = self.post('/v1/domain',
                             json=dict(title='DEP3',
                                       dependeds=[dep2_id],
                                       aggregators=[1]))
        data = self.OK(response)
        dep3_id = data['items'][0]['id']

        response = self.get('/v1/domain/depends',
                            query_string=dict(
                                id=dep3_id
                            ))
        data = self.OK(response)
        self.format(data['items'])
        self.assertEqual(len(data['items']), 5)
        self.assertEqual(data['items'][0]['id'], 1)
        self.assertEqual(data['items'][3]['id'], dep2_id)
        self.assertEqual(data['items'][4]['id'], dep3_id)  

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
