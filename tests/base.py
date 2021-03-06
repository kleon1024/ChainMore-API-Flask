import unittest

from flask import url_for

import json
from collections import OrderedDict

from flask_restful import Api

from chainmore import create_app
from chainmore.extensions import db
from chainmore.models import User
from chainmore.blueprints import auth

from chainmore.initialize import (admin, root_domain, resource_media_type,
                                  init_role)


class BaseTestCase(unittest.TestCase):

    username = None
    nickname = None
    access_token = None
    refresh_token = None

    def setUp(self):
        app = create_app('testing')
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

        db.create_all()
        init_role()
        admin()
        root_domain()
        resource_media_type()

    def tearDown(self):
        db.drop_all()
        self.context.pop()

    def login(self, username=None, password=None):
        if username is None and password is None:
            username = 'kleon'
            password = 'hellokleon'

        data = self.client.post('/v1/auth/signin',
                                json=dict(username=username,
                                          password=password))
        response = data.get_json()
        if (response is not None):
            self.access_token = response["access_token"]
            self.refresh_token = response["refresh_token"]
            self.username = response["username"]
        return data

    def logout(self):
        return self.delete('/v1/auth/signout')

    def post(self, url, **kwargs):
        kwargs["headers"] = {'Authorization': 'Bearer ' + self.access_token}
        print(kwargs)
        return self.client.post(url, **kwargs)

    def get(self, url, **kwargs):
        kwargs["headers"] = {'Authorization': 'Bearer ' + self.access_token}
        return self.client.get(url, **kwargs)

    def put(self, url, **kwargs):
        kwargs["headers"] = {'Authorization': 'Bearer ' + self.access_token}
        return self.client.put(url, **kwargs)

    def delete(self, url, **kwargs):
        kwargs["headers"] = {'Authorization': 'Bearer ' + self.access_token}
        return self.client.delete(url, **kwargs)

    def OK(self, response):
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        if response.status_code != 200:
            print(response)
        return data

    def ERR(self, response, code=None):
        data = response.get_json()
        if code is not None:
            self.assertEqual(response.status_code, code)
            if response.status_code != code:
                print(response)
        else:
            self.assertNotEqual(response.status_code, 200)

    def format(self, d):
        data = json.dumps(d, indent=2)
        print(data)