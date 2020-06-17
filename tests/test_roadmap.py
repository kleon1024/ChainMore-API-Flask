from flask import current_app

from tests.base import BaseTestCase


class RoadmapTestCase(BaseTestCase):
    def test_create_roadmap(self):
        self.login()

        response = self.post('/v1/domain',
                             json=dict(title='Education',
                                       intro='',
                                       dependeds=[1],
                                       aggregators=[1]))
        data = self.OK(response)
        domain_id = data['items'][0]['id']

        response = self.post('/v1/roadmap',
                             json=dict(title='Eduation X',
                                       intro='BlaBla',
                                       description='TODO',
                                       nodes=[
                                           dict(type='domain',
                                                id=domain_id,
                                                description='')
                                       ]))

        data = self.OK(response)

        nodes = data['items'][0]['nodes']
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0]['type'], 'domain')
        self.assertEqual(nodes[0]['nodeDomain']['id'], domain_id)

        self.logout()
