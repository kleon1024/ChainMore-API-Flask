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
    classifieds = db.relationship('Classify',
                                  back_populates='classifier',
                                  cascade='all')

    @staticmethod
    def init_category(categories):
        for category in categories:
            c = Category(category=category)
            db.session.add(c)
        db.session.commit()

    def serialize(self):
        result = {}
        result["id"] = self.id
        result["category"] = self.category


class Classify(db.Model):
    classified_id = db.Column(db.Integer,
                              db.ForeignKey('post.id'),
                              primary_key=True)
    classifier_id = db.Column(db.Integer,
                              db.ForeignKey('category.id'),
                              primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    classified = db.relationship('Post',
                                 foreign_keys=[classified_id],
                                 back_populates='classifiers',
                                 lazy='joined')
    classifier = db.relationship('Category',
                                 foreign_keys=[classifier_id],
                                 back_populates='classifieds',
                                 lazy='joined')


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
    aggregator_id = db.Column(db.Integer,
                              db.ForeignKey('domain.id'),
                              primary_key=True)
    aggregated_id = db.Column(db.Integer,
                              db.ForeignKey('domain.id'),
                              primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    aggregator = db.relationship('Domain',
                                 foreign_keys=[aggregator_id],
                                 back_populates='aggregateds',
                                 lazy='joined')
    aggregated = db.relationship('Domain',
                                 foreign_keys=[aggregated_id],
                                 back_populates='aggregators',
                                 lazy='joined')


class Depend(db.Model):
    depended_id = db.Column(db.Integer,
                            db.ForeignKey('domain.id'),
                            primary_key=True)
    dependant_id = db.Column(db.Integer,
                             db.ForeignKey('domain.id'),
                             primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    depended = db.relationship('Domain',
                               foreign_keys=[depended_id],
                               back_populates='dependants',
                               lazy='joined')
    dependant = db.relationship('Domain',
                                foreign_keys=[dependant_id],
                                back_populates='dependeds',
                                lazy='joined')


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

    root_certified = db.Column(db.Boolean)

    posts = db.relationship('Post', back_populates='author', cascade='all')
    domains = db.relationship('Domain',
                              back_populates='creator',
                              cascade='all')
    comments = db.relationship('Comment',
                               back_populates='author',
                               cascade='all')
    likeds = db.relationship('Like', back_populates='liker', cascade='all')
    voteds = db.relationship('Vote', back_populates='voter', cascade='all')
    certifieds = db.relationship('Certify',
                                 back_populates='certifier',
                                 lazy='dynamic',
                                 cascade='all')
    collections = db.relationship('Collect',
                                  back_populates='collector',
                                  cascade='all')
    watcheds = db.relationship('Watch',
                               back_populates='watcher',
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


class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)

    choiceproblem_id = db.Column(db.Integer,
                                 db.ForeignKey('choice_problem.id'))
    choiceproblem = db.relationship('ChoiceProblem', back_populates='choices')

    answerproblem = db.relationship('ChoiceProblem', back_populates='answers')

    def serialize(self):
        result = {}
        result["id"] = self.id
        result["body"] = self.body
        return result


class ChoiceProblem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'))
    rule = db.relationship('Rule', back_populates='choiceproblems')

    choices = db.relationship('Choice',
                              back_populates='choiceproblem',
                              cascade='all')
    answers = db.relationship('Choice',
                              back_populates='answerproblem',
                              cascade='all')

    def add_choices(self, choices, answers):
        for idx, choice in enumerate(choices):
            c = Choice(body=choice, choiceproblem=self)
            if idx in answers:
                c.answerproblem = self
            db.session.add(c)
        db.session.commit()

    def check_answer(self, answers):
        return set(answers) == set([answer.id for answer in self.answers])

    def serialize(self):
        result = {}
        result["id"] = self.id
        result["body"] = self.body
        result["choices"] = [c.serialize() for c in self.choices]
        return result


class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30), unique=True)
    count = db.Column(db.Integer)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'))
    domain = db.relationship('Domain', back_populates='rules')

    choiceproblems = db.relationship('ChoiceProblem',
                                     back_populates='rule',
                                     cascade='all')

    def add_choiceproblem(self, choiceproblems):
        for choiceproblem in choiceproblems:
            choiceproblem.rule = self
        db.session.commit()

    def serialize(self):
        result = {}
        result["id"] = self.id
        result["type"] = self.type
        if self.type == "choiceproblem":
            result["items"] = [cp.serialize() for cp in self.choiceproblems]

        return result


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
                               lazy='dynamic',
                               cascade='all')

    posts = db.relationship('Post',
                            back_populates='domain',
                            lazy='dynamic',
                            cascade='all')
                            
    certifiers = db.relationship('Certify',
                                 back_populates='certified',
                                 lazy='dynamic',
                                 cascade='all')

    rules = db.relationship('Rule',
                            back_populates='domain',
                            lazy='dynamic',
                            cascade='all')

    aggregateds = db.relationship('Aggregate',
                                  foreign_keys=[Aggregate.aggregator_id],
                                  back_populates='aggregator',
                                  lazy='dynamic',
                                  cascade='all')

    aggregators = db.relationship('Aggregate',
                                  foreign_keys=[Aggregate.aggregated_id],
                                  back_populates='aggregated',
                                  lazy='dynamic',
                                  cascade='all')

    dependeds = db.relationship('Depend',
                                foreign_keys=[Depend.dependant_id],
                                back_populates='dependant',
                                lazy='dynamic',
                                cascade='all')

    dependants = db.relationship('Depend',
                                 foreign_keys=[Depend.depended_id],
                                 back_populates='depended',
                                 lazy='dynamic',
                                 cascade='all')

    def serialize(self, level=0, user=None):
        result = {}

        result["id"] = self.id
        result["title"] = self.title
        result["timestamp"] = self.timestamp
        result["watchers"] = len(self.watchers.all())
        result["certifiers"] = len(self.certifiers.all())
        result["bio"] = self.bio
        result["posts"] = len(self.posts.all())
        result["description"] = ""

        if user is not None:
            result['certified'] = False
            if user.certifieds.filter_by(
                    certified_id=self.id).first() is not None:
                result['certified'] = True
            result['depended'] = False
            for depended in self.dependeds.all():
                print(depended)
                if user.certifieds.filter_by(
                        certified_id=depended.depended_id).first() is not None:
                    result['depended'] = True
                else:
                    result['depended'] = False

        if level >= 1: return result

        result["aggregators"] = [
            a.aggregator.serialize(level=1) for a in self.aggregators
        ]
        result["aggregateds"] = [
            a.aggregated.serialize(level=1) for a in self.aggregateds
        ]

        result["dependeds"] = [
            d.depended.serialize(level=1) for d in self.dependeds
        ]
        result["dependants"] = [
            d.dependant.serialize(level=1) for d in self.dependants
        ]

        result["description"] = self.description

        if level >= 0: return result

    def get_rules(self):
        return [rule.serialize() for rule in self.rules]

    def add_dependant(self, domain):
        if not self.is_depending(domain):
            depend = Depend(depended=self, dependant=domain)
            db.session.add(depend)
            db.session.commit()

    def remove_dependant(self, domain):
        depend = self.dependants.filter_by(dependant_id=domain.id).first()
        if depend:
            db.session.delete(depend)
            db.session.commit()

    def is_depending(self, domain):
        if domain.id is None:  # when depend self, domain.id will be None
            return False
        return self.dependants.filter_by(
            dependant_id=domain.id).first() is not None

    def aggregate(self, domain):
        if not self.is_aggregating(domain):
            aggregate = Aggregate(aggregator=self, aggregated=domain)
            db.session.add(aggregate)
            db.session.commit()

    def unaggregate(self, domain):
        aggregate = self.aggregateds.filter_by(aggregated_id=domain.id).first()
        if aggregate:
            db.session.delete(aggregate)
            db.session.commit()

    def is_aggregating(self, domain):
        if domain.id is None:  # when aggregate self, domain.id will be None
            return False
        return self.aggregateds.filter_by(
            aggregated_id=domain.id).first() is not None

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

    classifiers = db.relationship('Classify',
                                  back_populates='classified',
                                  cascade='all')
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
            "categories":
            [category.serialize() for category in self.classifiers],
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
