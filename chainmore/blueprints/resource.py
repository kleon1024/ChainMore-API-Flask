# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api
from flask_restful import Resource as RestfulResource

from ..utils import (response, merge)
from ..models import (
Resource, MediaType, ResourceType, 
Collection, Reference, 
Order, Star, ResourceTag
)
from ..extensions import db
from ..decorators import admin_required, permission_required

resource_bp = Blueprint('post', __name__)
api = Api(resource_bp)


class ResourceStared(RestfulResource):
    @jwt_required
    def get(self):
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 1))
        order = request.args.get('order', Order.time_desc.value)
        if order == Order.time_desc.value:
            order_by = Star.timestamp.desc()
        elif order == Order.time_asc.value:
            order_by = Star.timestamp.asc()
        else:
            order_by = Star.timestamp.desc()
        items = [merge(star.resource.s, star.s) for star in
                 current_user.stars.order_by(order_by).paginate(offset, limit).items]
        return response('OK', items=items)


# class ResourceCollected(RestfulResource):
#     @jwt_required
#     def get(self):
#         items = [collect.collected.s for collect in
#                  current_user.collecteds]
#         return response('OK', items=items)


class ResourceCreated(RestfulResource):
    @jwt_required
    def get(self):
        items = [resource.s for resource in
                 current_user.resources]
        return response('OK', items=items)


class ResourceCollections(RestfulResource):
    def get(self):
        id = request.args.get('id')
        offset = int(request.args.get('offset', 1))
        limit = int(request.args.get('limit', 10))
        order = request.args.get('order', Order.time_desc.value)

        resource = Resource.query.get_or_404(id)

        if order == Order.time_desc.value:
            order_by = Reference.timestamp.desc()
        elif order == Order.time_asc.value:
            order_by = Reference.timestamp.asc()
        else:
            order_by = Reference.timestamp.desc()

        collections = [ref.referencer for ref in resource.referencers.order_by(
            order_by).paginate(offset, limit).items]
        rs = [collection.s for collection in collections]
        return response("OK", items=rs)


class ResourceInstance(RestfulResource):
    def get(self):
        id = request.args.get('id')
        r = Resource.query.get_or_404(id)
        return response('OK', items=[r.s])

    @jwt_required
    def post(self):
        data = request.get_json()

        kwargs = dict(
            title=data['title'],
            url=data['url'],
            external=data['external'],
            free=data['free'],
            resource_type_id=data['resource_type_id'],
            media_type_id=data['media_type_id'],
            author_id=current_user.id,
        )

        r = Resource(**kwargs)

        db.session.add(r)
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def put(self):
        data = request.get_json()

        r = Resource.query.get_or_404(data['id'])
        assert r.author_id == current_user.id

        r.title = data['title']
        r.url = data['url']
        r.external = data['external']
        r.free = data['free']
        r.resource_type_id = data['resource_type_id']
        r.media_type_id = data['media_type_id']

        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        id = request.args.get('id')
        r = Resource.query.get_or_404(id)
        assert r.author_id == current_user.id
        r.deleted = True
        return response('OK', items=[r.s])


class MediaTypeInstance(RestfulResource):
    @jwt_required
    @admin_required
    def get(self):
        id = request.args.get('id', None)
        if id:
            r = MediaType.query.get_or_404(id)
        name = request.args.get('name', None)
        if name:
            r = MediaType.query.filter_by(name=name).first_or_404()
        return response('OK', items=[r.s])

    @jwt_required
    @admin_required
    def post(self):
        data = request.get_json()
        kwargs = {}
        kwargs['name'] = data['title']
        r = MediaType(**kwargs)
        db.session.add(r)
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    @admin_required
    def put(self):
        data = request.get_json()
        r = MediaType.query.get_or_404(data['id'])
        r.name = data['name']
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    @admin_required
    def delete(self):
        id = request.args.get('id')
        r = MediaType.query.get_or_404(id)
        db.session.delete(r)
        return response('OK', items=[r.s])


class ResourceTypeInstance(RestfulResource):
    @jwt_required
    @admin_required
    def get(self):
        id = request.args.get('id', None)
        if id:
            r = ResourceType.query.get_or_404(id)
        name = request.args.get('name', None)
        if name:
            r = ResourceType.query.filter_by(name=name).first_or_404()
        return response('OK', items=[r.s])

    @jwt_required
    @admin_required
    def post(self):
        data = request.get_json()
        kwargs = {}
        kwargs['name'] = data['title']
        r = ResourceType(**kwargs)
        db.session.add(r)
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    @admin_required
    def put(self):
        data = request.get_json()
        r = ResourceType.query.get_or_404(data['id'])
        r.name = data['name']
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    @admin_required
    def delete(self):
        id = request.args.get('id')
        r = ResourceType.query.get_or_404(id)
        db.session.delete(r)
        return response('OK', items=[r.s])


class ResourceExistence(RestfulResource):
    @jwt_required
    def post(self):
        data = request.get_json()
        # TODO check url validation
        r = Resource.query.filter_by(url=data['url']).first()
        rt = []
        if r is not None:
            rt.append(r.s)
        return response('OK', items=rt)


class ResourceStar(RestfulResource):
    @jwt_required
    def get(self):
        id = request.args['id']
        r = Resource.query.get_or_404(id)
        items = []
        if current_user.is_staring(r):
            items.append(r.s)
        return response('OK', items=items)

    @jwt_required
    def post(self):
        data = request.get_json()
        r = Resource.query.get_or_404(data['id'])
        current_user.star(r)
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        id = request.args.get('id')
        r = Resource.query.get_or_404(id)
        current_user.unstar(r)
        return response('OK', items=[r.s])

class ResourceTagItem(RestfulResource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        r = ResourceTag.query.get_or_404(id)
        return response('OK', items=[r.s])

    @jwt_required
    def post(self):
        data = request.get_json()
        kwargs = {}
        kwargs['title'] = data['title']
        kwargs['creator_id'] = current_user.id
        r = ResourceTag(**kwargs)
        db.session.add(r)
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def put(self):
        data = request.get_json()
        r = ResourceTag.query.get_or_404(data['id'])
        if 'title' in data:
            r.title = data['title']
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        id = request.args.get('id')
        r = ResourceTag.query.get_or_404(id)
        assert r.creator_id == current_user.id
        r.remove_all()
        return response('OK', items=[r.s])

class ResourceStick(RestfulResource):
    @jwt_required
    def post(self):
        resource = Resource.query.get_or_404(data['resource'])
        tag = Tag.query.get_or_404(data['tag'])

        assert tag.creator_id == current_user.id
        assert current_user.stars.filter_by(resource_id=resource.id).first() is not None

        resource.add_tag(tag)
        return response('OK', items=[resource.s])

    @jwt_required
    def delete(self):
        resource = request.args.get('resource')
        tag = request.args.get('tag')
        resource = Resource.query.get_or_404(resource)
        tag = Tag.query.get_or_404(tag)

        assert tag.creator_id == current_user.id
        assert current_user.stars.filter_by(resource_id=resource.id).first() is not None

        resource.remove_tag(tag)
        return response('OK', items=[resource.s])


api.add_resource(ResourceInstance, '')
api.add_resource(MediaTypeInstance, '/media_type')
api.add_resource(ResourceTypeInstance, '/resource_type')
api.add_resource(ResourceExistence, '/exist')
api.add_resource(ResourceStar, '/star')
# api.add_resource(ResourceCollected, '/collected')
api.add_resource(ResourceStared, '/stared')
api.add_resource(ResourceCreated, '/created')
api.add_resource(ResourceCollections, '/collections')
api.add_resource(ResourceTagItem, '/tag')
api.add_resource(ResourceStick, '/stick')