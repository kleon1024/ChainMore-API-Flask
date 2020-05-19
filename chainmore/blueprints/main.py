# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request, app, current_app, send_from_directory
from flask_restful import Api, Resource
from flask_jwt_extended import (jwt_required, current_user)

from ..utils import (response)
from ..models import (User, Domain)
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
        offset = int(request.args.get('offset', 1))
        limit = int(request.args.get('limit', 10))
        domains = Domain.query.order_by(Domain.timestamp.desc()).paginate(
            offset, limit).items
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
        limit = int(request.args.get('limit', 10))

        domains = Domain.query.whooshee_search(q).paginate(offset, limit).items
        domains = [
            domain.serialize(level=1, user=current_user, depended=True)
            for domain in domains
        ]
        return response("OK", items=domains)


class Update(Resource):
    def get(self):
        version = {}
        version["appStoreUrl"] = ""
        version[
            "apkUrl"] = "https://cm-1301052396.cos.ap-shanghai.myqcloud.com/chainmore_1.0.6_20200113001113.apk"
        version["version"] = "1.0.6"
        version["content"] = "全新升级:\n1.增加标签系统\n2.增加表情回复系统\n3.改进视图\n4.修复若干缺陷"

        return response("OK", item=version)


class Download(Resource):
    def get(self, filename):
        head, tail = os.path.split(filename)
        path = os.path.join(
            current_app.config.get('APK_URL', current_app.root_path), head)
        return send_from_directory(path, filename=tail, as_attachment=True)


class CategoryGroupResource(Resource):
    def get(self):
        category_groups = [
            category_group.serialize()
            for category_group in CategoryGroup.query.all()
        ]
        return response("OK", items=category_groups)


api.add_resource(Search, '/search')
api.add_resource(HotSearch, '/search/hot')
api.add_resource(DomainSearch, '/search/domain')
api.add_resource(Update, '/update')
api.add_resource(Download, '/download/<path:filename>')
api.add_resource(CategoryGroupResource, '/category_groups')
