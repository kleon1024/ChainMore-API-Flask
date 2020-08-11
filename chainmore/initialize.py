# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import random
import string

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
    else:
        domain.intro = "chainmore 阡陌 根领域"

    admin.mark(domain)

    # domain.certify(User.query.filter_by(username='kleon').first())

    Depend.query.filter(Depend.ancestor_id==domain.id, Depend.descendant_id==domain.id).delete()

    db.session.add(Depend(ancestor_id=domain.id,
                          descendant_id=domain.id,
                          distance=0))

    db.session.add(Aggregate(ancestor_id=domain.id,
                             descendant_id=domain.id,
                             distance=0))

    db.session.commit()


def resource_media_type():

    # Independent discussion/expression on any topics
    article = ResourceType(name="article")
    # Series of organized educational materials, MOOC
    course = ResourceType(name="course")
    # Organized relatively independent collection of options, stories, discussion (Published)
    book = ResourceType(name="book")
    # Instructions/Procedure with few feedback
    tutorial = ResourceType(name="tutorial")
    # Periodical & Publication, Arxiv, Research Paper
    research = ResourceType(name="research")
    # Art
    art = ResourceType(name="art")
    # Website
    share = ResourceType(name="share")

    text = MediaType(name="text")
    image = MediaType(name="image")
    audio = MediaType(name="audio")
    video = MediaType(name="video")

    resources = [article, course, book, tutorial,
                 research, share, art]
    medias = [text, image, audio, video]

    for i, resource in enumerate(resources):
        if ResourceType.query.filter_by(name=resource.name).first() is None:
            db.session.add(resource)
        else:
            resources[i] = ResourceType.query.filter_by(name=resource.name).first()

    for i, media in enumerate(medias):
        if MediaType.query.filter_by(name=media.name).first() is None:
            db.session.add(media)
        else:
            medias[i] = MediaType.query.filter_by(name=media.name).first()

    db.session.commit()

    for resource in resources:
        for media in medias:
            if (
                # Discussion & Expression article | image | audio, Podcast | video, VLOG, speech
                resource.name == "article" and media.name in ["text", "image", "audio", "video"] or
                # Via pure text | Mainly expressed in image | Audio Course | Video Course, MOOC
                resource.name == "course" and media.name in ["text", "image", "audio", "video"] or
                # Textbook | Picture Collection | Audio Book
                resource.name == "book" and media.name in ["text", "image", "audio", "video"] or
                # Tutorial in text | Tutorial in image | Tutorial in audio | Tutorial in video
                resource.name == "tutorial" and media.name in ["text", "image", "audio", "video"] or
                # Publication Research Paper | Pulicated Image | Publicated Audio | Publicated Video
                resource.name == "research" and media.name in [
                    "text", "image", "audio", "video"] or
                # Literature | Graphic Art | Music | Movie
                resource.name == "art" and media.name in ["text", "image", "audio", "video"] or
                # Any Instance
                resource.name == "share" and media.name in [
                    "text", "image", "audio", "video"]
            ):
                if Classify.query.filter_by(classifier_id=resource.id, classified_id=media.id).first() is None:
                    db.session.add(
                        Classify(classifier_id=resource.id, classified_id=media.id))

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


def add_user(username, role):
    if User.query.filter_by(username=username).first() is None:
        admin = User(username=username)

        salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        admin.email = salt
        admin.phone = salt
        admin.set_password(salt)
        assert role in [r.name for r in Role.query.all()]
        admin.set_role(role)
        print("salt:{}".format(salt))
        db.session.add(admin)
        db.session.commit()

def reset_user(username, role):
    if User.query.filter_by(username=username).first() is not None:
        admin = User.query.filter_by(username=username).first()

        salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        admin.set_password(salt)
        admin.email = salt
        admin.phone = salt
        assert role in [r.name for r in Role.query.all()]
        admin.set_role(role)
        print("salt:{}".format(salt))
        db.session.commit()
