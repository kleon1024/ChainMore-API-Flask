# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import datetime

from flask import Blueprint, request
from flask_jwt_extended import (create_access_token)

import base64

from ..extensions import db, jwt
from ..utils import (exist_email, exist_username, validate_email,
                     validate_username, validate_password, response)
from ..models import User

auth_bp = Blueprint('auth', __name__)


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return User.query.filter_by(username=identity).first()


@jwt.user_loader_error_loader
def custom_user_loader_error(identity):
    return response("INVALID_AUTH", msg="User {} not found".format(identity))


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if data is None:
        return response("EMPTY_BODY", msg="Empty Body")
    nickname = data.get("nickname", "")
    email = data.get("email", "")
    payload = data.get("payload", "")
    username, password = base64.b64decode(payload).split(':')
    if not validate_email(email, 64) or \
       not validate_username(username, 20) or \
       not validate_password(password, 64):
        return response("BAD_REQUEST", msg="Invalid Data")
    if exist_email(email):
        return response("EMAIL_EXIST", msg="Mail Exist")
    if exist_username(username):
        return response("USERNAME_EXIST", msg="Username Exist")
    user = User(nickname=nickname, email=email, username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return response("OK", msg="User Registered")


@auth_bp.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    if data is None:
        return response("EMPTY_BODY", msg="Empty Body")
    payload = data.get("payload", "")
    username, password = base64.b64decode(payload).split(':')

    if validate_email(username, 18):
        user = User.query.filter_by(email=username.lower()).first()
        if user is not None and user.validate_password(password):
            username = user.username
            expires = datetime.timedelta(hours=1)
            access_token = create_access_token(identity=username,
                                               expired=expires)
            return response("CREATED",
                            msg="User Login As {}".format(username),
                            token=access_token)

    if validate_username(username, 20):
        user = User.query.filter_by(username=username.lower()).first()
        if user is not None and user.validate_password(password):
            access_token = create_access_token(identity=username)
            return response("CREATED",
                            msg="User Login As {}".format(username),
                            token=access_token)

    return response("SIGN_IN_FAILED", msg="Invalid Credential")
