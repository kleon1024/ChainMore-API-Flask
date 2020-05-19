from flask import current_app

from tests.base import BaseTestCase


class DomainTestCase(BaseTestCase):
    def test_create_domain(self):
        self.login()
        response = self.post('/v1/domain',
                             json=dict(title="测试", depended=1, aggregator=1))
        self.OK(response)
        response = self.get('/v1/domain', query_string=dict(id=3))
        self.OK(response)
        data = response.get_json()
        print(data["item"])
        self.assertEqual(data["item"]["title"], "测试")

    def test_put_domain(self):
        self.login()
        response = self.post('/v1/domain',
                             json=dict(title="测试", depended=1, aggregator=1))
        response = self.put('/v1/domain',
                            json=dict(
                                domain=3,
                                title="测试2",
                                depended=2,
                                aggregator=2,
                            ))
        self.OK(response)
        response = self.get('/v1/domain', query_string=dict(id=3))
        self.OK(response)
        data = response.get_json()
        print(data["item"])
        self.assertEqual(data["item"]["title"], "测试2")

    def test_create_roadmap(self):
        self.login()
        response = self.post('/v1/domain/roadmap',
                             json=dict(title="Python入门方案",
                                       description="适合0基础的孩子",
                                       heads=[2]))
        self.OK(response)
        response = self.get('/v1/domain/roadmap', query_string=dict(roadmap=1))
        data = response.get_json()
        self.assertEqual(data["roadmap"]["title"], "Python入门方案")

    def test_put_roadmap(self):
        self.login()
        response = self.post('/v1/domain/roadmap',
                             json=dict(title="Python入门方案",
                                       description="适合0基础的孩子",
                                       heads=[2]))
        response = self.put('/v1/domain/roadmap',
                            json=dict(title="Python基础", roadmap=1))
        response = self.get('/v1/domain/roadmap', query_string=dict(roadmap=1))
        data = response.get_json()
        self.assertEqual(data["roadmap"]["title"], "Python入门方案")

    def test_learn_roadmap(self):
        self.login()
        response = self.post('/v1/domain/roadmap',
                             json=dict(title="Python入门方案",
                                       description="适合0基础的孩子",
                                       heads=[2]))
        response = self.post('/v1/domain/roadmap/learn',
                             query_string=dict(roadmap=1))
        self.OK(response)
        response = self.delete('/v1/domain/roadmap/learn',
                               query_string=dict(roadmap=1))
        self.OK(response)
