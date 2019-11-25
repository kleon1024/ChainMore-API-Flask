# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import datetime

from flask import Blueprint, request
from flask_jwt_extended import (create_access_token, jwt_required,
                                current_user, get_raw_jwt,
                                create_refresh_token, jwt_refresh_token_required)
from flask_restful import Api, Resource

import base64

from ..extensions import db, jwt
from ..utils import (exist_email, exist_username, validate_email,
                     validate_username, validate_password, response)
from ..models import User

blacklist = set()

auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp)


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
        nickname = data.get("nickname", "")
        email = data.get("email", "")
        payload = data.get("payload", "")
        payload = base64.b64decode(payload).decode("utf-8")
        username, password = payload.split(':')
        # if not validate_email(email, 64) or \
        # not validate_username(username, 20):
        #     return response("BAD_REQUEST", msg="Invalid Data")
        if exist_email(email):
            return response("EMAIL_EXIST", msg="Mail Exist")
        if exist_username(username):
            return response("USERNAME_EXIST", msg="Username Exist")
        user = User(nickname=nickname, email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return response("OK", msg="User Registered")


class SignIn(Resource):
    def post(self):
        data = request.get_json()
        if data is None:
            return response("EMPTY_BODY", msg="Empty Body")
        payload = data.get("payload", "")
        payload = base64.b64decode(payload).decode("utf-8")
        username, password = payload.split(':')

        if validate_email(username, 18):
            user = User.query.filter_by(email=username.lower()).first()
        elif validate_username(username, 20):
            user = User.query.filter_by(username=username.lower()).first()

        if user is not None and user.validate_password(password):
            username = user.username
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            return response("OK",
                            msg="User Login As {}".format(username),
                            accessToken=access_token,
                            refreshToken=refresh_token)
        
        return response("SIGN_IN_FAILED", msg="Invalid Credential")


class SignOut(Resource):
    @jwt_required
    def delete(self):
        jti = get_raw_jwt()['jti']
        print(jti)
        blacklist.add(jti)
        return response("OK", msg="Successfully logged out")

class SigninRefresh(Resource):
    @jwt_refresh_token_required
    def get(self):
        username = current_user.username
        access_token = create_access_token(identity=username)
        return response("OK",
                        msg="Token Refreshed",
                        accessToken=access_token)

api.add_resource(SignIn, '/signin')
api.add_resource(SignUp, '/signup')
api.add_resource(SignOut, '/signout')
api.add_resource(SigninRefresh, '/signin/refresh')
