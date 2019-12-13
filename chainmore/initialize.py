# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import (User, Post, Domain, Comment, Category)
from .utils import (exist_username, exist_email, exist_nickname, exist_domain)

fake = Faker(locale='zh_CN')


def admin():
    admin = User(nickname='柯力卬Kleon',
                 username='kleon',
                 email='1995dingli@gmail.com',
                 bio='阡陌 - 连接更多')

    admin.set_password('hellokleon')
    db.session.add(admin)
    db.session.commit()

def root_domain():
    domain = Domain(title="源",
                    description="领域根源",
                    bio="人正在关注",
                    creator=User.query.filter_by(username='kleon').first())
    db.session.add(domain)
    db.session.commit()

