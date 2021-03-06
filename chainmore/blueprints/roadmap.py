# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api, Resource

from ..utils import (response)
from ..models import (Roadmap)
from ..extensions import db
from ..decorators import admin_required, permission_required

roadmap_bp = Blueprint('roadmap', __name__)
api = Api(roadmap_bp)


class RoadmapInstance(Resource):
    def get(self):
        id = request.args.get('id')
        r = Roadmap.query.get_or_404(id)
        return response('OK', items=[r.s])

    @jwt_required
    def post(self):
        data = request.get_json()

        kwargs = dict(
            title=data['title'],
            intro=data['intro'],
            description=data['description'],
            creator_id=current_user.id,
        )
        nodes = data['nodes']
        assert (isinstance(nodes, (list, tuple)))

        r = Roadmap(**kwargs)
        db.session.add(r)
        db.session.commit()

        r.update(nodes)
        db.session.commit()

        return response('OK', items=[r.s])

    @jwt_required
    def put(self):
        data = request.get_json()
        r = Roadmap.query.get_or_404(data['id'])
        r.title = data['title']
        r.intro = data['intro']
        r.description = data['description']

        nodes = data['nodes']
        assert (isinstance(nodes, (list, tuple)))

        r.update(nodes)
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        id = request.args.get('id')
        r = Roadmap.query.get_or_404(id)
        assert (r.author_id == current_user.id)
        r.deleting = True
        return response('OK', items=[r.s])


api.add_resource(RoadmapInstance, '')
# api.add_resource(RoadmapWatch, '/watch')
# api.add_resource(RoadmapCollections, '/collections')
# api.add_resource(RoadmapCerification, '/certify')
# api.add_resource(RoadmapHot, '/hot')
# api.add_resource(RoadMapInstance, '/roadmap')
# api.add_resource(RoadMapLearn, '/roadmap/learn')
