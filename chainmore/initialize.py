# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import (User, Domain, Depend, Aggregate, ResourceType, MediaType,
                     Role)
from .utils import (exist_username, exist_email, exist_nickname, exist_domain)

fake = Faker(locale='zh_CN')


def admin():
    admin = User(nickname='Kleon',
                 username='kleon',
                 email='dingli.cm@gmail.com',
                 bio='阡陌 - 连接更多')

    admin.set_password('hellokleon')
    admin.set_role('Administrator')

    db.session.add(admin)
    db.session.commit()


def root_domain():
    admin = User.query.filter_by(username='kleon').first()
    domain = Domain(title="阡陌", creator=admin)
    db.session.add(domain)
    db.session.commit()

    domain.certify(User.query.filter_by(username='kleon').first())

    depend = Depend(ancestor_id=domain.id, descendant_id=domain.id, distance=0)
    aggregate = Aggregate(ancestor_id=domain.id,
                          descendant_id=domain.id,
                          distance=0)

    db.session.add(depend)
    db.session.add(aggregate)
    db.session.commit()


def resource_type():
    r = ResourceType(name="article")
    db.session.add(r)
    db.session.commit()


def media_type():
    m = MediaType(name="text")
    db.session.add(m)
    db.session.commit()


def init_role():
    Role.init_role()
