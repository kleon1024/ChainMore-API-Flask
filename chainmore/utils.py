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
        abort(401)
    elif status == "EMPTY_BODY":
        result["code"] = 20002
    elif status == "EMAIL_EXIST":
        result["code"] = 20100
    elif status == "USERNAME_EXIST":
        result["code"] = 20101
    elif status == "SIGN_IN_FAILED":
        result["code"] = 20102
    elif status == "DOMAIN_EXIST":
        result["code"] = 20200
    elif status == "CREATED":
        result["code"] = 20000
        status_code = 201
    elif status == "CERTIFY_FAILED":
        result["code"] = 30000
    elif status == "AGGREGATE_NOT_ALLOWED":
        result["code"] = 30001
    elif status == "DEPEND_NOT_ALLOWED":
        result["code"] = 30002
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
    return User.query.filter_by(email=value.lower()).first() is not None

def exist_username(value):
    return User.query.filter_by(username=value).first() is not None

def exist_nickname(value):
    return User.query.filter_by(nickname=value).first() is not None

def exist_domain(value):
    return Domain.query.filter_by(title=value).first() is not None

def validate_email(email, length):
    pattern = r'^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)\
                |(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]\
                {1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
    return len(email) <= length or re.match(pattern, email)

def validate_username(name, length):
    return len(name) <= length

def validate_password(password, length):
    pattern = r'^(?=.*?[a-zA-Z])(?=.*?[0-9])(?=.*?[!@#\$&*~]).{6,}$'
    return len(password) <= length or re.match(pattern, password)

def validate_number(number):
    pattern = r'^[1-9][0-9\.]*$'
    return re.match(pattern, number)