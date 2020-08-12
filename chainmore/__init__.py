# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import os

import click

from flask import Flask
from collections import OrderedDict

from .blueprints.auth import auth_bp
from .blueprints.domain import domain_bp
# from .blueprints.comment import comment_bp
# from .blueprints.sparkle import sparkle_bp
from .blueprints.roadmap import roadmap_bp
from .blueprints.collection import collection_bp
from .blueprints.user import user_bp
from .blueprints.resource import resource_bp
from .blueprints.main import main_bp

from .extensions import db, jwt, whooshee
from .settings import config
from flask_migrate import Migrate
from flask_cors import CORS


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('chainmore')
    CORS(app, resources={r"/v1/*": {"origins": "https://www.chainmore.fun"}})
    
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errorhandlers(app)

    return app


def register_extensions(app):
    db.init_app(app)
    whooshee.init_app(app)
    jwt.init_app(app)
    Migrate(app, db)


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/v1/auth')
    app.register_blueprint(domain_bp, url_prefix='/v1/domain')
    app.register_blueprint(roadmap_bp, url_prefix='/v1/roadmap')
    # app.register_blueprint(comment_bp, url_prefix='/v1/comment')
    app.register_blueprint(collection_bp, url_prefix='/v1/collection')
    # app.register_blueprint(sparkle_bp, url_prefix='/v1/sparkle')
    app.register_blueprint(user_bp, url_prefix='/v1/user')
    app.register_blueprint(resource_bp, url_prefix='/v1/resource')
    app.register_blueprint(main_bp, url_prefix='/v1')


def register_errorhandlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return {}, 400


def register_commands(app):

    @click.option('--username', required=True)
    @click.option('--role', required=True)
    @app.cli.command()
    def create_user(username, role):
        """Create User"""
        click.echo("Creating {}".format(username))
        from .initialize import add_user
        add_user(username, role)

    @click.option('--username', required=True)
    @click.option('--role', required=True)
    @app.cli.command()
    def reset_user(username, role):
        """Create User"""
        click.echo("Creating {}".format(username))
        from .initialize import reset_user
        reset_user(username, role)

    @app.cli.command()
    def reset():
        """Reset database"""
        click.echo("Resetting database...")

        db.drop_all()
        db.create_all()
        db.session.commit()

    @app.cli.command()
    def init():
        """Initialize data"""
        db.create_all()
        db.session.commit()
        click.echo('Initializing data...')

        from .initialize import (init_role, admin, root_domain,
                                 resource_media_type, collection_type)

        click.echo('Creating roles...')
        init_role()
        click.echo('Creating admin...')
        admin()
        click.echo('Creating root domain...')
        root_domain()
        click.echo('Creating resource media type...')
        resource_media_type()
        click.echo('Creating collection type...')
        collection_type()

        click.echo('Done')

    @app.cli.command()
    @click.option('--user', default=30)
    @click.option('--domain', default=10)
    @click.option('--post', default=20)
    @click.option('--follow', default=30)
    @click.option('--comment', default=50)
    @click.option('--collect', default=20)
    @click.option('--watch', default=30)
    @click.option('--like', default=100)
    @click.option('--vote', default=50)
    def forge(user, domain, post, follow, comment, collect, watch, like, vote):
        """Generate fake data."""
        click.echo('Initializing fake data...')

        from .fakes import (fake_admin, fake_user, fake_comment, fake_follow,
                            fake_domain, fake_post, fake_watch, fake_like,
                            fake_vote, fake_collect)

        click.echo('Generating the administrator...')
        fake_admin()
        click.echo('Generating %d users...' % user)
        fake_user(user)
        click.echo('Generating %d follows...' % follow)
        fake_follow(follow)
        click.echo('Generating %d domain...' % domain)
        fake_domain(domain)
        click.echo('Generating %d posts...' % post)
        fake_post(post)
        click.echo('Generating %d comments...' % comment)
        fake_comment(comment)
        click.echo('Generating %d watches...' % watch)
        fake_watch(watch)
        click.echo('Generating %d likes...' % like)
        fake_like(like)
        click.echo('Generating %d votes...' % vote)
        fake_vote(vote)
        click.echo('Generating %d collects...' % collect)
        fake_collect(collect)
        click.echo('Done')
