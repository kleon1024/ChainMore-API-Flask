# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api
from flask_restful import Resource as RestfulResource

from ..utils import (response)
from ..models import Resource
from ..extensions import db

resource_bp = Blueprint('post', __name__)
api = Api(resource_bp)


class ResourceInstance(RestfulResource):
    def get(self):
        id = request.args.get('id')
        r = Resource.query.get_or_404(id)
        return response('OK', items=[r.s])

    @jwt_required
    def post(self):
        data = request.get_json()

        kwargs = {}
        kwargs['title'] = data['title']
        kwargs['url'] = data['url']
        kwargs['external'] = data['external']
        kwargs['free'] = data['free']
        kwargs['resource_type_id'] = data['resourceTypeId']
        kwargs['media_type_id'] = data['mediaTypeId']

        r = Resource(**kwargs)

        db.session.add(r)
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def put(self):
        data = request.get_json()

        r = Resource.query.get_or_404(data['id'])
        r.title = data['title']
        r.url = data['url']
        r.external = data['external']
        r.free = data['free']
        r.resource_type_id = data['resourceTypeId']
        r.media_type_id = data['mediaTypeId']

        db.session.commit()


api.add_resource(ResourceInstance, '')
