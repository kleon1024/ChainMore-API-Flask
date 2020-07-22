# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import datetime
import os
import time

from flask import Blueprint, request
from flask_jwt_extended import (create_access_token, jwt_required,
                                current_user, get_raw_jwt,
                                create_refresh_token,
                                jwt_refresh_token_required)
from flask_restful import Api, Resource

import base64

from ..extensions import db, jwt
from ..utils import (exist_email, exist_username, validate_email,
                     validate_username, validate_password, response)
from ..models import User

blacklist = set()

auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp)

access_token_expire_time = datetime.timedelta(days=120)
refresh_token_expire_time = datetime.timedelta(days=300)


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return User.query.filter_by(username=identity).first()


@jwt.user_loader_error_loader
def custom_user_loader_error(identity):
    return response("INVALID_AUTH", msg="User {} not found".format(identity))


class SignUp(Resource):
    def post(self):
        data = request.get_json()
        if data is None:
            return response("EMPTY_BODY", msg="Empty Body")
        email = data.get("email", "")
        username = data.get("username", "")
        password = data.get("password", "")
        # if not validate_email(email, 64) or \
        # not validate_username(username, 20):
        #     return response("BAD_REQUEST", msg="Invalid Data")
        if exist_email(email):
            return response("EMAIL_EXIST", msg="Mail Exist")
        if exist_username(username):
            return response("USERNAME_EXIST", msg="Username Exist")

        if nickname == "":
            nickname = "探索者" + username + str(int(time.time() % 100000000))
        user = User(nickname=nickname, email=email, username=username, bio="")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return response("OK", msg="User Registered")


class SignIn(Resource):
    def post(self):
        data = request.get_json()
        username = data["username"]
        password = data["password"]

        if validate_email(username, 18):
            user = User.query.filter_by(email=username.lower()).first()
        elif validate_username(username, 20):
            user = User.query.filter_by(username=username.lower()).first()
        
        if user is not None and user.validate_password(password):
            username = user.username
            access_token = create_access_token(
                identity=username, expires_delta=access_token_expire_time)
            refresh_token = create_refresh_token(
                identity=username, expires_delta=refresh_token_expire_time)
            return response("OK",
                            msg="User Login As {}".format(username),
                            id=user.id,
                            username=username,
                            access_token=access_token,
                            refresh_token=refresh_token)

        return response("BAD_REQUEST")


class SignOut(Resource):
    @jwt_required
    def delete(self):
        jti = get_raw_jwt()['jti']
        blacklist.add(jti)
        return response("OK", msg="Successfully logged out")


class SigninRefresh(Resource):
    @jwt_refresh_token_required
    def get(self):
        username = current_user.username
        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)
        return response("OK",
                        msg="Token Refreshed",
                        access_token=access_token,
                        refresh_token=refresh_token)


api.add_resource(SignIn, '/signin')
api.add_resource(SignUp, '/signup')
api.add_resource(SignOut, '/signout')
api.add_resource(SigninRefresh, '/refresh')
