# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import (User, Post, Domain, Comment, Category, ChoiceProblem,
                     Rule)
from .utils import (exist_username, exist_email, exist_nickname, exist_domain)

fake = Faker(locale='zh_CN')


def admin():
    admin = User(nickname='柯力卬Kleon',
                 username='kleon',
                 email='1995dingli@gmail.com',
                 root_certified=False,
                 bio='阡陌 - 连接更多')

    admin.set_password('hellokleon')
    db.session.add(admin)
    db.session.commit()


def admin_clear_root_certification():
    admin = User.query.filter_by(username='kleon').first()
    admin.root_certified = False
    root = Domain.query.filter_by(title="阡陌").first()
    root.uncertify(admin)
    db.session.commit()

def root_domain():
    admin = User.query.filter_by(username='kleon').first()
    domain = Domain(title="阡陌", description="领域根源", bio="人正在关注", creator=admin)
    # domain.certify(admin)
    cp = ChoiceProblem(body="良好的社区氛围离不开每个人的一言一行，以下属于正面有效发言的是：")
    cp.add_choices(
        ["可以试着尝试一些不同的风格。", "这点水平就不要出来丢人现眼了！", "要不要加入我们的学习小组？", "今天天气不错哦。"],
        [0])
    rule = Rule(type="choiceproblem", domain=domain, count=10)
    rule.add_choiceproblem([cp])

    cp = ChoiceProblem(body="遇到极端不友善发言的应对方法是：")
    cp.add_choices(
        ["直接举报", "友善提醒", "冷嘲热讽", "人身攻击"],
        [0])
    rule.add_choiceproblem([cp])

    db.session.add(rule)
    db.session.add(domain)
    db.session.commit()


def super_domain():
    root = Domain.query.get_or_404(1)

    super_domains = [
        ["知识", "学而时习", "人正在上下求索，温故知新"],
    ]

    for super_domain in super_domains:
        domain = Domain(title=super_domain[0],
                        description=super_domain[1],
                        bio=super_domain[2],
                        creator=User.query.filter_by(username='kleon').first())
        root.aggregate(domain)
        root.add_dependant(domain)
        db.session.add(domain)
    db.session.commit()
