# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import random
import string

from faker import Faker
from sqlalchemy.exc import IntegrityError
from typing import NamedTuple

from .extensions import db
from .models import (User, Domain, Depend, Aggregate, ResourceType, MediaType,
                     Role, Classify, CollectionType)
from .utils import (exist_username, exist_email, exist_nickname, exist_domain)

fake = Faker(locale='zh_CN')

class Language(NamedTuple):
    name_zh_cn: str
    name_en_us: str

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
    article = ResourceType(
        name="article",
        name_zh_cn="表达",
        name_en_us="Expression"
    )
    # Series of organized educational materials, MOOC
    course = ResourceType(
        name="course",
        name_zh_cn="课程",
        name_en_us="Course"
    )
    # Organized relatively independent collection of options, stories, discussion (Published)
    book = ResourceType(
        name="book",
        name_zh_cn="书籍",
        name_en_us="Book"
    )
    # Instructions/Procedure with few feedback
    tutorial = ResourceType(
        name="tutorial",
        name_zh_cn="教程步骤",
        name_en_us="Tutorial/Steps"
    )
    # Periodical & Publication, Arxiv, Research Paper
    research = ResourceType(
        name="research",
        name_zh_cn="研究",
        name_en_us="Research"
    )
    # Art
    art = ResourceType(
        name="art",
        name_zh_cn="艺术",
        name_en_us="Art"
    )
    # 分享
    share = ResourceType(
        name="share",
        name_zh_cn="分享",
        name_en_us="Share"
    )
    # Project
    project = ResourceType(
        name="project",
        name_zh_cn="公开合作项目",
        name_en_us="Project"
    )

    text = MediaType(
        name="text",
        name_zh_cn="文本",
        name_en_us="Text"
    )
    image = MediaType(
        name="image",
        name_zh_cn="图像",
        name_en_us="Image"
    )
    audio = MediaType(
        name="audio",
        name_zh_cn="音频",
        name_en_us="Audio"
    )
    video = MediaType(
        name="video",
        name_zh_cn="视频",
        name_en_us="Video"
    )
    interact = MediaType(
        name="interact",
        name_zh_cn="互动",
        name_en_us="Interact"
    )

    resources = [article, course, book, tutorial,
                 research, share, art, project]
    medias = [text, image, audio, video, interact]

    for i, resource in enumerate(resources):
        r = ResourceType.query.filter_by(name=resource.name).first()
        if r is None:
            db.session.add(resource)
        else:
            r.name = resources[i].name
            r.name_zh_cn = resources[i].name_zh_cn
            r.name_en_us = resources[i].name_en_us
            resources[i] = r

    for i, media in enumerate(medias):
        r = MediaType.query.filter_by(name=media.name).first()
        if r is None:
            db.session.add(media)
        else:
            r.name = medias[i].name
            r.name_zh_cn = medias[i].name_zh_cn
            r.name_en_us = medias[i].name_en_us
            medias[i] = r

    db.session.commit()

    m = {}
    m[(article.name, text.name)] = Language(
        name_zh_cn="文章",
        name_en_us="Article/Eassay"
    )
    m[(article.name, image.name)] = Language(
        name_zh_cn="图文",
        name_en_us="Graphic Article"
    )
    m[(article.name, audio.name)] = Language(
        name_zh_cn="播客/录音",
        name_en_us="Podcast/Audio"
    )
    m[(article.name, video.name)] = Language(
        name_zh_cn="视频",
        name_en_us="Video"
    )
    m[(article.name, interact.name)] = Language(
        name_zh_cn="互动表达",
        name_en_us="Interactive Expression"
    )

    m[(course.name, text.name)] = Language(
        name_zh_cn="文本课程",
        name_en_us="Text Course"
    )
    m[(course.name, image.name)] = Language(
        name_zh_cn="图文课程",
        name_en_us="Graphic Course"
    )
    m[(course.name, audio.name)] = Language(
        name_zh_cn="音频课程",
        name_en_us="Audio Course"
    )
    m[(course.name, video.name)] = Language(
        name_zh_cn="视频课程",
        name_en_us="Video Course"
    )
    m[(course.name, interact.name)] = Language(
        name_zh_cn="互动课程",
        name_en_us="Interactive Course"
    )

    m[(book.name, text.name)] = Language(
        name_zh_cn="书籍（文本为主）",
        name_en_us="Text Book"
    )
    m[(book.name, image.name)] = Language(
        name_zh_cn="书籍（图片为主）",
        name_en_us="Graphic Book"
    )
    m[(book.name, audio.name)] = Language(
        name_zh_cn="有声书",
        name_en_us="Audio Book"
    )
    m[(book.name, video.name)] = Language(
        name_zh_cn="书籍（嵌入视频）",
        name_en_us="Video Book"
    )
    m[(book.name, interact.name)] = Language(
        name_zh_cn="互动书籍",
        name_en_us="Interactive Book"
    )

    m[(tutorial.name, text.name)] = Language(
        name_zh_cn="文字教程",
        name_en_us="Text Tutorial"
    )
    m[(tutorial.name, image.name)] = Language(
        name_zh_cn="图片教程",
        name_en_us="Graphic Tutorial"
    )
    m[(tutorial.name, audio.name)] = Language(
        name_zh_cn="音频教程",
        name_en_us="Audio Tutorial"
    )
    m[(tutorial.name, video.name)] = Language(
        name_zh_cn="视频教程",
        name_en_us="Video Tutorial"
    )
    m[(tutorial.name, interact.name)] = Language(
        name_zh_cn="互动教程",
        name_en_us="Interactive Tutorial"
    )

    m[(research.name, text.name)] = Language(
        name_zh_cn="论文",
        name_en_us="Paper"
    )
    m[(research.name, image.name)] = Language(
        name_zh_cn="科研图像",
        name_en_us="Research Image"
    )
    m[(research.name, audio.name)] = Language(
        name_zh_cn="科研音频",
        name_en_us="Research Audio"
    )
    m[(research.name, video.name)] = Language(
        name_zh_cn="科研视频",
        name_en_us="Research Video"
    )
    m[(research.name, interact.name)] = Language(
        name_zh_cn="科研互动",
        name_en_us="Research Interactive"
    )

    m[(art.name, text.name)] = Language(
        name_zh_cn="文学",
        name_en_us="Literature"
    )
    m[(art.name, image.name)] = Language(
        name_zh_cn="静态视觉艺术",
        name_en_us="Static Graphic Art"
    )
    m[(art.name, audio.name)] = Language(
        name_zh_cn="声音艺术",
        name_en_us="Audio Art"
    )
    m[(art.name, video.name)] = Language(
        name_zh_cn="动态视觉艺术",
        name_en_us="Dynamic Graphic Art"
    )
    m[(art.name, interact.name)] = Language(
        name_zh_cn="互动艺术",
        name_en_us="Interactive Art"
    )

    m[(share.name, text.name)] = Language(
        name_zh_cn="短评",
        name_en_us="Short Comment"
    )
    m[(share.name, image.name)] = Language(
        name_zh_cn="长图",
        name_en_us="Long Picture"
    )
    m[(share.name, audio.name)] = Language(
        name_zh_cn="短音频",
        name_en_us="Short Audio"
    )
    m[(share.name, video.name)] = Language(
        name_zh_cn="短视频",
        name_en_us="Short Video"
    )
    m[(share.name, interact.name)] = Language(
        name_zh_cn="社交互动",
        name_en_us="Social Interaction"
    )

    m[(project.name, text.name)] = Language(
        name_zh_cn="代码库",
        name_en_us="Code Base"
    )
    m[(project.name, image.name)] = Language(
        name_zh_cn="图像库",
        name_en_us="Graphic Library"
    )
    m[(project.name, audio.name)] = Language(
        name_zh_cn="音频项目",
        name_en_us="Audio Project"
    )
    m[(project.name, video.name)] = Language(
        name_zh_cn="视频项目",
        name_en_us="Video Project"
    )
    m[(project.name, interact.name)] = Language(
        name_zh_cn="互动项目/网站",
        name_en_us="Interactive Project/WebSite"
    )

    for resource in resources:
        for media in medias:
            
            language = m.get((resource.name, media.name), None)
            if language is None:
                continue

            r = Classify.query.filter_by(classifier_id=resource.id, classified_id=media.id).first()
            if r is None:
                db.session.add(
                    Classify(
                        classifier_id=resource.id, 
                        classified_id=media.id, 
                        name_zh_cn=language.name_zh_cn,
                        name_en_us=language.name_en_us))
            else:
                r.name_zh_cn = language.name_zh_cn
                r.name_en_us = language.name_en_us

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
    
        root = Domain.query.get_or_404(1)
        admin.mark(root)

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

        root = Domain.query.get_or_404(1)
        admin.mark(root)

def certify():
    admin = User.query.filter_by(username='kleon').first()
    root = Domain.query.get_or_404(1)

    root.certify(admin)