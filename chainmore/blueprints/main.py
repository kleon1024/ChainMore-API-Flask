# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request, app, current_app, send_from_directory
from flask_restful import Api, Resource
from flask_jwt_extended import (jwt_required, current_user)

from ..utils import (response)
from ..models import (User, Domain, Post)
import os

main_bp = Blueprint('main', __name__)
api = Api(main_bp)


class Search(Resource):
    def get(self):
        q = request.args.get('query', '').strip()
        if q == '':
            return response("OK", items=[])
        offset = int(request.args.get('offset', 1))
        limit = int(request.args.get('limit', 20))

        type = request.args.get('type', '')
        if type == 'user':
            users = User.query.whooshee_search(q).paginate(offset, limit).items
            users = [user.serialize() for user in users]
            return response("OK", items=users, type='user')
        if type == 'domain':
            domains = Domain.query.whooshee_search(q).paginate(offset,
                                                               limit).items
            domains = [domain.serialize(level=1) for domain in domains]
            return response("OK", items=domains, type='domain')
        if type == 'post':
            posts = Post.query.whooshee_search(q).paginate(offset, limit).items
            posts = [post.serialize() for post in posts]
            return response("OK", items=posts, type='post')
        return response("OK", items=[])


class HotSearch(Resource):
    def get(self):
        domains = Domain.query.order_by(Domain.timestamp.desc()).all()
        domains = domains[20] if len(domains) > 20 else domains
        domains = [domain.title for domain in domains]
        hot = {}
        hot["queries"] = domains
        return response("OK", item=hot)


class DomainSearch(Resource):
    @jwt_required
    def get(self):
        q = request.args.get('query', '').strip()
        if q == '':
            return response("OK", items=[])
        offset = int(request.args.get('offset', 1))
        limit = int(request.args.get('limit', 20))

        domains = Domain.query.whooshee_search(q).paginate(offset, limit).items
        domains = [
            domain.serialize(level=1, user=current_user) for domain in domains
        ]
        return response("OK", items=domains)

class Update(Resource):
    def get(self):
        version = {}
        version["appStoreUrl"] = ""
        version["apkUrl"] = "https://api.kleon.space/v1/download/apk/chainmore_1.0.2_20200108222741.apk"
        version["version"] = "1.0.2"
        version["content"] = "船新版本"

        return response("OK", item=version)

class Download(Resource):
    def get(self, filename):
        head, tail = os.path.split(filename)
        path = os.path.join(current_app.config.get('APK_URL', current_app.root_path), head)
        return send_from_directory(path, filename=tail, as_attachment=True)

api.add_resource(Search, '/search')
api.add_resource(HotSearch, '/search/hot')
api.add_resource(DomainSearch, '/search/domain')
api.add_resource(Update, '/update')
api.add_resource(Download, '/download/<path:filename>')
