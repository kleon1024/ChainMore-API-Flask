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
        results = []
        users = []
        domains = []
        posts = []
        # if category == 'user' or category == 'all':
        #     users = User.query.whooshee_search(q).all()
        #     users = [user.serialize() for user in users]
        #     for user in users:
        #         user["type"] = "user"
        if category == 'domain' or category == 'all':
            domains = Domain.query.whooshee_search(q).all()
            domains = [domain.serialize() for domain in domains]
            for domain in domains:
                domain["type"] = "domain"
        if category == 'post' or category == 'all':
            posts = Post.query.whooshee_search(q).all()
            posts = [post.serialize() for post in posts]
            for post in posts:
                post["type"] = "feed"
        results.extend(users)
        results.extend(domains)
        results.extend(posts)
        return response("OK", items=results)


api.add_resource(Search, '/search')
