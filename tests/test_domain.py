from flask import current_app
from tests.base import BaseTestCase


class DomainTestCase(BaseTestCase):
    # def test_create_domain(self):
    #     self.login()
    #     response = self.post('/v1/domain',
    #                          json=dict(title='Education',
    #                                    dependeds=[1],
    #                                    aggregators=[1]))
    #     data = self.OK(response)
    #     domain_id = data['items'][0]['id']
    #     self.assertEqual(data['items'][0]['title'], 'Education')

    #     response = self.get('/v1/domain', query_string=dict(id=domain_id))
    #     data = self.OK(response)
    #     self.assertEqual(data['items'][0]['title'], 'Education')

    #     self.logout()

    # def test_aggregate_domain(self):
    #     self.login()
    #     # Root
    #     # |  |
    #     # a0 a1
    #     response = self.post('/v1/domain',
    #                          json=dict(title='Agg0',
    #                                    dependeds=[1],
    #                                    aggregators=[1]))
    #     data = self.OK(response)
    #     a0_id = data['items'][0]['id']
    #     response = self.post('/v1/domain',
    #                          json=dict(title='Agg1',
    #                                    dependeds=[1],
    #                                    aggregators=[1]))
    #     data = self.OK(response)
    #     a1_id = data['items'][0]['id']

    #     response = self.get('/v1/domain/aggregators', query_string=dict(id=1, distance=0))
    #     data = self.OK(response)
    #     self.assertEqual(len(data['items']), 1)
    #     for item in data['items']:
    #         self.assertEqual(item['ancestor']['id'], 1)
    #         self.assertEqual(item['descendant']['id'], 1)
    #         self.assertEqual(item['distance'], 0)

    #     response = self.get('/v1/domain/aggregateds', query_string=dict(id=1, distance=3))
    #     data = self.OK(response)
    #     self.assertEqual(len(data['items']), 3)
    #     for item in data['items']:
    #         self.assertEqual(item['ancestor']['id'], 1)
    #         if item['descendant']['id'] == 1:
    #             self.assertEqual(item['distance'], 0)
    #         elif item['descendant']['id'] == a0_id:
    #             self.assertEqual(item['distance'], 1)
    #         elif item['descendant']['id'] == a1_id:
    #             self.assertEqual(item['distance'], 1)

    #     self.logout()

    # def test_depend_domain(self):
    #     self.login()
    #     # Root
    #     # |  |
    #     # a0 a1
    #     response = self.post('/v1/domain',
    #                          json=dict(title='Dep0',
    #                                    dependeds=[1],
    #                                    aggregators=[1]))
    #     data = self.OK(response)
    #     a0_id = data['items'][0]['id']
    #     response = self.post('/v1/domain',
    #                          json=dict(title='Dep1',
    #                                    dependeds=[1],
    #                                    aggregators=[1]))
    #     data = self.OK(response)
    #     a1_id = data['items'][0]['id']

    #     response = self.get('/v1/domain/dependeds', query_string=dict(id=1))
    #     data = self.OK(response)
    #     self.assertEqual(len(data['items']), 1)
    #     for item in data['items']:
    #         self.assertEqual(item['ancestor']['id'], 1)
    #         self.assertEqual(item['descendant']['id'], 1)
    #         self.assertEqual(item['distance'], 0)

    #     response = self.get('/v1/domain/dependants', query_string=dict(id=1))
    #     data = self.OK(response)
    #     self.assertEqual(len(data['items']), 3)
    #     for item in data['items']:
    #         self.assertEqual(item['ancestor']['id'], 1)
    #         if item['descendant']['id'] == 1:
    #             self.assertEqual(item['distance'], 0)
    #         elif item['descendant']['id'] == a0_id:
    #             self.assertEqual(item['distance'], 1)
    #         elif item['descendant']['id'] == a1_id:
    #             self.assertEqual(item['distance'], 1)

    #     self.logout()

    # def test_gen_depends_domain(self):
    #     self.login()
    #     # Root
    #     # |  |
    #     # a0 a1
    #     #
    #     response = self.post('/v1/domain',
    #                          json=dict(title='Dep0',
    #                                    dependeds=[1],
    #                                    aggregators=[1]))
    #     data = self.OK(response)
    #     a0_id = data['items'][0]['id']
    #     response = self.post('/v1/domain',
    #                          json=dict(title='Dep1',
    #                                    dependeds=[1],
    #                                    aggregators=[1]))
    #     data = self.OK(response)
    #     a1_id = data['items'][0]['id']

    #     response = self.get('/v1/domain/depends',
    #                         query_string=dict(id=a1_id))
    #     data = self.OK(response)
    #     self.assertEqual(len(data['items']), 2)
    #     self.assertEqual(data['items'][0]['id'], 1)
    #     self.assertEqual(data['items'][1]['id'], a1_id)

    # def test_mark_domain(self):
    #     self.login()
    #     response = self.post('/v1/domain',
    #                          json=dict(title='DEP0',
    #                                    dependeds=[1],
    #                                    aggregators=[1]))
    #     data = self.OK(response)
    #     id = data['items'][0]['id']
    #     response = self.post('/v1/domain/mark',
    #                          json=dict(id=id))
    #     data = self.OK(response)
    #     self.assertEqual(data['items'][0]['id'], id)

    #     response = self.get('/v1/domain/marked')
    #     data = self.OK(response)
    #     self.assertEqual(len(data['items']), 2)

    # def test_learn_domain(self):
    #     self.login()
    #     '''
    #     infinity 1
    #     |      |
    #     DEP0 2 DEP1 3
    #     |      |
    #     DEP2 4 -
    #     |
    #     DEP3 5
    #     '''
    #     response = self.post('/v1/domain',
    #                          json=dict(title='DEP0',
    #                                    dependeds=[1],
    #                                    aggregators=[1]))
    #     data = self.OK(response)
    #     dep0_id = data['items'][0]['id']
    #     response = self.post('/v1/domain',
    #                          json=dict(title='DEP1',
    #                                    dependeds=[1],
    #                                    aggregators=[1]))
    #     data = self.OK(response)
    #     dep1_id = data['items'][0]['id']
    #     response = self.post('/v1/domain',
    #                          json=dict(title='DEP2',
    #                                    dependeds=[dep0_id, dep1_id],
    #                                    aggregators=[1]))
    #     data = self.OK(response)
    #     dep2_id = data['items'][0]['id']
    #     response = self.post('/v1/domain',
    #                          json=dict(title='DEP3',
    #                                    dependeds=[dep2_id],
    #                                    aggregators=[1]))
    #     data = self.OK(response)
    #     dep3_id = data['items'][0]['id']

    #     response = self.get('/v1/domain/depends',
    #                         query_string=dict(
    #                             id=dep3_id
    #                         ))
    #     data = self.OK(response)
    #     self.format(data['items'])
    #     self.assertEqual(len(data['items']), 5)
    #     self.assertEqual(data['items'][0]['id'], 1)
    #     self.assertEqual(data['items'][3]['id'], dep2_id)
    #     self.assertEqual(data['items'][4]['id'], dep3_id)

    # def test_put_domain(self):
    #     self.login()
    #     '''
    #     root 
    #     |    
    #     DEP0 
    #     '''
    #     response = self.post('/v1/domain',
    #                          json=dict(title="DEP0",
    #                                    dependeds=[1],
    #                                    aggregators=[1]))
    #     data = self.OK(response)
    #     dep0_id = data['items'][0]['id']
    #     response = self.put('/v1/domain',
    #                         json=dict(
    #                             id=dep0_id,
    #                             title="DEP1",
    #                             dependeds=[1],
    #                             aggregators=[1],
    #                         ))
    #     data = self.OK(response)
    #     self.assertEqual(data['items'][0]['id'], dep0_id)

    #     response = self.get('/v1/domain', query_string=dict(id=dep0_id))
    #     self.OK(response)
    #     data = response.get_json()
    #     self.assertEqual(data["items"][0]["title"], "DEP1")

    def test_put_dep_domain(self):
        self.login()
        '''
        root ---  ---
        |      |     |
        DEP0   DEP1  DEP4
        |      |
        DEP5   |
        |      |
        DEP2 --
        |
        DEP3
        '''
        response = self.post('/v1/domain',
                             json=dict(title="DEP0",
                                       dependeds=[1],
                                       aggregators=[1]))
        data = self.OK(response)
        dep0_id = data['items'][0]['id']

        response = self.post('/v1/domain',
                             json=dict(title="DEP1",
                                       dependeds=[1],
                                       aggregators=[1]))
        data = self.OK(response)
        dep1_id = data['items'][0]['id']

        response = self.post('/v1/domain',
                             json=dict(title="DEP5",
                                       dependeds=[dep0_id],
                                       aggregators=[dep0_id]))
        data = self.OK(response)
        dep5_id = data['items'][0]['id']

        response = self.post('/v1/domain',
                             json=dict(title="DEP4",
                                       dependeds=[1],
                                       aggregators=[1]))
        data = self.OK(response)
        dep4_id = data['items'][0]['id']

        response = self.post('/v1/domain',
                             json=dict(title="DEP2",
                                       dependeds=[dep5_id, dep1_id],
                                       aggregators=[dep0_id]))
        data = self.OK(response)
        dep2_id = data['items'][0]['id']

        response = self.post('/v1/domain',
                             json=dict(title="DEP3",
                                       dependeds=[dep2_id],
                                       aggregators=[dep2_id]))
        data = self.OK(response)
        dep3_id = data['items'][0]['id']

        response = self.get('/v1/domain/dependeds',
                            query_string=dict(id=dep2_id, distance=6))
        data = self.OK(response)
        self.assertEqual(len(data['items']), 5)
        self.assertEqual(data['items'][0]['ancestor_id'], 1)
        self.assertEqual(data['items'][0]['distance'], 3)
        self.assertEqual(data['items'][1]['ancestor_id'], dep0_id)
        self.assertEqual(data['items'][1]['distance'], 2)
        self.assertIn(data['items'][2]['ancestor_id'], [dep5_id, dep1_id])
        self.assertEqual(data['items'][2]['distance'], 1)
        self.assertIn(data['items'][3]['ancestor_id'], [dep5_id, dep1_id])
        self.assertEqual(data['items'][3]['distance'], 1)
        self.assertEqual(data['items'][4]['ancestor_id'], dep2_id)
        self.assertEqual(data['items'][4]['distance'], 0)

        response = self.get('/v1/domain/dependeds',
                            query_string=dict(id=dep3_id, distance=6))
        data = self.OK(response)
        self.assertEqual(len(data['items']), 6)
        self.assertEqual(data['items'][0]['ancestor_id'], 1)
        self.assertEqual(data['items'][0]['distance'], 4)
        self.assertEqual(data['items'][1]['ancestor_id'], dep0_id)
        self.assertEqual(data['items'][1]['distance'], 3)
        self.assertIn(data['items'][2]['ancestor_id'], [dep5_id, dep1_id])
        self.assertEqual(data['items'][2]['distance'], 2)
        self.assertIn(data['items'][3]['ancestor_id'], [dep5_id, dep1_id])
        self.assertEqual(data['items'][3]['distance'], 2)
        self.assertEqual(data['items'][4]['ancestor_id'], dep2_id)
        self.assertEqual(data['items'][4]['distance'], 1)
        self.assertEqual(data['items'][5]['ancestor_id'], dep3_id)
        self.assertEqual(data['items'][5]['distance'], 0)

        response = self.get('/v1/domain/dependants',
                            query_string=dict(id=dep2_id, distance=3))
        data = self.OK(response)
        self.assertEqual(len(data['items']), 2)
        self.assertEqual(data['items'][0]['descendant_id'], dep2_id)
        self.assertEqual(data['items'][0]['distance'], 0)
        self.assertEqual(data['items'][1]['descendant_id'], dep3_id)
        self.assertEqual(data['items'][1]['distance'], 1)

        response = self.put('/v1/domain',
                            json=dict(
                                id=dep2_id,
                                title="DEP1",
                                dependeds=[dep5_id, dep4_id],
                                aggregators=[dep1_id],
                            ))
        data = self.OK(response)
        self.assertEqual(data['items'][0]['id'], dep2_id)

        response = self.get('/v1/domain/dependeds',
                            query_string=dict(id=dep2_id, distance=3))
        data = self.OK(response)
        self.format(data)
        self.assertEqual(len(data['items']), 5)
        self.assertEqual(data['items'][0]['ancestor_id'], 1)
        self.assertEqual(data['items'][0]['distance'], 3)
        self.assertEqual(data['items'][1]['ancestor_id'], dep0_id)
        self.assertEqual(data['items'][1]['distance'], 2)
        self.assertIn(data['items'][2]['ancestor_id'], [dep5_id, dep4_id])
        self.assertEqual(data['items'][2]['distance'], 1)
        self.assertIn(data['items'][3]['ancestor_id'], [dep5_id, dep4_id])
        self.assertEqual(data['items'][3]['distance'], 1)
        self.assertEqual(data['items'][4]['ancestor_id'], dep2_id)
        self.assertEqual(data['items'][4]['distance'], 0)

        response = self.get('/v1/domain/dependeds',
                            query_string=dict(id=dep3_id, distance=5))
        data = self.OK(response)
        self.assertEqual(len(data['items']), 6)
        self.assertEqual(data['items'][0]['ancestor_id'], 1)
        self.assertEqual(data['items'][0]['distance'], 4)
        self.assertEqual(data['items'][1]['ancestor_id'], dep0_id)
        self.assertEqual(data['items'][1]['distance'], 3)
        self.assertIn(data['items'][2]['ancestor_id'], [dep5_id, dep4_id])
        self.assertEqual(data['items'][2]['distance'], 2)
        self.assertIn(data['items'][3]['ancestor_id'], [dep5_id, dep4_id])
        self.assertEqual(data['items'][3]['distance'], 2)
        self.assertEqual(data['items'][4]['ancestor_id'], dep2_id)
        self.assertEqual(data['items'][4]['distance'], 1)
        self.assertEqual(data['items'][5]['ancestor_id'], dep3_id)
        self.assertEqual(data['items'][5]['distance'], 0)

        response = self.get('/v1/domain/dependants',
                            query_string=dict(id=dep2_id, distance=3))
        data = self.OK(response)
        self.assertEqual(len(data['items']), 2)
        self.assertEqual(data['items'][0]['descendant_id'], dep2_id)
        self.assertEqual(data['items'][0]['distance'], 0)
        self.assertEqual(data['items'][1]['descendant_id'], dep3_id)
        self.assertEqual(data['items'][1]['distance'], 1)
