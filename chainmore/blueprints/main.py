# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request, app, current_app, send_from_directory
from flask_restful import Api, Resource
from flask_jwt_extended import (jwt_required, current_user)

from ..utils import (response)
from ..models import (User, Domain, Classify)
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
        return response("OK", items=[])


class Update(Resource):
    def get(self):
        version = {}
        version["appStoreUrl"] = ""
        version[
            "apkUrl"] = "https://cm-1301052396.cos.ap-shanghai.myqcloud.com/chainmore_1.0.6_20200113001113.apk"
        version["version"] = "1.0.6"
        version["content"] = "全新升级:\n1.增加标签系统\n2.增加表情回复系统\n3.改进视图\n4.修复若干缺陷"

        return response("OK", item=version)


class ResourceType(Resource):
    def get(self):
        types = [c.s for c in Classify.query.all()]
        return response("OK", items=types)


api.add_resource(Search, '/search')
api.add_resource(Update, '/update')
api.add_resource(ResourceType, '/type')
