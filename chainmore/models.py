# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from datetime import datetime

from werkzeug.security import (generate_password_hash, check_password_hash)

from .extensions import db, whooshee


def to_dict(self):
    return {
        c.name: getattr(self, c.name, None)
        for c in self.__table__.columns
    }


@property
def s(self):
    return self.to_dict()


db.Model.to_dict = to_dict
db.Model.s = s


class MediaType(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Media Type: Article/Video/Audio/Image/VR/AR/offline/book/e-book
    name = db.Column(db.String)
    resources = db.relationship('Resource', back_populates='media_type')


class ResourceType(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Resource Type:
    # Internal: QA/Tutorial/Experience/Project/Record/Example/Quiz/Problem
    # External: Quora/Blog/Podcast
    name = db.Column(db.String)
    resources = db.relationship('Resource', back_populates='resource_type')


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # title
    title = db.Column(db.String)

    # resource router
    url = db.Column(db.String, unique=True)

    # External resource with third-party url, which is considered as reship.
    # If this is declared as False, the resource must be declared as original.
    external = db.Column(db.Boolean, default=True)

    # Free resource, which must respect the copyright.
    free = db.Column(db.Boolean, default=True)

    # Reource Type
    resource_type = db.relationship('ResourceType', back_populates='resources')
    resource_type_id = db.Column(db.Integer, db.ForeignKey('resource_type.id'))

    # Media Type
    media_type = db.relationship('MediaType', back_populates='resources')
    media_type_id = db.Column(db.Integer, db.ForeignKey('media_type.id'))

    referencers = db.relationship('Reference',
                                  back_populates='referenced',
                                  lazy='dynamic',
                                  cascade='all')

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


@whooshee.register_model('description')
class Reference(db.Model):
    referenced_id = db.Column(db.Integer,
                              db.ForeignKey('resource.id'),
                              primary_key=True)
    referencer_id = db.Column(db.Integer,
                              db.ForeignKey('collection.id'),
                              primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    referenced = db.relationship('Resource',
                                 foreign_keys=[referenced_id],
                                 back_populates='referencers',
                                 lazy='joined')
    referencer = db.relationship('Collection',
                                 foreign_keys=[referencer_id],
                                 back_populates='referenceds',
                                 lazy='joined')
    description = db.Column(db.Text)


# Resource Collection
@whooshee.register_model('title', 'intro')
class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    intro = db.Column(db.Text)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='collections')

    # Ref to resource
    referenceds = db.relationship('Reference',
                                  back_populates='referencer',
                                  lazy='dynamic',
                                  cascade='all')

    # A post belongs to one domain, but a resource may belong to many with refs.
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'))
    domain = db.relationship('Domain', back_populates='collections')

    # comments = db.relationship('Comment', back_populates='post', cascade='all')
    collectors = db.relationship('Collect',
                                 back_populates='collected',
                                 lazy='dynamic',
                                 cascade='all')

    deleted = db.Column(db.Boolean, default=False)


class Certify(db.Model):
    certifier_id = db.Column(db.Integer,
                             db.ForeignKey('user.id'),
                             primary_key=True)
    certified_id = db.Column(db.Integer,
                             db.ForeignKey('domain.id'),
                             primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    certifier = db.relationship('User',
                                foreign_keys=[certifier_id],
                                back_populates='certifieds',
                                lazy='joined')
    certified = db.relationship('Domain',
                                foreign_keys=[certified_id],
                                back_populates='certifiers',
                                lazy='joined')


class Aggregate(db.Model):
    ancestor_id = db.Column(db.Integer,
                            db.ForeignKey('domain.id'),
                            primary_key=True)
    descendant_id = db.Column(db.Integer,
                              db.ForeignKey('domain.id'),
                              primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ancestor = db.relationship('Domain',
                               foreign_keys=[ancestor_id],
                               back_populates='aggregateds',
                               lazy='joined')
    descendant = db.relationship('Domain',
                                 foreign_keys=[descendant_id],
                                 back_populates='aggregators',
                                 lazy='joined')
    distance = db.Column(db.Integer)


class Depend(db.Model):
    ancestor_id = db.Column(db.Integer,
                            db.ForeignKey('domain.id'),
                            primary_key=True)
    descendant_id = db.Column(db.Integer,
                              db.ForeignKey('domain.id'),
                              primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ancestor = db.relationship('Domain',
                               foreign_keys=[ancestor_id],
                               back_populates='dependants',
                               lazy='joined')
    descendant = db.relationship('Domain',
                                 foreign_keys=[descendant_id],
                                 back_populates='dependeds',
                                 lazy='joined')
    distance = db.Column(db.Integer)


class Follow(db.Model):
    follower_id = db.Column(db.Integer,
                            db.ForeignKey('user.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer,
                            db.ForeignKey('user.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    follower = db.relationship('User',
                               foreign_keys=[follower_id],
                               back_populates='followings',
                               lazy='joined')
    followed = db.relationship('User',
                               foreign_keys=[followed_id],
                               back_populates='followers',
                               lazy='joined')


# class Vote(db.Model):
#     voter_id = db.Column(db.Integer,
#                          db.ForeignKey('user.id'),
#                          primary_key=True)
#     voted_id = db.Column(db.Integer,
#                          db.ForeignKey('comment.id'),
#                          primary_key=True)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
#     voter = db.relationship('User', back_populates='voteds', lazy='joined')
#     voted = db.relationship('Comment', back_populates='voters', lazy='joined')

# class Like(db.Model):
#     liker_id = db.Column(db.Integer,
#                          db.ForeignKey('user.id'),
#                          primary_key=True)
#     liked_id = db.Column(db.Integer,
#                          db.ForeignKey('sparkle.id'),
#                          primary_key=True)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
#     liker = db.relationship('User', back_populates='likeds', lazy='joined')
#     liked = db.relationship('Sparkle', back_populates='likers', lazy='joined')


class Collect(db.Model):
    collector_id = db.Column(db.Integer,
                             db.ForeignKey('user.id'),
                             primary_key=True)
    collected_id = db.Column(db.Integer,
                             db.ForeignKey('collection.id'),
                             primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    collector = db.relationship('User',
                                back_populates='collecteds',
                                lazy='joined')
    collected = db.relationship('Collection',
                                back_populates='collectors',
                                lazy='joined')


class Watch(db.Model):
    watcher_id = db.Column(db.Integer,
                           db.ForeignKey('user.id'),
                           primary_key=True)
    watched_id = db.Column(db.Integer,
                           db.ForeignKey('domain.id'),
                           primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    watcher = db.relationship('User', back_populates='watcheds', lazy='joined')
    watched = db.relationship('Domain',
                              back_populates='watchers',
                              lazy='joined')


@whooshee.register_model('nickname', 'username')
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    nickname = db.Column(db.String(30), unique=True)
    bio = db.Column(db.String(120))

    root_certified = db.Column(db.Boolean)

    collections = db.relationship('Collection',
                                  back_populates='author',
                                  cascade='all')
    roadmaps = db.relationship('Roadmap',
                               back_populates='creator',
                               cascade='all')
    # emoji_replies = db.relationship('EmojiReply',
    #                 back_populates='user',
    #                 lazy='dynamic',
    #                 cascade='all')
    domains = db.relationship('Domain',
                              back_populates='creator',
                              cascade='all')
    # comments = db.relationship('Comment',
    #                            back_populates='author',
    #                            cascade='all')
    # sparkles = db.relationship('Sparkle',
    #                            back_populates='author',
    #                            cascade='all')
    # likeds = db.relationship('Like', back_populates='liker', cascade='all')
    # voteds = db.relationship('Vote', back_populates='voter', cascade='all')
    certifieds = db.relationship('Certify',
                                 back_populates='certifier',
                                 lazy='dynamic',
                                 cascade='all')
    collecteds = db.relationship('Collect',
                                 back_populates='collector',
                                 lazy='dynamic',
                                 cascade='all')
    watcheds = db.relationship('Watch',
                               back_populates='watcher',
                               lazy='dynamic',
                               cascade='all')
    learnings = db.relationship('Learn',
                                back_populates='learner',
                                lazy='dynamic',
                                cascade='all')
    followings = db.relationship('Follow',
                                 foreign_keys=[Follow.follower_id],
                                 back_populates='follower',
                                 lazy='dynamic',
                                 cascade='all')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                back_populates='followed',
                                lazy='dynamic',
                                cascade='all')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def set_filtered_categories(self, categories):
        print(categories)
        for filter_category in self.filtered_categories:
            if filter_category.category.id not in categories:
                db.session.delete(filter_category)
        for category_id in categories:
            category = Category.query.get_or_404(category_id)
            if not self.has_filtered_category(category):
                filter_category = FilterCategory(category=category, user=self)
                db.session.add(filter_category)

    def has_filtered_category(self, category):
        return self.filtered_categories.with_parent(self).filter_by(
            category_id=category.id).first() is not None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        follow = self.followings.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    def is_following(self, user):
        if user.id is None:  # when follow self, user.id will be None
            return False
        return self.followings.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    def collect(self, post):
        if not self.is_collecting(post):
            collect = Collect(collector=self, collected=post)
            db.session.add(collect)
            db.session.commit()

    def uncollect(self, post):
        collect = Collect.query.with_parent(self).filter_by(
            collected_id=post.id).first()
        if collect:
            db.session.delete(collect)
            db.session.commit()

    def is_collecting(self, post):
        return Collect.query.with_parent(self).filter_by(
            collected_id=post.id).first() is not None

    def like(self, sparkle):
        if not self.is_liking(sparkle):
            like = Like(liker=self, liked=sparkle)
            db.session.add(like)
            db.session.commit()

    def unlike(self, sparkle):
        like = Like.query.with_parent(self).filter_by(
            liked_id=sparkle.id).first()
        if like:
            db.session.delete(like)
            db.session.commit()

    def is_liking(self, sparkle):
        return Like.query.with_parent(self).filter_by(
            liked_id=sparkle.id).first() is not None

    def vote(self, comment):
        if not self.is_voting(comment):
            vote = Vote(voter=self, voted=comment)
            db.session.add(vote)
            db.session.commit()

    def unvote(self, comment):
        vote = Vote.query.with_parent(self).filter_by(
            voted_id=comment.id).first()
        if vote:
            db.session.delete(vote)
            db.session.commit()

    def is_voting(self, comment):
        return Vote.query.with_parent(self).filter_by(
            voted_id=comment.id).first() is not None

    def watch(self, post):
        if not self.is_watching(post):
            watch = Watch(watcher=self, watched=post)
            db.session.add(watch)
            db.session.commit()

    def unwatch(self, post):
        watch = Watch.query.with_parent(self).filter_by(
            watched_id=post.id).first()
        if watch:
            db.session.delete(watch)
            db.session.commit()

    def is_watching(self, post):
        return Watch.query.with_parent(self).filter_by(
            watched_id=post.id).first() is not None

    def learn(self, roadmap):
        if not self.is_learning(roadmap):
            learn = Learn(learner=self, learning=roadmap)
            db.session.add(learn)
            db.session.commit()

    def unlearn(self, roadmap):
        learn = Learn.query.with_parent(self).filter_by(
            learning_id=roadmap.id).first()
        if learn:
            db.session.delete(learn)
            db.session.commit()

    def is_learning(self, roadmap):
        return Learn.query.with_parent(self).filter_by(
            learning_id=roadmap.id).first() is not None


class RoadmapNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    type = db.Column(db.String)

    # Node (domain)
    node_domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'))
    node_domain = db.relationship('Domain', back_populates='nodes')

    # Node (roadmap)
    node_roadmap_id = db.Column(db.Integer, db.ForeignKey('roadmap.id'))
    node_roadmap = db.relationship('Roadmap',
                                   foreign_keys=[node_roadmap_id],
                                   back_populates='node_roadmaps')

    # Node belongs to roadmap
    roadmap_id = db.Column(db.Integer, db.ForeignKey('roadmap.id'))
    roadmap = db.relationship('Roadmap',
                              foreign_keys=[roadmap_id],
                              back_populates='nodes')

    description = db.Column(db.Text)


class Learn(db.Model):
    learner_id = db.Column(db.Integer,
                           db.ForeignKey('user.id'),
                           primary_key=True)
    learning_id = db.Column(db.Integer,
                            db.ForeignKey('roadmap.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    learner = db.relationship('User',
                              back_populates='learnings',
                              lazy='joined')
    learning = db.relationship('Roadmap',
                               back_populates='learners',
                               lazy='joined')

    learned = db.Column(db.Boolean, default=False)


@whooshee.register_model('title', 'intro', 'description')
class Roadmap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    intro = db.Column(db.String)
    description = db.Column(db.Text)
    create_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    modify_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', back_populates='roadmaps')

    learners = db.relationship('Learn',
                               back_populates='learning',
                               lazy='dynamic',
                               cascade='all')

    node_roadmaps = db.relationship('RoadmapNode',
                                    foreign_keys=[RoadmapNode.node_roadmap_id],
                                    back_populates='node_roadmap')

    # Node belongs to roadmap node
    nodes = db.relationship('RoadmapNode',
                            foreign_keys=[RoadmapNode.roadmap_id],
                            back_populates='roadmap')


@whooshee.register_model('title', 'intro')
class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True)
    intro = db.Column(db.String)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship('User', back_populates='domains')
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Node belongs to roadmap node
    nodes = db.relationship('RoadmapNode',
                            back_populates='node_domain',
                            lazy='dynamic',
                            cascade='all')

    watchers = db.relationship('Watch',
                               back_populates='watched',
                               lazy='dynamic',
                               cascade='all')

    collections = db.relationship('Collection',
                                  back_populates='domain',
                                  lazy='dynamic',
                                  cascade='all')

    certifiers = db.relationship('Certify',
                                 back_populates='certified',
                                 lazy='dynamic',
                                 cascade='all')

    aggregateds = db.relationship('Aggregate',
                                  foreign_keys=[Aggregate.ancestor_id],
                                  back_populates='descendant',
                                  lazy='dynamic',
                                  cascade='all')

    aggregators = db.relationship('Aggregate',
                                  foreign_keys=[Aggregate.descendant_id],
                                  back_populates='ancestor',
                                  lazy='dynamic',
                                  cascade='all')

    dependants = db.relationship('Depend',
                                 foreign_keys=[Depend.ancestor_id],
                                 back_populates='descendant',
                                 lazy='dynamic',
                                 cascade='all')

    dependeds = db.relationship('Depend',
                                foreign_keys=[Depend.descendant_id],
                                back_populates='ancestor',
                                lazy='dynamic',
                                cascade='all')

    def certify(self, user):
        if not self.is_certified(user):
            certify = Certify(certifier=user, certified=self)
            db.session.add(certify)
            db.session.commit()

    def uncertify(self, user):
        certify = self.certifiers.filter_by(certifier_id=user.id).first()
        if certify:
            db.session.delete(certify)
            db.session.commit()

    def is_certified(self, user):
        if user.id is None:
            return False
        return self.certifiers.filter_by(
            certifier_id=user.id).first() is not None


# @whooshee.register_model('body')
# class Sparkle(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.String(100))
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
#     deleted = db.Column(db.Boolean, default=False)

#     deleted = db.Column(db.Integer, default=0)

#     author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     replied_id = db.Column(db.Integer, db.ForeignKey('sparkle.id'))

#     author = db.relationship('User', back_populates='sparkles')

#     replies = db.relationship('Sparkle',
#                               back_populates='replied',
#                               lazy='dynamic',
#                               cascade='all')

#     replied = db.relationship('Sparkle',
#                               back_populates='replies',
#                               remote_side=[id])

#     likers = db.relationship('Like', back_populates='liked', cascade='all')
#     like_count = db.Column(db.Integer)

#     def serialize(self, level=0):
#         if self.deleted:
#             return {'id': self.id, 'deleted': self.deleted}

#         result = {}

#         result["id"] = self.id
#         result["body"] = self.body
#         result["deleted"] = self.deleted
#         result["votes"] = self.replies.filter_by(deleted=0).count()
#         result["deleted"] = self.deleted == 1
#         result["timestamp"] = self.timestamp
#         result["author"] = self.author.serialize(level=1)

#         if level == 1:
#             result["replied"] = None
#         elif level == 0:
#             result["replied"] = self.replied.serialize(level=0) if self.replied else None

#         result["replies"] = [reply.serialize(level=1) for reply in self.replies.order_by(
#             Sparkle.timestamp.desc()).paginate(1, 3).items]
#         return result

# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.Text)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
#     deleted = db.Column(db.Boolean, default=False)

#     replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
#     author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

#     voters = db.relationship('Vote', back_populates='voted', cascade='all')
#     voter_count = db.Column(db.Integer)

#     post = db.relationship('Post', back_populates='comments')
#     author = db.relationship('User', back_populates='comments')
#     replies = db.relationship('Comment',
#                               back_populates='replied',
#                               cascade='all')
#     replied = db.relationship('Comment',
#                               back_populates='replies',
#                               remote_side=[id])

#     def serialize(self):
#         if self.deleted:
#             return {
#                 "id": self.id,
#                 "deleted": self.deleted,
#             }

#         return {
#             "id": self.id,
#             "body": self.body,
#             "deleted" : self.deleted,
#             "timestamp": self.timestamp,
#             "replied": self.replied_id,
#             "author": self.author.serialize(level=1),
#             "post": self.post_id,
#             "votes": len(self.voters),
#             "replies": len(self.replies)
#         }
