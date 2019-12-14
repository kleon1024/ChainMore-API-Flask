# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import re

from flask import (jsonify, abort)

from .models import User, Domain


def response(status="OK", **kwargs):
    result = {}
    status_code = 200
    for k, v in kwargs.items():
        result[k] = v
    if status == "OK":
        result["code"] = 20000
    elif status == "INVALID_AUTH":
        result["code"] = 20001
    elif status == "EMPTY_BODY":
        result["code"] = 20002
    elif status == "EMAIL_EXIST":
        result["code"] = 20100
    elif status == "USERNAME_EXIST":
        result["code"] = 20101
    elif status == "SIGN_IN_FAILED":
        result["code"] = 20102
    elif status == "CREATED":
        result["code"] = 20000
        status_code = 201
    elif status == "CERTIFY_FAILED":
        result["code"] = 30000
    elif status == "BAD_REQUEST":
        abort(400)
    elif status == "UNAUTHORIZED":
        abort(401)
    elif status == "METHOD_NOT_ALLOWED":
        abort(405)
    else:
        abort(404)
    response = jsonify(result)
    response.status_code = status_code
    return response


def exist_email(value):
    if User.query.filter_by(email=value.lower()).first():
        return True
    else:
        return False


def exist_username(value):
    if User.query.filter_by(username=value).first():
        return True
    else:
        return False


def exist_nickname(value):
    if User.query.filter_by(nickname=value).first():
        return True
    else:
        return False


def exist_domain(value):
    if Domain.query.filter_by(title=value).first():
        return True
    else:
        return False


def validate_email(email, length):
    if len(email) > length:
        return False
    pattern = r'^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)\
                |(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]\
                {1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'

    if not re.match(pattern, email):
        return False
    return True


def validate_username(name, length):
    if len(name) > length:
        return False
    return True


def validate_password(password, length):
    if len(password) > length:
        return False
    pattern = r'^(?=.*?[a-zA-Z])(?=.*?[0-9])(?=.*?[!@#\$&*~]).{6,}$'
    if not re.match(pattern, password):
        return False
    return True
