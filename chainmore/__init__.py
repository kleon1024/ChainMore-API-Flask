# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import os

import click

from flask import Flask

from .blueprints.auth import auth_bp
from .blueprints.domain import domain_bp
from .blueprints.comment import comment_bp
from .blueprints.post import post_bp
from .blueprints.user import user_bp
from .blueprints.main import main_bp
from .extensions import db, jwt, whooshee
from .settings import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('chainmore')

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


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/v1/auth')
    app.register_blueprint(domain_bp, url_prefix='/v1/domain')
    app.register_blueprint(comment_bp, url_prefix='/v1/comment')
    app.register_blueprint(post_bp, url_prefix='/v1/post')
    app.register_blueprint(user_bp, url_prefix='/v1/user')
    app.register_blueprint(main_bp, url_prefix='/v1')


def register_errorhandlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return {}, 400


def register_commands(app):
    @app.cli.command()
    def forge():
        """Generate fake data."""
        click.echo('Initializing fake data...')
