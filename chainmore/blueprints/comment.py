# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api, Resource

from ..utils import (response)
from ..models import Domain, Comment
from ..extensions import db

comment_bp = Blueprint('comment', __name__)
api = Api(comment_bp)


class CommentInstance(Resource):
    def get(self, id):
        comment = Comment.query.get_or_404(id)
        return response("OK", item=comment.serialize())

    @jwt_required
    def put(self, id):
        comment = Comment.query.get_or_404(id)
        if comment.author_id != current_user.id:
            return response("BAD_REQUEST", msg="Invalid Operation")
        data = request.get_json()
        if data is None:
            return response("EMPTY_BODY", msg="Empty Body")
        body = data.get("comment", None)
        comment.body = body
        db.session.commit()
        return response("OK", msg="Comment modified")

    @jwt_required
    def delete(self, id):
        comment = Comment.query.get_or_404(id)
        db.session.delete(comment)
        db.session.commit()
        return response("OK", msg="Comment deleted")


class CommentVote(Resource):
    @jwt_required
    def post(self, id):
        comment = Comment.query.get_or_404(id)
        current_user.vote(comment)
        return response("OK", msg="Comment voted")

    @jwt_required
    def delete(self, id):
        comment = Comment.query.get_or_404(id)
        current_user.unvote(comment)
        return response("OK", msg="Comment unvoted")


api.add_resource(CommentInstance, '/<int:id>')
api.add_resource(CommentVote, '/<int:id>/vote')
