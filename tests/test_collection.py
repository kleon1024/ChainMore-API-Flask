from flask import current_app

from tests.base import BaseTestCase


class CollectionTestCase(BaseTestCase):
    def test_create_collection(self):
        response = self.post('/v1/collection',
                        json=dict(title='HTML入门资料',
                        domain_id=1,
                        ))
        self.OK(response)