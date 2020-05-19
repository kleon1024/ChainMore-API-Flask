# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import (User, Domain, ResourceType, MediaType)
from .utils import (exist_username, exist_email, exist_nickname, exist_domain)

fake = Faker(locale='zh_CN')


def admin():
    admin = User(nickname='柯力卬Kleon',
                 username='kleon',
                 email='dingli.cm@gmail.com',
                 root_certified=False,
                 bio='阡陌 - 连接更多')

    admin.set_password('hellokleon')
    db.session.add(admin)
    db.session.commit()


def root_domain():
    admin = User.query.filter_by(username='kleon').first()
    domain = Domain(title="阡陌", creator=admin)

    db.session.add(domain)
    db.session.commit()


def resource_type():
    r = ResourceType(name="article")
    db.session.add(r)
    db.session.commit()


def media_type():
    m = MediaType(name="text")
    db.session.add(m)
    db.session.commit()
