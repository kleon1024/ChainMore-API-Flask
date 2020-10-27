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
    article = ResourceType(
        name="article",
        name_zh_cn="表达"
    )
    # Series of organized educational materials, MOOC
    course = ResourceType(
        name="course",
        name_zh_cn="课程"
    )
    # Organized relatively independent collection of options, stories, discussion (Published)
    book = ResourceType(
        name="book",
        name_zh_cn="书籍"
    )
    # Instructions/Procedure with few feedback
    tutorial = ResourceType(
        name="tutorial",
        name_zh_cn="教程步骤"
    )
    # Periodical & Publication, Arxiv, Research Paper
    research = ResourceType(
        name="research",
        name_zh_cn="研究"
    )
    # Art
    art = ResourceType(
        name="art",
        name_zh_cn="艺术"
    )
    # 分享
    share = ResourceType(
        name="share",
        name_zh_cn="社交分享"
    )
    # Project
    project = ResourceType(
        name="project",
        name_zh_cn="公开合作项目"
    )

    text = MediaType(
        name="text",
        name_zh_cn="文本"
    )
    image = MediaType(
        name="image",
        name_zh_cn="图像"
    )
    audio = MediaType(
        name="audio",
        name_zh_cn="音频"
    )
    interact = MediaType(
        name="interact",
        name_zh_cn="互动"
    )

    resources = [article, course, book, tutorial,
                 research, share, art, project]
    medias = [text, image, audio, video, interact]

    for i, resource in enumerate(resources):
        if ResourceType.query.filter_by(name=resource.name).first() is None:
            db.session.add(resource)
        else:
            r = ResourceType.query.filter_by(name=resource.name).first()
            r.name = resources[i].name
            r.name_zh_cn = resources[i].name_zh_cn
            resources[i] = r
            

    for i, media in enumerate(medias):
        if MediaType.query.filter_by(name=media.name).first() is None:
            db.session.add(media)
        else:
            r = MediaType.query.filter_by(name=media.name).first()
            r.name = medias[i].name
            r.name_zh_cn = medias[i].name_zh_cn
            medias[i] = r

    db.session.commit()

    m = {}
    m[(article.id, text.id)] = dict(
        name_zh_cn="文章"
    )
    m[(article.id, image.id)] = dict(
        name_zh_cn="图文"
    )
    m[(article.id, audio.id)] = dict(
        name_zh_cn="播客/录音"
    )
    m[(article.id, video.id)] = dict(
        name_zh_cn="视频"
    )
    m[(article.id, interact.id)] = dict(
        name_zh_cn="互动作品"
    )

    m[(course.id, text.id)] = dict(
        name_zh_cn="文本课程"
    )
    m[(course.id, image.id)] = dict(
        name_zh_cn="图文课程"
    )
    m[(course.id, audio.id)] = dict(
        name_zh_cn="音频课程"
    )
    m[(course.id, video.id)] = dict(
        name_zh_cn="视频课程"
    )
    m[(course.id, interact.id)] = dict(
        name_zh_cn="互动课程"
    )

    m[(book.id, text.id)] = dict(
        name_zh_cn="书籍（文本为主）"
    )
    m[(book.id, image.id)] = dict(
        name_zh_cn="书籍（图片为主）"
    )
    m[(book.id, audio.id)] = dict(
        name_zh_cn="有声书"
    )
    m[(book.id, video.id)] = dict(
        name_zh_cn="书籍（嵌入视频）"
    )
    m[(book.id, interact.id)] = dict(
        name_zh_cn="互动书籍"
    )

    m[(tutorial.id, text.id)] = dict(
        name_zh_cn="文字教程"
    )
    m[(tutorial.id, image.id)] = dict(
        name_zh_cn="图片教程"
    )
    m[(tutorial.id, audio.id)] = dict(
        name_zh_cn="音频教程"
    )
    m[(tutorial.id, video.id)] = dict(
        name_zh_cn="视频教程"
    )
    m[(tutorial.id, interact.id)] = dict(
        name_zh_cn="互动教程"
    )

    m[(research.id, text.id)] = dict(
        name_zh_cn="论文"
    )
    m[(research.id, image.id)] = dict(
        name_zh_cn="科研图像"
    )
    m[(research.id, audio.id)] = dict(
        name_zh_cn="科研音频"
    )
    m[(research.id, video.id)] = dict(
        name_zh_cn="科研视频"
    )
    m[(research.id, interact.id)] = dict(
        name_zh_cn="科研互动"
    )

    m[(art.id, text.id)] = dict(
        name_zh_cn="文学"
    )
    m[(art.id, image.id)] = dict(
        name_zh_cn="静态视觉艺术"
    )
    m[(art.id, audio.id)] = dict(
        name_zh_cn="声音艺术"
    )
    m[(art.id, video.id)] = dict(
        name_zh_cn="动态视觉艺术"
    )
    m[(art.id, interact.id)] = dict(
        name_zh_cn="互动艺术"
    )

    m[(share.id, text.id)] = dict(
        name_zh_cn="短评"
    )
    m[(share.id, image.id)] = dict(
        name_zh_cn="长图"
    )
    m[(share.id, audio.id)] = dict(
        name_zh_cn="短音频"
    )
    m[(share.id, video.id)] = dict(
        name_zh_cn="短视频"
    )
    m[(share.id, interact.id)] = dict(
        name_zh_cn="社交互动"
    )

    m[(project.id, text.id)] = dict(
        name_zh_cn="代码库"
    )
    m[(project.id, image.id)] = dict(
        name_zh_cn="图像库"
    )
    m[(project.id, audio.id)] = dict(
        name_zh_cn="音频项目"
    )
    m[(project.id, video.id)] = dict(
        name_zh_cn="视频项目"
    )
    m[(project.id, interact.id)] = dict(
        name_zh_cn="互动项目"
    )


    for resource in resources:
        for media in medias:
            if (resource.id, media.id) in m:
                r = Classify.query.filter_by(classifier_id=resource.id, classified_id=media.id).first():
                if r is None:
                    db.session.add(
                        Classify(classifier_id=resource.id, classified_id=media.id, name_zh_cn=m[(resource.id, media.id)]['name_zh_cn']))
                else:
                    r.name_zh_cn = m[(resource.id, media.id)]['name_zh_cn']

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