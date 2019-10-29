# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request
from flask_restful import Api, Resource

from ..utils import (response)
from ..models import (User, Domain, Post)

main_bp = Blueprint('main', __name__)
api = Api(main_bp)


class Search(Resource):
    def get(self):
        q = request.args.get('q', '').strip()
        if q == '':
            return response("OK", items=[])

        category = request.args.get('category', '')
        if category == 'user':
            users = User.query.whooshee_search(q).all()
            users = [user.serialize() for user in users]
            return response("OK", items=users)
        elif category == 'domains':
            domains = Domain.query.whooshee_search(q).all()
            domains = [domain.serialize() for domain in domains]
            return response("OK", items=domains)
        elif category == 'post':
            posts = Post.query.whooshee_search(q).all()
            posts = [post.serialize() for post in posts]
            return response("OK", items=posts)
        return response("OK", items=[])


api.add_resource(Search, '/search')
