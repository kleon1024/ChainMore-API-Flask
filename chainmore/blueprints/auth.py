# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import datetime

from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import (create_access_token, 
                                create_refresh_token)

from ..extensions import db, jwt

auth_bp = Blueprint('auth', __name__)

