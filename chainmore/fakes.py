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
from .utils import (exist_username, exist_email, 
                    exist_nickname, exist_domain)

fake = Faker(locale='zh_CN')

def fake_admin():
    admin = User(nickname='KLEON',
                 username='kleon',
                 email='1995dingli@gmail.com',
                 bio='阡陌 - 连接更多')

    admin.set_password('hellokleon')
    db.session.add(admin)
    db.session.commit()

def fake_user(count=10):
    for _ in range(count):
        while True:
            username = fake.user_name()
            if not exist_username(username): break
        while True:
            email = fake.email()
            if not exist_email(email): break
        while True:
            nickname = fake.name()
            if not exist_nickname(nickname): break
        user = User(nickname=nickname,
                    username=username,
                    bio=fake.sentence(),
                    email=email)
        user.set_password('123456')
        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()

def fake_collect(count=30):
    for _ in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.collect(Post.query.get(random.randint(1, Post.query.count())))
    db.session.commit()

def fake_comment(count=30):
    for _ in range(count):
        comment = Comment(
            author=User.query.get(random.randint(1, User.query.count())),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            post=Post.query.get(random.randint(1, Post.query.count())),
        )
        db.session.add(comment)
    db.session.commit()

def fake_vote(count=30):
    for _ in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.vote(Comment.query.get(random.randint(1, Comment.query.count())))
    db.session.commit()

def fake_follow(count=30):
    for _ in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.follow(User.query.get(random.randint(1, User.query.count())))
    db.session.commit()

def fake_domain(count=30):
    for _ in range(count):
        while True:
            title = fake.job()
            if not exist_domain(title): break
        domain = Domain(
            title = title,
            description = fake.text(),
            bio = "名" + fake.job() + "正在" + fake.word(),
            timestamp = fake.date_time_this_year(),
            creator=User.query.get(random.randint(1, User.query.count()))
        )
        db.session.add(domain)
    db.session.commit()

def fake_post(count=30):
    for _ in range(count):
        post = Post(
            title=fake.sentence(),
            description=fake.text(),
            url="https://juejin.im/post/5db684ddf265da4d495c40e5",
            timestamp = fake.date_time_this_year(),
            category = Category.query.get(random.randint(1, Category.query.count())),
            author = User.query.get(random.randint(1, User.query.count())),
            domain = Domain.query.get(random.randint(1, Domain.query.count())),
        )
        db.session.add(post)
    db.session.commit()

def fake_like(count=50):
    for _ in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.like(Post.query.get(random.randint(1, Post.query.count())))
    db.session.commit()

def fake_watch(count=30):
    for _ in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.watch(Domain.query.get(random.randint(1, Domain.query.count())))
    db.session.commit()