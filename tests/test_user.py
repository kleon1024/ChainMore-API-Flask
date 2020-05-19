from flask import current_app

from tests.base import BaseTestCase


class UserTestCase(BaseTestCase):
    def test_set_filtered_categories(self):
        self.login()
        response = self.post('/v1/user/kleon', json=dict(categories=[1, 2, 3]))
        self.OK(response)
        response = self.get('/v1/user/kleon')
        self.OK(response)
        data = response.get_json()
        print(data["user"]["filteredCategories"])
        self.assertEqual(len(data["user"]["filteredCategories"]), 3)
        response = self.post('/v1/user/kleon',
                             json=dict(categories=[3, 4, 5, 6]))
        self.OK(response)
        response = self.get('/v1/user/kleon')
        self.OK(response)
        data = response.get_json()
        print(data["user"]["filteredCategories"])
        self.assertEqual(len(data["user"]["filteredCategories"]), 4)

    def test_set_nickname(self):
        self.login()
        response = self.post('/v1/user/kleon', json=dict(nickname="探索者"))
        self.OK(response)
        response = self.get('/v1/user/kleon')
        self.OK(response)
        data = response.get_json()
        self.assertEqual(data["user"]["nickname"], "探索者")
