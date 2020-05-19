import unittest

from flask import url_for

import json
from collections import OrderedDict

from flask_restful import Api

from chainmore import create_app
from chainmore.extensions import db
from chainmore.models import User
from chainmore.blueprints import auth

from chainmore.initialize import (admin, root_domain, resource_type,
                                  media_type)


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
        admin()
        root_domain()
        resource_type()
        media_type()

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
            self.access_token = response["accessToken"]
            self.refresh_token = response["refreshToken"]
            self.nickname = response["nickname"]
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
        self.assertEqual(data["code"], 20000)
