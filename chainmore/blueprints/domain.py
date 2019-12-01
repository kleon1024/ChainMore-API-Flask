# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api, Resource

from ..utils import (response)
from ..models import (Domain, Post)
from ..extensions import db

domain_bp = Blueprint('domain', __name__)
api = Api(domain_bp)


class DomainInstance(Resource):
    def get(self, id):
        domain = Domain.query.get_or_404(id)
        return response("OK", item=domain.serialize())


class Domains(Resource):
    @jwt_required
    def post(self):
        data = request.get_json()
        if data is None:
            return response("EMPTY_BODY", msg="Empty Body")
        title = data.get("title", None)
        description = data.get("description", "")
        bio = data.get("bio", "人正在关注")
        if title is None:
            return response("BAD_REQUEST", msg="No title provided")

        domain = Domain(
            title=title,
            description=description,
            author_id=current_user.id,
            bio=bio,
        )
        db.session.add(domain)
        db.session.commit()

        return response("OK", msg="Domain Created")

    def get(self):
        id = request.args.get('id', '').strip()
        try:
            id = int(id)
        except:
            return response("BAD_REQUEST")
        
        domain = Domain.query.get_or_404(id)
        return response("OK", item=domain.serialize(level=0))

class DomainWatch(Resource):
    @jwt_required
    def post(self, id):
        domain = Domain.query.get_or_404(id)
        current_user.watch(domain)
        return response("OK", msg="Domain watched")

    @jwt_required
    def delete(self, id):
        domain = Domain.query.get_or_404(id)
        current_user.unwatch(domain)
        return response("OK", msg="Domain unwatched")

class DomainPost(Resource):
    def get(self):
        id = request.args.get('id', '').strip()
        try:
            id = int(id)
        except:
            return response("BAD_REQUEST")
        domain = Domain.query.get_or_404(id)
        posts = Post.query.with_parent(domain).order_by(
            Post.timestamp.asc()).all()

        posts = [post.serialize(level=1) for post in posts]
        return response("OK", items=posts)

api.add_resource(DomainInstance, '/<int:id>')
api.add_resource(Domains, '')
api.add_resource(DomainWatch, '/<int:id>/watch')
api.add_resource(DomainPost, '/post')