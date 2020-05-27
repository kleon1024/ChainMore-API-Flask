from functools import wraps

from flask import Markup, flash, url_for, redirect, abort
from flask_jwt_extended import (jwt_required, current_user)


def permission_required(permission_name):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission_name):
                abort(405)
            return func(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(func):
    return permission_required('ADMINISTER')(func)
