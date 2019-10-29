# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api, Resource

from ..utils import (response)
from ..models import (User)

user_bp = Blueprint('user', __name__)
api = Api(user_bp)


class UserInstance(Resource):
    def get(self, username):
        user = User.query.filter_by(username=username).first_or_404()
        return response("OK", user=user.serialize())


class UserFollow(Resource):
    @jwt_required
    def post(self, username):
        user = User.query.filter_by(username=username).first_or_404()
        current_user.follow(user)
        return response("OK", msg="Followed")

    @jwt_required
    def delete(self, username):
        user = User.query.filter_by(username=username).first_or_404()
        current_user.unfollow(user)
        return response("OK", msg="Unfollowed")


api.add_resource(UserInstance, '/<username>')
api.add_resource(UserFollow, '/<username>/follow')
