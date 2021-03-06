# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from datetime import datetime
from enum import Enum

from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db, whooshee
from .common import merge

import json

DIGEST_LENGTH = 64
COLOR_MAX = int("0xffffff", 16)


def to_dict(self):
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


@property
def s(self):
    return self.to_dict()


db.Model.to_dict = to_dict
db.Model.s = s


class Order(Enum):
    time_desc = "time_desc"
    time_asc = "time_asc"


class UserRoles:
    LOCKED = "Locked"
    USER = "User"
    MODERATOR = "Moderator"
    ADMINISTRATOR = "Administrator"


class Permissions:
    FOLLOW = "FOLLOW"
    COLLECT = "COLLECT"
    COMMENT = "COMMENT"
    UPLOAD = "UPLOAD"
    MODERATE = "MODERATE"
    ADMINISTER = "ADMINISTER"


roles_permissions = db.Table(
    "roles_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("role.id")),
    db.Column("permission_id", db.Integer, db.ForeignKey("permission.id")),
)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    permissions = db.relationship(
        "Permission", secondary=roles_permissions, back_populates="roles"
    )
    users = db.relationship("User", back_populates="role")

    @staticmethod
    def init_role():
        roles_permissions_map = {
            "Locked": ["FOLLOW", "COLLECT"],
            "User": ["FOLLOW", "COLLECT", "COMMENT", "UPLOAD"],
            "Moderator": ["FOLLOW", "COLLECT", "COMMENT", "UPLOAD", "MODERATE"],
            "Administrator": [
                "FOLLOW",
                "COLLECT",
                "COMMENT",
                "UPLOAD",
                "MODERATE",
                "ADMINISTER",
            ],
        }
        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()

    def __repr__(self):
        return "<Role %r>" % self.name


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    roles = db.relationship(
        "Role", secondary=roles_permissions, back_populates="permissions"
    )

    def __repr__(self):
        return "<Permission %r>" % self.name


class Classify(db.Model):
    classified_id = db.Column(
        db.Integer, db.ForeignKey("media_type.id"), primary_key=True
    )
    classifier_id = db.Column(
        db.Integer, db.ForeignKey("resource_type.id"), primary_key=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    classified = db.relationship(
        "MediaType",
        foreign_keys=[classified_id],
        back_populates="classifiers",
        lazy="joined",
    )
    classifier = db.relationship(
        "ResourceType",
        foreign_keys=[classifier_id],
        back_populates="classifieds",
        lazy="joined",
    )
    name_zh_cn = db.Column(db.String)
    name_en_us = db.Column(db.String)

    @property
    def s(self):
        d = self.to_dict()
        d["resource_id"] = self.classifier_id
        d["resource_name"] = self.classifier.name
        d["resource"] = self.classifier.s
        d["media_id"] = self.classified_id
        d["media_name"] = self.classified.name
        d["media"] = self.classified.s
        return d


class MediaType(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Media Type: Article/Video/Audio/Image/VR/AR/offline
    name = db.Column(db.String)
    name_zh_cn = db.Column(db.String)
    name_en_us = db.Column(db.String)
    resources = db.relationship("Resource", back_populates="media_type")

    classifiers = db.relationship(
        "Classify", back_populates="classified", lazy="dynamic", cascade="all"
    )

    def __repr__(self):
        return "<MediaType %r>" % self.name


class ResourceType(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Resource Type:
    # Internal: QA/Tutorial/Experience/Project/Record/Example/Quiz/Problem
    # External: Quora/Blog/Podcast/Course/Book/Music/Movie
    name = db.Column(db.String)
    name_zh_cn = db.Column(db.String)
    name_en_us = db.Column(db.String)
    resources = db.relationship("Resource", back_populates="resource_type")

    classifieds = db.relationship(
        "Classify", back_populates="classifier", lazy="dynamic", cascade="all"
    )

    def __repr__(self):
        return "<ResourceType %r>" % self.name


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String, unique=True)
    reports = db.relationship("Report", back_populates="status")


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reported_id = db.Column(db.Integer, db.ForeignKey("resource.id"), primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reported = db.relationship(
        "Resource",
        foreign_keys=[reported_id],
        back_populates="reporters",
        lazy="joined",
    )
    reporter = db.relationship(
        "User", foreign_keys=[reporter_id], back_populates="reporteds", lazy="joined"
    )
    description = db.Column(db.Text)
    status_id = db.Column(db.Integer, db.ForeignKey("status.id"))
    status = db.relationship("Status", back_populates="reports")


@whooshee.register_model("title")
class ResourceTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    creator = db.relationship("User", back_populates="resource_tags")

    resources = db.relationship(
        "ResourceStick", back_populates="tag", lazy="dynamic", cascade="all"
    )

    def remove_all(self):
        self.resources.delete(synchronize_session=False)
        db.session.delete(self)
        db.session.commit()


class ResourceStick(db.Model):
    resource_id = db.Column(db.Integer, db.ForeignKey("resource.id"), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("resource_tag.id"), primary_key=True)
    resource = db.relationship(
        "Resource", foreign_keys=[resource_id], back_populates="tags", lazy="joined"
    )
    tag = db.relationship(
        "ResourceTag", foreign_keys=[tag_id], back_populates="resources", lazy="joined"
    )


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # title
    title = db.Column(db.String)

    # resource router
    url = db.Column(db.String, unique=True, index=True)

    # External resource with third-party url, which is considered as from web.
    # If this is declared as False, the resource must be declared as original.
    external = db.Column(db.Boolean, default=True)

    # Free resource, which must respect the copyright.
    free = db.Column(db.Boolean, default=True)

    # Reource Type
    resource_type = db.relationship("ResourceType", back_populates="resources")
    resource_type_id = db.Column(db.Integer, db.ForeignKey("resource_type.id"))

    # Media Type
    media_type = db.relationship("MediaType", back_populates="resources")
    media_type_id = db.Column(db.Integer, db.ForeignKey("media_type.id"))

    referencers = db.relationship(
        "Reference", back_populates="referenced", lazy="dynamic", cascade="all"
    )

    reporters = db.relationship(
        "Report", back_populates="reported", lazy="dynamic", cascade="all"
    )

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="resources")

    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow)

    deleted = db.Column(db.Boolean, default=False)

    collectors = db.relationship(
        "Star", back_populates="resource", lazy="dynamic", cascade="all"
    )

    tags = db.relationship(
        "ResourceStick", back_populates="resource", lazy="dynamic", cascade="all"
    )
    trackers = db.relationship(
        "ActionTracker", back_populates="resource", lazy="dynamic", cascade="all"
    )

    @property
    def s(self):
        if self.deleted:
            d = {"id": self.id, "deleted": self.deleted}
        else:
            d = self.to_dict()
            d["media_type"] = self.media_type.name
            d["resource_type"] = self.resource_type.name

        return d

    def ss(self, current_user):
        if self.deleted:
            d = {"id": self.id, "deleted": self.deleted}
        else:
            d = self.to_dict()
            d["media_type"] = self.media_type.name
            d["resource_type"] = self.resource_type.name
            d["tags"] = [t.tag_id for t in self.tags]
        return d

    def has_tag(self, tag):
        return self.tags.filter_by(tag_id=tag.id).first() is not None

    def add_tag(self, tag):
        if not self.has_tag(tag):
            s = ResourceStick(resource_id=self.id, tag_id=tag.id)
            db.session.add(s)
            db.session.commit()

    def remove_tag(self, tag):
        s = self.tags.filter_by(tag_id=tag.id).first()
        if s is not None:
            db.session.delete(s)
            db.session.commit()


class Star(db.Model):
    resource_id = db.Column(db.Integer, db.ForeignKey("resource.id"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    resource = db.relationship(
        "Resource",
        foreign_keys=[resource_id],
        back_populates="collectors",
        lazy="joined",
    )
    user = db.relationship(
        "User", foreign_keys=[user_id], back_populates="stars", lazy="joined"
    )

    @property
    def s(self):
        d = dict(star_time=self.timestamp)
        return d


@whooshee.register_model("description")
class Reference(db.Model):
    referenced_id = db.Column(
        db.Integer, db.ForeignKey("resource.id"), primary_key=True
    )
    referencer_id = db.Column(
        db.Integer, db.ForeignKey("collection.id"), primary_key=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    order = db.Column(db.Integer)
    referenced = db.relationship(
        "Resource",
        foreign_keys=[referenced_id],
        back_populates="referencers",
        lazy="joined",
    )
    referencer = db.relationship(
        "Collection",
        foreign_keys=[referencer_id],
        back_populates="referenceds",
        lazy="joined",
    )
    description = db.Column(db.Text)


class CollectionType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    collections = db.relationship("Collection", back_populates="type")
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


# Resource Collection
@whooshee.register_model("title", "description")
class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.Text, default="")
    indicator = db.Column(db.String, default="")

    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="collections")

    head_id = db.Column(db.Integer, db.ForeignKey("collection.id"))
    head = db.relationship(
        "Collection",
        foreign_keys=[head_id],
        back_populates="subjects",
        remote_side=[id],
    )
    subjects = db.relationship(
        "Collection",
        foreign_keys=[head_id],
        back_populates="head",
        lazy="dynamic",
        cascade="all",
    )

    reply_id = db.Column(db.Integer, db.ForeignKey("collection.id"))
    reply = db.relationship(
        "Collection",
        foreign_keys=[reply_id],
        back_populates="repliers",
        remote_side=[id],
    )
    repliers = db.relationship(
        "Collection",
        foreign_keys=[reply_id],
        back_populates="reply",
        lazy="dynamic",
        cascade="all",
    )

    # Ref to resource
    referenceds = db.relationship(
        "Reference", back_populates="referencer", lazy="dynamic", cascade="all"
    )

    # A post belongs to one domain, but a resource may belong to many with refs.
    domain_id = db.Column(db.Integer, db.ForeignKey("domain.id"))
    domain = db.relationship("Domain", back_populates="collections")

    # comments = db.relationship('Comment', back_populates='post', cascade='all')
    collectors = db.relationship(
        "Collect", back_populates="collected", lazy="dynamic", cascade="all"
    )

    deleted = db.Column(db.Boolean, default=False)

    type_id = db.Column(db.Integer, db.ForeignKey("collection_type.id"))
    type = db.relationship("CollectionType", back_populates="collections")

    trackers = db.relationship(
        "ActionTracker", back_populates="collection", lazy="dynamic", cascade="all"
    )

    def ref(self, resources):
        cur_res = Reference.query.filter_by(referencer_id=self.id).all()

        new_res = []

        for res in cur_res:
            db.session.delete(res)
        for res_id in resources:
            if res_id in new_res:
                continue
            new_res.append(res_id)
            res = Resource.query.get_or_404(res_id)
            ref = Reference(referenced_id=res.id, referencer_id=self.id)
            db.session.add(ref)

    def resource_indicators(self):
        d = {1: "text", 2: "image", 3: "audio", 4: "video"}
        indictor = set()
        for ref in self.referenceds:
            indictor.add(d.get(ref.referenced.media_type_id, ""))
        return "".join(indictor)

    @property
    def s(self):
        if self.deleted:
            d = {}
            d["id"] = self.id
            d["deleted"] = self.deleted
        else:
            d = self.to_dict()
            d["domain_title"] = self.domain.title
        return d


class Certify(db.Model):
    certifier_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    certified_id = db.Column(db.Integer, db.ForeignKey("domain.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    certifier = db.relationship(
        "User", foreign_keys=[certifier_id], back_populates="certifieds", lazy="joined"
    )
    certified = db.relationship(
        "Domain",
        foreign_keys=[certified_id],
        back_populates="certifiers",
        lazy="joined",
    )


class Aggregate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ancestor_id = db.Column(db.Integer, db.ForeignKey("domain.id"))
    descendant_id = db.Column(db.Integer, db.ForeignKey("domain.id"))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    descendant = db.relationship(
        "Domain",
        foreign_keys=[descendant_id],
        back_populates="aggregateds",
        lazy="joined",
    )
    ancestor = db.relationship(
        "Domain",
        foreign_keys=[ancestor_id],
        back_populates="aggregators",
        lazy="joined",
    )
    distance = db.Column(db.Integer)

    @property
    def s(self):
        d = self.to_dict()
        d["ancestor"] = self.ancestor.s
        d["descendant"] = self.descendant.s
        return d

    @property
    def ss(self):
        d = {}
        d["ancestor"] = self.ancestor.ss
        d["descendant"] = self.descendant.ss
        return d


class Depend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ancestor_id = db.Column(db.Integer, db.ForeignKey("domain.id"))
    descendant_id = db.Column(db.Integer, db.ForeignKey("domain.id"))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    descendant = db.relationship(
        "Domain",
        foreign_keys=[descendant_id],
        back_populates="dependants",
        lazy="joined",
    )
    ancestor = db.relationship(
        "Domain", foreign_keys=[ancestor_id], back_populates="dependeds", lazy="joined"
    )
    distance = db.Column(db.Integer)

    @property
    def s(self):
        d = self.to_dict()
        d["ancestor"] = self.ancestor.s
        d["descendant"] = self.descendant.s
        return d

    def ss(self, distance=False):
        d = {}
        d["ancestor"] = self.ancestor.ss
        d["descendant"] = self.descendant.ss
        if distance:
            d["distance"] = self.distance
        return d


class Follow(db.Model):
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    follower = db.relationship(
        "User", foreign_keys=[follower_id], back_populates="followings", lazy="joined"
    )
    followed = db.relationship(
        "User", foreign_keys=[followed_id], back_populates="followers", lazy="joined"
    )


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
    collector_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    collected_id = db.Column(
        db.Integer, db.ForeignKey("collection.id"), primary_key=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    collector = db.relationship("User", back_populates="collecteds", lazy="joined")
    collected = db.relationship(
        "Collection", back_populates="collectors", lazy="joined"
    )

    @property
    def s(self):
        d = dict(collect_time=self.timestamp)
        return d


class Watch(db.Model):
    watcher_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    watched_id = db.Column(db.Integer, db.ForeignKey("domain.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    watcher = db.relationship("User", back_populates="watcheds", lazy="joined")
    watched = db.relationship("Domain", back_populates="watchers", lazy="joined")


class Mark(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    domain_id = db.Column(db.Integer, db.ForeignKey("domain.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", back_populates="markeds", lazy="joined")
    domain = db.relationship("Domain", back_populates="markers", lazy="joined")

    @property
    def s(self):
        d = dict(mark_time=self.timestamp)
        return d


@whooshee.register_model("username")
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, default="")
    email = db.Column(db.String(254), unique=True, index=True, default="")
    phone = db.Column(db.String(30), unique=True, index=True, default="")
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.String(120), default="")

    locked = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    role = db.relationship("Role", back_populates="users")

    avatar_raw = db.Column(db.String)
    avatar_raw_temp = db.Column(db.String)
    avatar_s = db.Column(db.String)
    avatar_m = db.Column(db.String)
    avatar_l = db.Column(db.String)

    receive_comment_notification = db.Column(db.Boolean, default=True)
    receive_follow_notification = db.Column(db.Boolean, default=True)
    receive_collect_notification = db.Column(db.Boolean, default=True)

    collections = db.relationship("Collection", back_populates="author", cascade="all")
    resources = db.relationship("Resource", back_populates="author", cascade="all")
    stars = db.relationship(
        "Star", back_populates="user", lazy="dynamic", cascade="all"
    )
    roadmaps = db.relationship(
        "Roadmap", back_populates="creator", lazy="dynamic", cascade="all"
    )
    # emoji_replies = db.relationship('EmojiReply',
    #                 back_populates='user',
    #                 lazy='dynamic',
    #                 cascade='all')
    domains = db.relationship(
        "Domain", back_populates="creator", lazy="dynamic", cascade="all"
    )
    resource_tags = db.relationship(
        "ResourceTag", back_populates="creator", lazy="dynamic", cascade="all"
    )
    # comments = db.relationship('Comment',
    #                            back_populates='author',
    #                            cascade='all')
    # sparkles = db.relationship('Sparkle',
    #                            back_populates='author',
    #                            cascade='all')
    # likeds = db.relationship('Like', back_populates='liker', cascade='all')
    # voteds = db.relationship('Vote', back_populates='voter', cascade='all')
    certifieds = db.relationship(
        "Certify", back_populates="certifier", lazy="dynamic", cascade="all"
    )
    collecteds = db.relationship(
        "Collect", back_populates="collector", lazy="dynamic", cascade="all"
    )
    watcheds = db.relationship(
        "Watch", back_populates="watcher", lazy="dynamic", cascade="all"
    )
    markeds = db.relationship(
        "Mark", back_populates="user", lazy="dynamic", cascade="all"
    )
    reporteds = db.relationship(
        "Report", back_populates="reporter", lazy="dynamic", cascade="all"
    )

    target_domains = db.relationship(
        "TargetDomain", back_populates="learner", lazy="dynamic", cascade="all"
    )

    target_roadmaps = db.relationship(
        "TargetRoadmap", back_populates="learner", lazy="dynamic", cascade="all"
    )

    followings = db.relationship(
        "Follow",
        foreign_keys=[Follow.follower_id],
        back_populates="follower",
        lazy="dynamic",
        cascade="all",
    )

    followers = db.relationship(
        "Follow",
        foreign_keys=[Follow.followed_id],
        back_populates="followed",
        lazy="dynamic",
        cascade="all",
    )

    finished_groups = db.relationship(
        "FinishCertificationGroup", back_populates="user", lazy="dynamic", cascade="all"
    )

    groups = db.relationship(
        "GroupMember", back_populates="user", lazy="dynamic", cascade="all"
    )

    vip = db.Column(db.Integer, default=0)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def set_role(self, role="User"):
        self.role = Role.query.filter_by(name=role).first_or_404()
        db.session.commit()

    def __repr__(self):
        return "<User %r>" % self.username

    @property
    def is_vip(self):
        return self.vip > 0

    @property
    def s(self):
        d = self.to_dict()
        d.pop("password_hash")
        d.pop("role_id")
        d["is_admin"] = self.is_admin
        d["is_active"] = self.is_active
        return d

    @property
    def short(self):
        d = {}
        d["username"] = self.username
        return d

    # def set_filtered_categories(self, categories):
    #     print(categories)
    #     for filter_category in self.filtered_categories:
    #         if filter_category.category.id not in categories:
    #             db.session.delete(filter_category)
    #     for category_id in categories:
    #         category = Category.query.get_or_404(category_id)
    #         if not self.has_filtered_category(category):
    #             filter_category = FilterCategory(category=category, user=self)
    #             db.session.add(filter_category)

    # def has_filtered_category(self, category):
    #     return self.filtered_categories.with_parent(self).filter_by(
    #         category_id=category.id).first() is not None

    def generate_avatar(self):
        pass

    @property
    def is_admin(self):
        return self.role.name == UserRoles.ADMINISTRATOR

    def can(self, permission_name):
        permission = Permission.query.filter_by(name=permission_name).first()
        return (
            permission is not None
            and self.role is not None
            and permission in self.role.permissions
        )

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
        return self.followings.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def follow_self_all(self):
        for user in User.query.all():
            user.follow(self)

    @property
    def is_active(self):
        return self.active

    def lock(self):
        self.locked = True
        self.role = Role.query.filter_by(name=UserRoles.LOCKED).first()
        db.session.commit()

    def unlock(self):
        self.locked = False
        self.role = Role.query.filter_by(name=UserRoles.USER).first()
        db.session.commit()

    def block(self):
        self.active = False
        db.session.commit()

    def unblock(self):
        self.active = True
        db.session.commit()

    def collect(self, collection):
        if not self.is_collecting(collection):
            collect = Collect(collector=self, collected=collection)
            db.session.add(collect)
            db.session.commit()

    def uncollect(self, collection):
        collect = (
            Collect.query.with_parent(self)
            .filter_by(collected_id=collection.id)
            .first()
        )
        if collect:
            db.session.delete(collect)
            db.session.commit()

    def is_collecting(self, collection):
        return (
            Collect.query.with_parent(self)
            .filter_by(collected_id=collection.id)
            .first()
            is not None
        )

    def star(self, resource):
        if not self.is_staring(resource):
            star = Star(user_id=self.id, resource_id=resource.id)
            db.session.add(star)
            db.session.commit()

    def unstar(self, resource):
        star = Star.query.with_parent(self).filter_by(resource_id=resource.id).first()
        if star:
            db.session.delete(star)
            db.session.commit()

    def is_staring(self, resource):
        return (
            Star.query.with_parent(self).filter_by(resource_id=resource.id).first()
            is not None
        )

    def mark(self, domain):
        if not self.is_marking(domain):
            mark = Mark(user_id=self.id, domain_id=domain.id)
            db.session.add(mark)
            db.session.commit()

    def unmark(self, domain):
        mark = Mark.query.with_parent(self).filter_by(domain_id=domain.id).first()
        if mark:
            db.session.delete(mark)
            db.session.commit()

    def is_marking(self, domain):
        return (
            Mark.query.with_parent(self).filter_by(domain_id=domain.id).first()
            is not None
        )

    #     def like(self, sparkle):
    #         if not self.is_liking(sparkle):
    #             like = Like(liker=self, liked=sparkle)
    #             db.session.add(like)
    #             db.session.commit()

    #     def unlike(self, sparkle):
    #         like = Like.query.with_parent(self).filter_by(
    #             liked_id=sparkle.id).first()
    #         if like:
    #             db.session.delete(like)
    #             db.session.commit()

    def is_liking(self, sparkle):
        return (
            Like.query.with_parent(self).filter_by(liked_id=sparkle.id).first()
            is not None
        )

    #     def vote(self, comment):
    #         if not self.is_voting(comment):
    #             vote = Vote(voter=self, voted=comment)
    #             db.session.add(vote)
    #             db.session.commit()

    #     def unvote(self, comment):
    #         vote = Vote.query.with_parent(self).filter_by(
    #             voted_id=comment.id).first()
    #         if vote:
    #             db.session.delete(vote)
    #             db.session.commit()

    #     def is_voting(self, comment):
    #         return Vote.query.with_parent(self).filter_by(
    #             voted_id=comment.id).first() is not None

    #     def watch(self, post):
    #         if not self.is_watching(post):
    #             watch = Watch(watcher=self, watched=post)
    #             db.session.add(watch)
    #             db.session.commit()

    #     def unwatch(self, post):
    #         watch = Watch.query.with_parent(self).filter_by(
    #             watched_id=post.id).first()
    #         if watch:
    #             db.session.delete(watch)
    #             db.session.commit()

    #     def is_watching(self, post):
    #         return Watch.query.with_parent(self).filter_by(
    #             watched_id=post.id).first() is not None

    def learn_roadmap(self, roadmap):
        roadmap = Roadmap.query.get_or_404(roadmap)
        if not self.is_learning_roadmap(roadmap):
            learn = TargetRoadmap(learner=self, learning=roadmap)
            db.session.add(learn)
            db.session.commit()

    def unlearn_roadmap(self, roadmap):
        roadmap = Roadmap.query.get_or_404(roadmap)
        learn = (
            TargetRoadmap.query.with_parent(self)
            .filter_by(learning_id=roadmap.id)
            .first()
        )
        if learn:
            db.session.delete(learn)
            db.session.commit()

    def is_learning_roadmap(self, roadmap):
        return (
            TargetRoadmap.query.with_parent(self)
            .filter_by(learning_id=roadmap.id)
            .first()
            is not None
        )

    def learn_domain(self, domain):
        if not self.is_learning_domain(domain):
            learn = TargetDomain(learner=self, learning=domain)
            db.session.add(learn)
            db.session.commit()

    def unlearn_domain(self, domain):
        learn = (
            TargetDomain.query.with_parent(self)
            .filter_by(learning_id=domain.id)
            .first()
        )
        if learn:
            db.session.delete(learn)
            db.session.commit()

    def is_learning_domain(self, domain):
        return (
            TargetDomain.query.with_parent(self)
            .filter_by(learning_id=domain.id)
            .first()
            is not None
        )


class RoadmapNode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer, default=0)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    type = db.Column(db.String)

    # Node (domain)
    node_domain_id = db.Column(db.Integer, db.ForeignKey("domain.id"))
    node_domain = db.relationship("Domain", back_populates="nodes")

    # Node (roadmap)
    node_roadmap_id = db.Column(db.Integer, db.ForeignKey("roadmap.id"))
    node_roadmap = db.relationship(
        "Roadmap", foreign_keys=[node_roadmap_id], back_populates="node_roadmaps"
    )

    # Node belongs to roadmap
    roadmap_id = db.Column(db.Integer, db.ForeignKey("roadmap.id"))
    roadmap = db.relationship(
        "Roadmap", foreign_keys=[roadmap_id], back_populates="nodes"
    )

    description = db.Column(db.Text)

    @property
    def s(self):
        d = self.to_dict()
        if self.node_roadmap:
            d["nodeRoadmap"] = self.node_roadmap.s
        if self.node_domain:
            d["nodeDomain"] = self.node_domain.s

        return d


class TargetRoadmap(db.Model):
    learner_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    learning_id = db.Column(db.Integer, db.ForeignKey("roadmap.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    learner = db.relationship("User", back_populates="target_roadmaps", lazy="joined")
    learning = db.relationship("Roadmap", back_populates="learners", lazy="joined")
    learned = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)


class TargetDomain(db.Model):
    learner_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    learning_id = db.Column(db.Integer, db.ForeignKey("domain.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    learner = db.relationship("User", back_populates="target_domains", lazy="joined")
    learning = db.relationship("Domain", back_populates="learners", lazy="joined")
    learned = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)


@whooshee.register_model("title", "intro", "description")
class Roadmap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    intro = db.Column(db.String)
    description = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow)

    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    creator = db.relationship("User", back_populates="roadmaps")

    learners = db.relationship(
        "TargetRoadmap", back_populates="learning", lazy="dynamic", cascade="all"
    )

    node_roadmaps = db.relationship(
        "RoadmapNode",
        foreign_keys=[RoadmapNode.node_roadmap_id],
        back_populates="node_roadmap",
    )

    # Node belongs to roadmap node
    nodes = db.relationship(
        "RoadmapNode", foreign_keys=[RoadmapNode.roadmap_id], back_populates="roadmap"
    )

    def update(self, nodes):
        for node in self.nodes:
            db.session.delete(node)

        new_nodes = []

        for node in nodes:
            key = str(node["type"]) + str(node["id"])
            if key in new_nodes:
                continue

            new_nodes.append(key)
            kwargs = dict(
                type=node["type"], roadmap_id=self.id, description=node["description"]
            )
            if node["type"] == "domain":
                domain = Domain.query.get_or_404(node["id"])
                rn = RoadmapNode(node_domain_id=domain.id, **kwargs)
            elif node["type"] == "roadmap":
                roadmap = Roadmap.query.get_or_404(node["id"])
                rn = RoadmapNode(node_roadmap_id=roadmap.id, **kwargs)
            db.session.add(rn)

    @property
    def s(self):
        d = self.to_dict()
        for node in self.nodes:
            print(node)
        d["nodes"] = [node.s for node in self.nodes]
        return d


@whooshee.register_model("title", "intro")
class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, index=True)
    intro = db.Column(db.String, default="")

    deleting = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)

    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship("User", back_populates="domains")
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    learners = db.relationship(
        "TargetDomain", back_populates="learning", lazy="dynamic", cascade="all"
    )

    # Node belongs to roadmap node
    nodes = db.relationship(
        "RoadmapNode", back_populates="node_domain", lazy="dynamic", cascade="all"
    )

    watchers = db.relationship(
        "Watch", back_populates="watched", lazy="dynamic", cascade="all"
    )

    markers = db.relationship(
        "Mark", back_populates="domain", lazy="dynamic", cascade="all"
    )

    collections = db.relationship(
        "Collection", back_populates="domain", lazy="dynamic", cascade="all"
    )

    certifiers = db.relationship(
        "Certify", back_populates="certified", lazy="dynamic", cascade="all"
    )

    aggregateds = db.relationship(
        "Aggregate",
        foreign_keys=[Aggregate.ancestor_id],
        back_populates="descendant",
        lazy="dynamic",
        cascade="all",
    )

    aggregators = db.relationship(
        "Aggregate",
        foreign_keys=[Aggregate.descendant_id],
        back_populates="ancestor",
        lazy="dynamic",
        cascade="all",
    )

    dependants = db.relationship(
        "Depend",
        foreign_keys=[Depend.ancestor_id],
        back_populates="descendant",
        lazy="dynamic",
        cascade="all",
    )

    dependeds = db.relationship(
        "Depend",
        foreign_keys=[Depend.descendant_id],
        back_populates="ancestor",
        lazy="dynamic",
        cascade="all",
    )

    certification_groups = db.relationship(
        "CertificationGroup", back_populates="domain", lazy="dynamic", cascade="all"
    )

    trackers = db.relationship(
        "ActionTracker", back_populates="domain", lazy="dynamic", cascade="all"
    )

    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    group = db.relationship("Group", back_populates="domain")

    def certify(self, user):
        if not self.is_certified(user):
            certify = Certify(certifier_id=user.id, certified_id=self.id)
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
        return self.certifiers.filter_by(certifier_id=user.id).first() is not None

    @property
    def ss(self):
        d = {}
        d["id"] = self.id
        d["title"] = self.title
        return d


class FinishCertificationGroup(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    certification_group_id = db.Column(
        db.Integer, db.ForeignKey("certification_group.id"), primary_key=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship(
        "User", foreign_keys=[user_id], back_populates="finished_groups", lazy="joined"
    )
    certification_group = db.relationship(
        "CertificationGroup",
        foreign_keys=[certification_group_id],
        back_populates="finished_users",
        lazy="joined",
    )


class CertificationGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    intro = db.Column(db.String, default="")
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)

    domain_id = db.Column(db.Integer, db.ForeignKey("domain.id"))
    domain = db.relationship("Domain", back_populates="certification_groups")

    certifications = db.relationship(
        "Certification",
        back_populates="certification_group",
        lazy="dynamic",
        cascade="all",
    )

    finished_users = db.relationship(
        "FinishCertificationGroup",
        back_populates="certification_group",
        lazy="dynamic",
        cascade="all",
    )

    def finish(self, user):
        if not self.is_finished(user):
            finish = FinishCertificationGroup(
                user_id=user.id, certification_group_id=self.id
            )
            db.session.add(finish)
            db.session.commit()

    def unfinish(self, user):
        finish = self.finished_users.filter_by(user_id=user.id).first()
        if finish:
            db.session.delete(finish)
            db.session.commit()

    def is_finished(self, user):
        if user.id is None:
            return False
        return self.finished_users.filter_by(user_id=user.id).first() is not None


class MultipleChoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)

    choice_problem_id = db.Column(
        db.Integer, db.ForeignKey("multiple_choice_problem.id")
    )
    choice_problem = db.relationship(
        "MultipleChoiceProblem",
        foreign_keys=[choice_problem_id],
        back_populates="choices",
    )

    answer_problem_id = db.Column(
        db.Integer, db.ForeignKey("multiple_choice_problem.id")
    )
    answer_problem = db.relationship(
        "MultipleChoiceProblem",
        foreign_keys=[answer_problem_id],
        back_populates="answers",
    )

    @property
    def s(self):
        d = dict(id=self.id, text=self.text,)
        return d


class MultipleChoiceProblemType(Enum):
    SINGLE_ANSWER = "single_answer"
    MULTIPLE_ANSWER = "multiple_answer"
    ANY_ANSWER = "any_answer"


class MultipleChoiceProblem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, default="")

    type = db.Column(db.String, default=MultipleChoiceProblemType.ANY_ANSWER.value)

    choices = db.relationship(
        "MultipleChoice",
        foreign_keys=[MultipleChoice.choice_problem_id],
        back_populates="choice_problem",
        lazy="dynamic",
        cascade="all",
    )

    answers = db.relationship(
        "MultipleChoice",
        foreign_keys=[MultipleChoice.answer_problem_id],
        back_populates="answer_problem",
        lazy="dynamic",
        cascade="all",
    )

    certification = db.relationship(
        "Certification", back_populates="mcp", uselist=False
    )

    def check_answer(self, answers):
        checked_answers = []
        for answer_id in answers:
            answer = MultipleChoice.query.get_or_404(answer_id)
            checked_answers.append(answer)

        assert set([a.id for a in checked_answers]) == set([a.id for a in self.answers])

    @property
    def s(self):
        d = self.to_dict()
        d["choices"] = [c.s for c in self.choices]
        return d

    @property
    def ss(self):
        d = self.to_dict()
        d["choices"] = [c.s for c in self.choices]
        d["answers"] = [c.id for c in self.answers]
        return d


class CertificationType(Enum):
    MCP = "multiple_choice_problem"


class Certification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    digest = db.Column(db.String, default="")
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)

    type = db.Column(db.String, default=CertificationType.MCP.value)

    mcp_id = db.Column(db.Integer, db.ForeignKey("multiple_choice_problem.id"))
    mcp = db.relationship("MultipleChoiceProblem", back_populates="certification")

    certification_group_id = db.Column(
        db.Integer, db.ForeignKey("certification_group.id")
    )
    certification_group = db.relationship(
        "CertificationGroup", back_populates="certifications"
    )

    def check_answer(self, answer):
        assert self.type == answer["type"]
        if self.type == CertificationType.MCP.value:
            self.mcp.check_answer(answer["answers"])

    @property
    def s(self):
        d = self.to_dict()
        if self.type == CertificationType.MCP.value:
            d["mcp"] = self.mcp.s
        return d

    @property
    def ss(self):
        d = self.to_dict()
        if self.type == CertificationType.MCP.value:
            d["mcp"] = self.mcp.ss
        return d


class GroupMember(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"), primary_key=True)
    user_only = db.Column(db.Integer, default=0)  # Boolean
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship(
        "User", foreign_keys=[user_id], back_populates="groups", lazy="joined"
    )
    group = db.relationship(
        "Group", foreign_keys=[group_id], back_populates="members", lazy="joined"
    )


class GroupPermission(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    permission = db.Column(db.String, default=GroupPermission.PUBLIC.value)

    title = db.Column(db.String, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow)
    deleted = db.Column(db.Integer, default=0)  # Boolean
    locked = db.Column(db.Integer, default=0)  # Boolean

    actions = db.relationship(
        "Action", back_populates="group", lazy="dynamic", cascade="all"
    )

    clusters = db.relationship(
        "AttributeCluster", back_populates="group", lazy="dynamic", cascade="all"
    )

    members = db.relationship(
        "GroupMember", back_populates="group", lazy="dynamic", cascade="all"
    )

    domain = db.relationship("Domain", back_populates="group", uselist=False)

    def is_member(self, user):
        if self.domain is not None:
            return self.domain.is_certified(current_user)
        return self.members.filter_by(user_id=user.id).first() is not None

    def add_member(self, user, user_only=0):
        if not self.is_member(user):
            r = GroupMember(group_id=self.id, user_id=user.id, user_only=user_only)
            db.session.add(r)
            db.session.commit()

    def remove_member(self, user):
        r = self.members.filter_by(user_id=user.id).first()
        if r is not None:
            db.session.remove(r)
            db.session.commit()

    def add_attr(self, attr):
        if not self.has_attr(attr):
            r = AttributeCluster(attr_id=attr.id, group_id=self.id)
            db.session.add(r)
            db.session.commit()

    def has_attr(self, attr):
        return self.clusters.filter_by(attr_id=attr.id).first() is not None

    def remove_attr(self, attr):
        r = self.clusters.filter_by(attr_id=attr.id).first()
        if r is not None:
            db.session.remove(r)
            db.session.commit()


class TrackerType(Enum):
    DOMAIN = "domain"
    COLLECTION = "collection"
    RESOURCE = "resource"


class ActionTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, default=TrackerType.DOMAIN.value)
    action_id = db.Column(db.Integer, db.ForeignKey("action.id"))
    action = db.relationship("Action", back_populates="tracker")

    domain_id = db.Column(db.Integer, db.ForeignKey("domain.id"))
    domain = db.relationship("Domain", back_populates="trackers")

    collection_id = db.Column(db.Integer, db.ForeignKey("collection.id"))
    collection = db.relationship("Collection", back_populates="trackers")

    resource_id = db.Column(db.Integer, db.ForeignKey("resource.id"))
    resource = db.relationship("Resource", back_populates="trackers")


class RemindCycleType(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class ActionReminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    action_id = db.Column(db.Integer, db.ForeignKey("action.id"))
    action = db.relationship("Action", back_populates="reminder")

    remind_time = db.Column(db.DateTime, default=datetime.utcnow)
    remind_cycle = db.Column(db.String, default=RemindCycleType.DAY.value)
    remind_freq = db.Column(db.Integer, default=0)


class AttributeBelong(db.Model):
    action_id = db.Column(db.Integer, db.ForeignKey("action.id"), primary_key=True)
    attr_id = db.Column(
        db.Integer, db.ForeignKey("action_attribute.id"), primary_key=True
    )
    order = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    action = db.relationship(
        "Action", foreign_keys=[action_id], back_populates="attrs", lazy="joined"
    )
    attr = db.relationship(
        "ActionAttribute",
        foreign_keys=[attr_id],
        back_populates="actions",
        lazy="joined",
    )


class AggAction(db.Model):
    ancestor_id = db.Column(db.Integer, db.ForeignKey("action.id"), primary_key=True)
    descendant_id = db.Column(db.Integer, db.ForeignKey("action.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    descendant = db.relationship(
        "Action",
        foreign_keys=[descendant_id],
        back_populates="aggregateds",
        lazy="joined",
    )
    ancestor = db.relationship(
        "Action",
        foreign_keys=[ancestor_id],
        back_populates="aggregators",
        lazy="joined",
    )
    distance = db.Column(db.Integer)


class DepAction(db.Model):
    ancestor_id = db.Column(db.Integer, db.ForeignKey("action.id"), primary_key=True)
    descendant_id = db.Column(db.Integer, db.ForeignKey("action.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    descendant = db.relationship(
        "Action",
        foreign_keys=[descendant_id],
        back_populates="dependants",
        lazy="joined",
    )
    ancestor = db.relationship(
        "Action", foreign_keys=[ancestor_id], back_populates="dependeds", lazy="joined",
    )
    distance = db.Column(db.Integer)


class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)

    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow)
    finish_time = db.Column(db.DateTime, default=datetime.utcnow)
    finished = db.Column(db.Integer, default=0)  # Boolean

    reminder = db.relationship("ActionReminder", back_populates="action", uselist=False)
    tracker = db.relationship("ActionTracker", back_populates="action", uselist=False)

    aggregators = db.relationship(
        "AggAction",
        foreign_keys=[AggAction.descendant_id],
        back_populates="ancestor",
        lazy="dynamic",
        cascade="all",
    )

    aggregateds = db.relationship(
        "AggAction",
        foreign_keys=[AggAction.ancestor_id],
        back_populates="descendant",
        lazy="dynamic",
        cascade="all",
    )

    dependeds = db.relationship(
        "DepAction",
        foreign_keys=[DepAction.descendant_id],
        back_populates="ancestor",
        lazy="dynamic",
        cascade="all",
    )

    dependants = db.relationship(
        "DepAction",
        foreign_keys=[DepAction.ancestor_id],
        back_populates="descendant",
        lazy="dynamic",
        cascade="all",
    )

    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    group = db.relationship("Group", back_populates="actions")

    attrs = db.relationship(
        "AttributeBelong", back_populates="action", lazy="dynamic", cascade="all"
    )

    def has_attr(self, attr):
        return self.attrs.filter_by(attr_id=attr.id).first() is not None

    def add_attr(self, attr, after):
        if after is not None:
            belongs = AttributeBelong.query.filter(
                AttributeBelong.attr_id == attr.id, AttributeBelong.order > after
            ).all()
            for b in belongs:
                b.order += 1
        else:
            max_belong = (
                AttributeBelong.query.filter(AttributeBelong.attr_id == attr.id)
                .order_by(AttributeBelong.order.desc())
                .first()
            )

            if max_belong is not None:
                after = max_belong.order + 1
            else:
                after = 0

        if after < 0:
            after = 0

        belong = self.attrs.filter_by(attr_id=attr.id).first()
        if belong is None:
            r = AttributeBelong(attr_id=attr.id, action_id=self.id, order=after)
            db.session.add(r)
            belong = r
        else:
            belong.order = after

        db.session.commit()
        return belong

    def remove_attr(self, attr):
        r = self.attrs.filter_by(attr_id=attr.id).first()
        if r is not None:
            db.session.delete(r)
            db.session.commit()

    @property
    def ss(self):
        d = self.to_dict()
        d["attrs"] = [merge(dict(order=a.order), a.attr.s) for a in self.attrs.all()]
        return d


class AttributeClusterType(Enum):
    TEXT = "text"
    NUMERIC = "numeric"
    TIME = "time"


class AttributeCluster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)

    deleted = db.Column(db.Integer, default=0)  # Boolean
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))
    group = db.relationship("Group", back_populates="clusters")

    attrs = db.relationship(
        "ActionAttribute", back_populates="cluster", lazy="dynamic", cascade="all"
    )

    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    modify_time = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String, default=AttributeClusterType.TEXT.value)
    aggregate = db.Column(db.Integer, default=0)  # Boolean

    @property
    def ss(self):
        d = self.to_dict()
        d["attrs"] = [attr.s for attr in self.attrs.all()]
        return d


class ActionAttribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    type = db.Column(db.String, default=AttributeClusterType.TEXT.value)
    order = db.Column(db.Integer, default=0)

    color = db.Column(db.Integer, nullable=False)

    actions = db.relationship(
        "AttributeBelong", back_populates="attr", lazy="dynamic", cascade="all"
    )

    cluster_id = db.Column(db.Integer, db.ForeignKey("attribute_cluster.id"))
    cluster = db.relationship("AttributeCluster", back_populates="attrs")


# @whooshee.register_model('body')
# class Sparkle(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.String(100))
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
#     deleted = db.Column(db.Boolean, default=False)

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
