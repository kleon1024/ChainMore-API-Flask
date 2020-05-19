# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api, Resource

from ..utils import (response)
from ..models import (Sparkle)
from ..extensions import db

sparkle_bp = Blueprint('sparkle', __name__)
api = Api(sparkle_bp)


class SparkleInstance(Resource):
    def get(self, id):
        sparkle = Sparkle.query.get_or_404(id)
        return response("OK", item=sparkle.serialize())

    @jwt_required
    def put(self, id):
        sparkle = Sparkle.query.get_or_404(id)
        if sparkle.author_id != current_user.id:
            return response("BAD_REQUEST")
        data = request.get_json()
        if data is None:
            return response("OK", )
        body = data.get("body", None)

        sparkle.body = body
        db.session.commit()

        return response("OK", msg="Sparkle modified")

    @jwt_required
    def delete(self, id):
        sparkle = Sparkle.query.get_or_404(id)
        if current_user.id == sparkle.author.id:
            sparkle.deleted = True
            db.session.commit()
            return response("OK")
        else:
            return response("BAD_REQUEST")


class SparkleTrendings(Resource):
    def get(self):
        try:
            offset = int(request.args.get('offset', 1))
            limit = int(request.args.get('limit', 5))
        except:
            return response("BAD_REQUEST")
        sparkles = Sparkle.query.filter_by(deleted=0).order_by(
            Sparkle.timestamp.desc()).paginate(offset, limit).items
        sparkles = [sparkle.serialize() for sparkle in sparkles]
        return response("OK", items=sparkles)


class Sparkles(Resource):
    def get(self):
        try:
            id = int(request.args.get('id', '').strip())
        except:
            return response("BAD_REQUEST")

        sparkle = Sparkle.query.get_or_404(id)
        return response("OK", item=sparkle.serialize())

    @jwt_required
    def post(self):
        data = request.get_json()
        if data is None:
            return response("OK", )
        body = data.get("body", None)

        sparkle = Sparkle(author_id=current_user.id, body=body)
        db.session.add(sparkle)
        db.session.commit()

        return response("OK")


class SparkleComment(Resource):
    @jwt_required
    def post(self, id):
        data = request.get_json()
        if data is None:
            return response("EMPTY_BODY", msg="Empty Body")
        replied_id = data.get("reply", None)
        if replied_id is None:
            sparkle = Sparkle.query.get_or_404(id)
        else:
            sparkle = Sparkle.query.get_or_404(int(replied_id))

        body = data.get("body", None)
        comment = Sparkle(body=body, author=current_user, replied=sparkle)

        db.session.add(comment)
        db.session.commit()

        return response("OK", msg="Comment added")

    def get(self, id):
        sparkle = Sparkle.query.get_or_404(id)
        comments = Sparkle.query.with_parent(sparkle).order_by(
            Sparkle.timestamp.desc()).all()
        comments = [comment.serialize(level=1) for comment in comments]

        return response("OK", items=comments)


class SparkleComments(Resource):
    @jwt_required
    def post(self):
        data = request.get_json()
        if data is None:
            return response("EMPTY_BODY", msg="Empty Body")
        body = data.get("body", None)
        if body is None:
            return response("EMPTY_BODY", msg="Empty Body")
        try:
            replied_id = int(data.get("reply", None))
        except:
            return response("BAD_REQUEST")

        sparkle = Sparkle.query.get_or_404(replied_id)

        comment = Sparkle(body=body, author=current_user, replied=sparkle)
        db.session.add(comment)
        db.session.commit()

        return response("OK", item=comment.serialize())

    def get(self):
        try:
            id = int(request.args.get('id', '').strip())
            offset = int(request.args.get('offset', 1))
            limit = int(request.args.get('limit', 20))
        except:
            return response("BAD_REQUEST")
        sparkle = Sparkle.query.get_or_404(id)
        comments = Sparkle.query.with_parent(sparkle).order_by(
            Sparkle.timestamp.desc()).paginate(offset, limit).items
        comments = [comment.serialize(level=1) for comment in comments]

        return response("OK", items=comments)


class SparkleLike(Resource):
    @jwt_required
    def post(self):
        try:
            id = int(request.args.get('id', '').strip())
        except:
            return response("BAD_REQUEST")
        sparkle = Sparkle.query.get_or_404(id)
        current_user.like(sparkle)
        return response("OK", msg="Liked")

    @jwt_required
    def delete(self):
        try:
            id = int(request.args.get('id', '').strip())
        except:
            return response("BAD_REQUEST")
        sparkle = Sparkle.query.get_or_404(id)
        current_user.unlike(sparkle)
        return response("OK", msg="Unliked")


api.add_resource(SparkleInstance, '/<int:id>')
api.add_resource(SparkleComment, '/<int:id>/comment')
api.add_resource(SparkleComments, '/reply')
api.add_resource(SparkleLike, '/like')
api.add_resource(Sparkles, '')
api.add_resource(SparkleTrendings, '/trendings')
