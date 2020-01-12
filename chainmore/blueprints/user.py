# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api, Resource

from ..utils import (response)
from ..models import (User)

user_bp = Blueprint('user', __name__)
api = Api(user_bp)


class UserInstanceUnsign(Resource):
    def get(self, username):
        user = User.query.filter_by(username=username).first_or_404()
        return response("OK", user=user.serialize())

class UserInstance(Resource):
    @jwt_required
    def get(self, username):
        user = User.query.filter_by(username=username).first_or_404()
        res = user.serialize()
        res["following"] = current_user.is_following(user)
        return response("OK", user=res)

class UserFollow(Resource):
    @jwt_required
    def post(self):
        try:
            username = request.args.get('username', '')
        except:
            return response("BAD_REQUEST")
        user = User.query.filter_by(username=username).first_or_404()
        current_user.follow(user)
        return response("OK", msg="Followed")

    @jwt_required
    def delete(self):
        try:
            username = request.args.get('username', '').strip()
        except:
            return response("BAD_REQUEST")
        user = User.query.filter_by(username=username).first_or_404()
        current_user.unfollow(user)
        return response("OK", msg="Unfollowed")

class EmojiReply(Resource):
    @jwt_required
    def post(self):
        try:
            post = Post.query.get_or_404(request.args['post'])
            emoji = Emoji.query.get_or_404(request.args['emoji'])
        except:
            return response("BAD_REQUEST")
        current_user.add_emoji_reply(post, emoji)

    @jwt_required
    def delete(self):
        try:
            post = Post.query.get_or_404(request.args['post'])
            emoji = Emoji.query.get_or_404(request.args['emoji'])
        except:
            return response("BAD_REQUEST")
        current_user.delete_emoji_reply(post, emoji)            

api.add_resource(UserInstance, '/<username>')
api.add_resource(UserInstanceUnsign, '/unsign/<username>')
api.add_resource(UserFollow, '/follow')
api.add_resource(EmojiReply, '/emoji')
