# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from datetime import datetime

from werkzeug.security import (generate_password_hash, check_password_hash)

from .extensions import db, whooshee


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(30), unique=True)
    posts = db.relationship('Post', back_populates='category')

    @staticmethod
    def init_category():
        category = Category(category='文章')
        db.session.add(category)
        db.session.commit()


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


class Vote(db.Model):
    voter_id = db.Column(db.Integer,
                         db.ForeignKey('user.id'),
                         primary_key=True)
    voted_id = db.Column(db.Integer,
                         db.ForeignKey('comment.id'),
                         primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    voter = db.relationship('User', back_populates='voteds', lazy='joined')
    voted = db.relationship('Comment', back_populates='voters', lazy='joined')


class Like(db.Model):
    liker_id = db.Column(db.Integer,
                         db.ForeignKey('user.id'),
                         primary_key=True)
    liked_id = db.Column(db.Integer,
                         db.ForeignKey('post.id'),
                         primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    liker = db.relationship('User', back_populates='likeds', lazy='joined')
    liked = db.relationship('Post', back_populates='likers', lazy='joined')


class Collect(db.Model):
    collector_id = db.Column(db.Integer,
                             db.ForeignKey('user.id'),
                             primary_key=True)
    collected_id = db.Column(db.Integer,
                             db.ForeignKey('post.id'),
                             primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    collector = db.relationship('User',
                                back_populates='collections',
                                lazy='joined')
    collected = db.relationship('Post',
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

    posts = db.relationship('Post', back_populates='author', cascade='all')
    domains = db.relationship('Domain',
                              back_populates='creator',
                              cascade='all')
    comments = db.relationship('Comment',
                               back_populates='author',
                               cascade='all')
    likeds = db.relationship('Like', back_populates='liker', cascade='all')
    voteds = db.relationship('Vote', back_populates='voter', cascade='all')
    collections = db.relationship('Collect',
                                  back_populates='collector',
                                  cascade='all')
    watcheds = db.relationship('Watch',
                               back_populates='watcher',
                               cascade='all')
    followings = db.relationship(
        'Follow',
        foreign_keys=[Follow.follower_id],
        back_populates='follower',
        #  lazy='dynamic',
        cascade='all')
    followers = db.relationship(
        'Follow',
        foreign_keys=[Follow.followed_id],
        back_populates='followed',
        # lazy='dynamic',
        cascade='all')

    def serialize(self, level=0):
        result = {"nickname": self.nickname, "username": self.username}

        if level == 1: return result

        result["bio"] = self.bio
        result["likeds"] = len(self.likeds)
        result["watcheds"] = len(self.watcheds)
        result["followings"] = len(self.followings)
        result["followers"] = len(self.followers)
        result["posts"] = len(self.posts)
        result["domains"] = len(self.domains)
        result["comments"] = len(self.comments)

        if level == 0: return result

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

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

    def like(self, post):
        if not self.is_liking(post):
            like = Like(liker=self, liked=post)
            db.session.add(like)
            db.session.commit()

    def unlike(self, post):
        like = Like.query.with_parent(self).filter_by(liked_id=post.id).first()
        if like:
            db.session.delete(like)
            db.session.commit()

    def is_liking(self, post):
        return Like.query.with_parent(self).filter_by(
            liked_id=post.id).first() is not None

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


@whooshee.register_model('title', 'description')
class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), unique=True)
    bio = db.Column(db.String(30))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    creator = db.relationship('User', back_populates='domains')
    watchers = db.relationship('Watch',
                               back_populates='watched',
                               cascade='all')

    posts = db.relationship('Post', back_populates='domain', cascade='all')

    def serialize(self, level=0):
        result = {
            "id": self.id,
            "title": self.title,
            "timestamp": self.timestamp,
            "watchers": len(self.watchers),
            "bio": self.bio,
            "posts": len(self.posts),
            "description" : "",
        }
        if level == 1: return result

        result["description"] = self.description
        if level == 0: return result


@whooshee.register_model('title', 'description')
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    url = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'))

    category = db.relationship('Category', back_populates='posts')
    author = db.relationship('User', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all')
    collectors = db.relationship('Collect',
                                 back_populates='collected',
                                 cascade='all')
    likers = db.relationship('Like', back_populates='liked', cascade='all')
    domain = db.relationship('Domain', back_populates='posts')

    def serialize(self, level=0):

        description_dict = self.description if level==0 else \
            self.description[:45].replace('\n', '')

        return {
            "id": self.id,
            "title": self.title,
            "description": description_dict,
            "url": self.url,
            "timestamp": self.timestamp,
            "author": self.author.serialize(level=1),
            "category": self.category.category,
            "domain": self.domain.serialize(level=1),
            "votes": len(self.likers),
            "comments": len(self.comments),
            "collects": len(self.collectors),
        }


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    flag = db.Column(db.Integer, default=0)

    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    voters = db.relationship('Vote', back_populates='voted', cascade='all')

    post = db.relationship('Post', back_populates='comments')
    author = db.relationship('User', back_populates='comments')
    replies = db.relationship('Comment',
                              back_populates='replied',
                              cascade='all')
    replied = db.relationship('Comment',
                              back_populates='replies',
                              remote_side=[id])

    def serialize(self):
        return {
            "id": self.id,
            "body": self.body,
            "timestamp": self.timestamp,
            "replied": self.replied_id,
            "author": self.author.serialize(level=1),
            "post": self.post_id,
            "votes": len(self.voters),
            "replies": len(self.replies)
        }
