# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api, Resource

from ..utils import (response)
from ..models import (Post, Comment, Category, Domain)
from ..extensions import db

post_bp = Blueprint('post', __name__)
api = Api(post_bp)


class PostInstance(Resource):
    def get(self, id):
        post = Post.query.get_or_404(id)
        return response("OK", item=post.serialize(level=0))

    @jwt_required
    def put(self, id):
        post = Post.query.get_or_404(id)
        if post.author_id != current_user.id:
            return response("BAD_REQUEST", msg="Illegal operation")
        data = request.get_json()
        if data is None:
            return response("OK", )
        title = data.get("title", None)
        url = data.get("url", None)
        description = data.get("description", None)
        category = data.get("category", None)

        post.title = title
        post.description = description
        post.url = url
        post.category_id = Category.query.filter_by(
            category=category).all()[0].id

        db.session.commit()

        return response("OK", msg="Post modified")

    @jwt_required
    def delete(self, id):
        post = Post.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        return response("OK", msg="Post deleted")


class PostTrendings(Resource):
    def get(self):
        posts = Post.query.order_by(Post.timestamp.desc()).all()
        posts = [post.serialize(level=1) for post in posts[0:10]]
        return response("OK", items=posts)


class Posts(Resource):
    def get(self):
        id = request.args.get('id', '').strip()
        try:
            id = int(id)
        except:
            return response("BAD_REQUEST")

        post = Post.query.get_or_404(id)
        return response("OK", item=post.serialize(level=0))

    @jwt_required
    def post(self):
        data = request.get_json()
        if data is None:
            return response("OK", )
        title = data.get("title", None)
        url = data.get("url", None)
        description = data.get("description", None)
        category = data.get("category", None)
        domain = data.get("domain", None)

        domain = Domain.query.get_or_404(int(domain))
        category = Category.query.filter_by(category=category).first_or_404()

        post = Post(title=title,
                    description=description,
                    url=url,
                    category_id=category.id,
                    author_id=current_user.id,
                    domain=domain)
        db.session.add(post)
        db.session.commit()

        return response("OK", msg="Resource posted")


class PostComment(Resource):
    @jwt_required
    def post(self, id):
        post = Post.query.get_or_404(id)
        data = request.get_json()
        if data is None:
            return response("EMPTY_BODY", msg="Empty Body")
        body = data.get("comment", None)
        comment = Comment(body=body, author=current_user, post=post)
        replied_id = data.get("reply", None)
        if replied_id is not None:
            comment.replied = Comment.query.get_or_404(replied_id)
        db.session.add(comment)
        db.session.commit()

        return response("OK", msg="Comment added")

    def get(self, id):
        post = Post.query.get_or_404(id)
        comments = Comment.query.with_parent(post).order_by(
            Comment.timestamp.desc()).all()
        comments = [comment.serialize() for comment in comments]

        return response("OK", items=comments)


class PostComments(Resource):
    @jwt_required
    def post(self):
        id = request.args.get('id', '').strip()
        try:
            id = int(id)
        except:
            return response("BAD_REQUEST")

        post = Post.query.get_or_404(id)
        data = request.get_json()
        if data is None:
            return response("EMPTY_BODY", msg="Empty Body")
        body = data.get("comment", None)
        comment = Comment(body=body, author=current_user, post=post)
        replied_id = data.get("reply", None)
        if replied_id is not None:
            comment.replied = Comment.query.get_or_404(replied_id)
        db.session.add(comment)
        db.session.commit()

        return response("OK", item=comment.serialize())

    def get(self):
        id = request.args.get('id', '').strip()
        try:
            id = int(id)
        except:
            return response("BAD_REQUEST")
        post = Post.query.get_or_404(id)
        comments = Comment.query.with_parent(post).order_by(
            Comment.timestamp.desc()).all()
        comments = [comment.serialize() for comment in comments]

        return response("OK", items=comments)


class PostLike(Resource):
    @jwt_required
    def post(self, id):
        post = Post.query.get_or_404(id)
        current_user.like(post)
        return response("OK", msg="Liked")

    @jwt_required
    def delete(self, id):
        post = Post.query.get_or_404(id)
        current_user.unlike(post)
        return response("OK", msg="Unliked")


class PostCollect(Resource):
    @jwt_required
    def post(self, id):
        post = Post.query.get_or_404(id)
        current_user.collect(post)
        return response("OK", msg="Collected")

    @jwt_required
    def delete(self, id):
        post = Post.query.get_or_404(id)
        current_user.uncollect(post)
        return response("OK", msg="Uncollected")


api.add_resource(PostInstance, '/<int:id>')
api.add_resource(PostComment, '/<int:id>/comment')
api.add_resource(PostComments, '/comment')
api.add_resource(PostLike, '/<int:id>/like')
api.add_resource(PostCollect, '/<int:id>/collect')
api.add_resource(Posts, '')
api.add_resource(PostTrendings, '/trendings')
