# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask_sqlalchemy import SQLAlchemy
from flask_whooshee import Whooshee
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
whooshee = Whooshee()
jwt = JWTManager()
