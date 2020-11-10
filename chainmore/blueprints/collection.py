# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api, Resource

from ..utils import (response)
from ..common import merge
from ..models import (Collection, Domain, Collect, Order)
from ..extensions import db

from ..decorators import admin_required, permission_required

collection_bp = Blueprint('collection', __name__)
api = Api(collection_bp)


class CollectionCollected(Resource):
    @jwt_required
    def get(self):
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 1))
        order = request.args.get('order', Order.time_desc.value)
        if order == Order.time_desc.value:
            order_by = Collect.timestamp.desc()
        elif order == Order.time_asc.value:
            order_by = Collect.timestamp.asc()
        else:
            order_by = Collect.timestamp.desc()
        items = [merge(collected.collected.s, collected.s) for collected in
                 current_user.collecteds.order_by(order_by).paginate(offset, limit).items if collected.collected.deleted == False]
        return response('OK', items=items)


class CollectionCreated(Resource):
    @jwt_required
    def get(self):
        items = [collection.s for collection in
                 current_user.collections]
        return response('OK', items=items)


class CollectionReferenceds(Resource):
    def get(self):
        id = request.args['id']
        collection = Collection.query.get_or_404(id)

        items = [ref.referenced.s for ref in
                 collection.referenceds]
        return response('OK', items=items)


class CollectionCollect(Resource):
    @jwt_required
    def get(self):
        id = request.args['id']
        r = Collection.query.get_or_404(id)
        items = []
        if current_user.is_collecting(r):
            items.append(r.s)
        return response('OK', items=items)

    @jwt_required
    def post(self):
        data = request.get_json()
        r = Collection.query.get_or_404(data['id'])
        current_user.collect(r)
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        id = request.args.get('id')
        r = Collection.query.get_or_404(id)
        current_user.uncollect(r)
        return response('OK', items=[r.s])


class CollectionInstance(Resource):
    def get(self):
        id = request.args.get('id')
        r = Collection.query.get_or_404(id)
        return response('OK', items=[r.s])

    @jwt_required
    def post(self):
        data = request.get_json()

        kwargs = dict(
            title=data['title'],
            description=data['description'],
            author_id=current_user.id,
            domain_id=data['domain_id'],
        )

        # domain = Domain.query.get_or_404(data['domain_id'])
        # for dep in domain.dependeds:
        #     assert dep.ancestor.is_certified(current_user)

        resources = data['resources']

        r = Collection(**kwargs)
        db.session.add(r)
        db.session.commit()

        r.ref(resources)

        db.session.commit()

        r.indicator = '' + r.resource_indicators()

        db.session.commit()

        return response('OK', items=[r.s])

    @jwt_required
    def put(self):
        data = request.get_json()

        r = Collection.query.get_or_404(data['id'])
        assert (r.author_id == current_user.id)
        r.title = data['title']
        r.description = data['description']
        r.domain_id = data['domain_id']
        r.modify_time = datetime.utcnow()

        resources = data['resources']
        r.ref(resources)

        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    @admin_required
    def delete(self):
        id = request.args.get('id')
        r = Collection.query.get_or_404(id)
        r.deleted = True
        r.referenceds.delete(synchronize_session=False)
        r.collectors.delete(synchronize_session=False)
        db.session.commit()
        return response('OK', items=[r.s])


# class PostTrendings(Resource):
#     def get(self):
#         offset = request.args.get('offset', 1)
#         limit = request.args.get('limit', 10)
#         posts = Post.query.order_by(Post.timestamp.desc()).paginate(
#             offset, limit).items
#         posts = [post.s for post in posts]
#         return response("OK", items=posts)

# class Posts(Resource):
#     @jwt_required
#     def get(self):
#         try:
#             id = int(request.args.get('id', '').strip())
#         except:
#             return response("BAD_REQUEST")

#         post = Post.query.get_or_404(id)
#         res = post.serialize(level=0, user=current_user)
#         res["collected"] = current_user.is_collecting(post)
#         return response("OK", item=res)

#     @jwt_required
#     def delete(self):
#         try:
#             id = int(request.args.get('id', '').strip())
#         except:
#             return response("BAD_REQUEST")

#         post = Post.query.get_or_404(id)
#         if current_user.id == post.author.id:
#             post.deleted = True
#             db.session.commit()
#             return response("OK")
#         else:
#             return response("BAD_REQUEST")

#     @jwt_required
#     def put(self):
#         data = request.get_json()
#         if data is None:
#             return response("BAD_REQUEST")
#         try:
#             post = Post.query.get_or_404(int(data["post"]))
#         except:
#             return response("BAD_REQUEST")

#         if post.author.id != current_user.id:
#             return response("UNAUTHORIZED")

#         title = data.get("title", None)
#         url = data.get("url", None)
#         description = data.get("description", None)
#         categories = data.get("categories", None)

#         if title != None:
#             post.title = title
#         if url != None:
#             post.url = url
#         if description != None:
#             post.description = description
#         db.session.commit()
#         if categories != None:
#             post.add_categories(categories)
#         db.session.commit()
#         return response("OK", msg="Resource putted")

#     @jwt_required
#     def post(self):
#         data = request.get_json()
#         if data is None:
#             return response("BAD_REQUEST")
#         try:
#             domain = int(data["domain"])
#             title = data["title"]
#         except:
#             return response("BAD_REQUEST")
#         url = data.get("url", "")
#         description = data.get("description", "")
#         categories = data.get("categories", [])

#         if (url == "" and description == ""):
#             return response("BAD_REQUEST")

#         domain = Domain.query.get_or_404(domain)

#         post = Post(title=title,
#                     description=description,
#                     url=url,
#                     author_id=current_user.id,
#                     domain=domain)
#         post.add_categories(categories)
#         db.session.add(post)
#         db.session.commit()

#         return response("OK", msg="Resource posted")

# class PostComment(Resource):
#     @jwt_required
#     def post(self, id):
#         post = Post.query.get_or_404(id)
#         data = request.get_json()
#         if data is None:
#             return response("EMPTY_BODY", msg="Empty Body")
#         body = data.get("comment", None)
#         comment = Comment(body=body, author=current_user, post=post)
#         replied_id = data.get("reply", None)
#         if replied_id is not None:
#             comment.replied = Comment.query.get_or_404(replied_id)
#         db.session.add(comment)
#         db.session.commit()

#         return response("OK", msg="Comment added")

#     def get(self, id):
#         post = Post.query.get_or_404(id)
#         comments = Comment.query.with_parent(post).order_by(
#             Comment.timestamp.desc()).all()
#         comments = [comment.serialize() for comment in comments]

#         return response("OK", items=comments)

# class PostComments(Resource):
#     @jwt_required
#     def post(self):
#         data = request.get_json()
#         try:
#             post = Post.query.get_or_404(int(data["id"]))
#             body = data["comment"]
#             replied_id = data.get("reply", None)
#         except:
#             return response("BAD_REQUEST")

#         comment = Comment(body=body, author=current_user, post=post)
#         if replied_id is not None:
#             comment.replied = Comment.query.get_or_404(replied_id)
#         db.session.add(comment)
#         db.session.commit()

#         return response("OK", item=comment.serialize())

#     def get(self):
#         id = request.args.get('id', '').strip()
#         try:
#             id = int(id)
#         except:
#             return response("BAD_REQUEST")
#         post = Post.query.get_or_404(id)
#         comments = Comment.query.with_parent(post).order_by(
#             Comment.timestamp.desc()).all()
#         comments = [comment.serialize() for comment in comments]

#         return response("OK", items=comments)

#     @jwt_required
#     def delete(self):
#         id = request.args.get('id', '').strip()
#         try:
#             id = int(id)
#         except:
#             return response("BAD_REQUEST")
#         comment = Comment.query.get_or_404(id)
#         if current_user.id == comment.author.id:
#             comment.deleted = True
#             db.session.commit()
#             return response("OK")
#         else:
#             return response("BAD_REQUEST")

#     @jwt_required
#     def put(self):
#         data = request.get_json()
#         try:
#             comment = Comment.query.get_or_404(int(data["id"]))
#             body = data.get("comment", None)
#             replied_id = data.get("reply", None)
#         except:
#             return response("BAD_REQUEST")

#         if body is not None:
#             comment.body = body
#         if replied_id is not None:
#             comment.replied = Comment.query.get_or_404(replied_id)
#         db.session.commit()

#         return response("OK", item=comment.serialize())

# class PostCollect(Resource):
#     @jwt_required
#     def post(self):
#         try:
#             id = int(request.args.get('id', '').strip())
#         except:
#             return response("BAD_REQUEST")
#         post = Post.query.get_or_404(id)
#         current_user.collect(post)
#         return response("OK", msg="Collected")

#     @jwt_required
#     def delete(self):
#         try:
#             id = int(request.args.get('id', '').strip())
#         except:
#             return response("BAD_REQUEST")
#         post = Post.query.get_or_404(id)
#         current_user.uncollect(post)
#         return response("OK", msg="Uncollected")

# class CommentVote(Resource):
#     @jwt_required
#     def post(self):
#         try:
#             id = int(request.args.get('id', '').strip())
#         except:
#             return response("BAD_REQUEST")
#         comment = Comment.query.get_or_404(id)
#         current_user.vote(comment)
#         return response("OK", msg="Voted")

#     @jwt_required
#     def delete(self):
#         try:
#             id = int(request.args.get('id', '').strip())
#         except:
#             return response("BAD_REQUEST")
#         comment = Comment.query.get_or_404(id)
#         current_user.unvote(comment)
#         return response("OK", msg="Unvoted")

# class EmojiReply(Resource):
#     @jwt_required
#     def post(self):
#         try:
#             post = request.args.get('post')
#             emoji = request.args.get('emoji')
#         except:
#             return response("BAD_REQUEST")
#         post = Post.query.get_or_404(post)
#         emoji = Emoji.query.get_or_404(emoji)
#         current_user.add_emoji_reply(post, emoji)
#         return response("OK")

#     @jwt_required
#     def delete(self):
#         try:
#             post = Post.query.get_or_404(request.args.get('post'))
#             emoji = Emoji.query.get_or_404(request.args.get('emoji'))
#         except:
#             return response("BAD_REQUEST")
#         current_user.delete_emoji_reply(post, emoji)
#         return response("OK")

api.add_resource(CollectionInstance, '')
# api.add_resource(PostComment, '/<int:id>/comment')
# api.add_resource(PostComments, '/comment')
# api.add_resource(PostCollect, '/collect')
# api.add_resource(Posts, '')
# api.add_resource(PostUnsign, '/unsign')
# api.add_resource(PostTrendings, '/trendings')
# api.add_resource(EmojiReply, '/emoji')
api.add_resource(CollectionCollected, '/collected')
api.add_resource(CollectionCreated, '/created')
api.add_resource(CollectionCollect, '/collect')
api.add_resource(CollectionReferenceds, '/referenceds')
