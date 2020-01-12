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
        try:
            offset = int(request.args.get('offset', 1))
            limit = int(request.args.get('limit', 5))
        except:
            return response("BAD_REQUEST")
        posts = Post.query.order_by(Post.timestamp.desc()).paginate(offset, limit).items
        posts = [post.serialize(level=1) for post in posts]
        return response("OK", items=posts)

class PostUnsign(Resource):
    def get(self):
        try:
            id = int(request.args.get('id', '').strip())
        except:
            return response("BAD_REQUEST")

        post = Post.query.get_or_404(id)
        post = post.serialize(level=0)
        return response("OK", item=post)

class Posts(Resource):
    @jwt_required
    def get(self):
        try:
            id = int(request.args.get('id', '').strip())
        except:
            return response("BAD_REQUEST")

        post = Post.query.get_or_404(id)
        res = post.serialize(level=0, user=current_user)
        res["collected"] = current_user.is_collecting(post)
        return response("OK", item=res)

    @jwt_required
    def put(self):
        data = request.get_json()
        if data is None:
            return response("BAD_REQUEST")
        try:
            post = Post.query.get_or_404(int(data["id"]))
        except:
            return response("BAD_REQUEST")

        if post.author.id != current_user.id:
            return response("UNAUTHORIZED")

        title = data.get("title", None)
        url = data.get("url", None)
        description = data.get("description", None)
        categories = data.get("categories", None)
        
        if title != None:
            post.title = title
        if url != None:
            post.url = url
        if description != None:
            post.description = description
        db.session.commit()
        if categories != None:
            post.add_categories(categories)
        db.session.commit()
        return response("OK", msg="Resource putted")
              
    @jwt_required
    def post(self):
        data = request.get_json()
        if data is None:
            return response("BAD_REQUEST")
        try:
            domain = int(data.get("domain", None))
        except:
            return response("BAD_REQUEST")
        title = data.get("title", None)
        if (title is None):
            return response("BAD_REQUEST")
        url = data.get("url", "")
        description = data.get("description", "")
        categories = data.get("categories", [])

        if (url == "" and description == ""):
            return response("BAD_REQUEST")
        
        domain = Domain.query.get_or_404(domain)

        post = Post(title=title,
                    description=description,
                    url=url,
                    author_id=current_user.id,
                    domain=domain)
        post.add_categories(categories)
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
        try:
            id = int(request.args.get('id', '').strip())
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


class PostCollect(Resource):
    @jwt_required
    def post(self):
        try:
            id = int(request.args.get('id', '').strip())
        except:
            return response("BAD_REQUEST")
        post = Post.query.get_or_404(id)
        current_user.collect(post)
        return response("OK", msg="Collected")

    @jwt_required
    def delete(self):
        try:
            id = int(request.args.get('id', '').strip())
        except:
            return response("BAD_REQUEST")
        post = Post.query.get_or_404(id)
        current_user.uncollect(post)
        return response("OK", msg="Uncollected")


api.add_resource(PostInstance, '/<int:id>')
api.add_resource(PostComment, '/<int:id>/comment')
api.add_resource(PostComments, '/comment')
api.add_resource(PostCollect, '/collect')
api.add_resource(Posts, '')
api.add_resource(PostUnsign, '/unsign')
api.add_resource(PostTrendings, '/trendings')
