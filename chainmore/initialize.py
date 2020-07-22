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
                     Role, Classify, CollectionType)
from .utils import (exist_username, exist_email, exist_nickname, exist_domain)

fake = Faker(locale='zh_CN')


def admin():
    if User.query.filter_by(username='kleon').first() is None:
        admin = User(username='kleon',
                    email='dingli.cm@gmail.com',
                    bio='阡陌 - 连接更多')

        admin.set_password('hellokleon')
        admin.set_role('Administrator')

        db.session.add(admin)
        db.session.commit()


def root_domain():
    admin = User.query.filter_by(username='kleon').first()
    domain = Domain.query.filter_by(title="∞").first()
    if domain is None:
        domain = Domain(title="∞", creator=admin)
        db.session.add(domain)
        db.session.commit()

    admin.mark(domain)

    domain.certify(User.query.filter_by(username='kleon').first())

    domain.dep(domain)
    domain.agg(domain)
    db.session.commit()


def resource_media_type():
    article = ResourceType(name="article")
    course = ResourceType(name="course")
    book = ResourceType(name="book")

    
    text = MediaType(name="text")
    image = MediaType(name="image")
    audio = MediaType(name="audio")
    video = MediaType(name="video")

    db.session.add(article)
    db.session.add(course)
    
    db.session.add(text)
    db.session.add(image)
    db.session.add(audio)
    db.session.add(video)

    db.session.commit()

    db.session.add(Classify(classifier_id=article.id, classified_id=text.id))
    db.session.add(Classify(classifier_id=article.id, classified_id=image.id))
    db.session.add(Classify(classifier_id=article.id, classified_id=audio.id))
    db.session.add(Classify(classifier_id=article.id, classified_id=video.id))

    db.session.add(Classify(classifier_id=course.id, classified_id=text.id))
    db.session.add(Classify(classifier_id=course.id, classified_id=image.id))
    db.session.add(Classify(classifier_id=course.id, classified_id=audio.id))
    db.session.add(Classify(classifier_id=course.id, classified_id=video.id))  

    db.session.commit()


def collection_type():
    collection = CollectionType(name="collection")
    idea = CollectionType(name="idea")
    news = CollectionType(name="news")
    question = CollectionType(name="question")
    answer = CollectionType(name="answer")

    db.session.add(collection)
    db.session.add(idea)
    db.session.add(news)
    db.session.add(question)
    db.session.add(answer)


def init_role():
    Role.init_role()
