# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api, Resource

from ..utils import (response)
from ..models import (Domain, Post)
from ..extensions import db

domain_bp = Blueprint('domain', __name__)
api = Api(domain_bp)


class DomainInstance(Resource):
    def get(self, id):
        domain = Domain.query.get_or_404(id)
        return response("OK", item=domain.serialize())


class Domains(Resource):
    @jwt_required
    def post(self):
        data = request.get_json()
        if data is None:
            return response("EMPTY_BODY", msg="Empty Body")
        title = data.get("title", None)
        description = data.get("description", "")
        bio = data.get("bio", "人正在关注")
        if title is None:
            return response("BAD_REQUEST", msg="No title provided")
        depended = data.get("depended", None)
        if depended is None:
            return response("BAD_REQUEST", msg="No depended provided")
        aggregator = data.get("aggregator", None)
        if aggregator is None:
            return response("BAD_REQUEST", msg="No aggregator provided")
        try:
            depended = int(depended)
            aggregator = int(aggregator)
        except:
            return response("BAD_REQUEST")

        if Domain.query.filter_by(title=title).first() is not None:
            return response("DOMAIN_EXIST")

        domain = Domain(
            title=title,
            description=description,
            creator_id=current_user.id,
            bio=bio,
        )

        depended_domain = Domain.query.get_or_404(depended)
        aggregator_domain = Domain.query.get_or_404(aggregator)

        depended_domain.add_dependant(domain)
        aggregator_domain.aggregate(domain)

        db.session.add(domain)
        db.session.commit()

        return response("OK", msg="Domain Created")

    @jwt_required
    def get(self):
        id = request.args.get('id', '').strip()
        try:
            id = int(id)
        except:
            return response("BAD_REQUEST")

        domain = Domain.query.get_or_404(id)
        result = domain.serialize(level=0, user=current_user)
        return response("OK", item=result)


class DomainWatch(Resource):
    @jwt_required
    def post(self, id):
        domain = Domain.query.get_or_404(id)
        current_user.watch(domain)
        return response("OK", msg="Domain watched")

    @jwt_required
    def delete(self, id):
        domain = Domain.query.get_or_404(id)
        current_user.unwatch(domain)
        return response("OK", msg="Domain unwatched")


class DomainPost(Resource):
    def get(self):
        id = request.args.get('id', '').strip()
        try:
            id = int(id)
        except:
            return response("BAD_REQUEST")
        domain = Domain.query.get_or_404(id)
        posts = Post.query.with_parent(domain).order_by(
            Post.timestamp.asc()).all()

        posts = [post.serialize(level=1) for post in posts]
        return response("OK", items=posts)


class DomainCerification(Resource):
    def get(self):
        id = request.args.get('id', '').strip()
        try:
            id = int(id)
        except:
            return response("BAD_REQUEST")

        domain = Domain.query.get_or_404(id)
        rules = domain.get_rules()

        return response("OK", items=rules)

    @jwt_required
    def post(self):
        data = request.get_json()
        if data is None:
            return response("EMPTY_BODY", msg="Empty Body")
        domain = data.get("domain", None)
        domain = Domain.query.get_or_404(domain)
        domain_rules = domain.rules
        rules = data.get("rules", None)
        if rules is None:
            return response("EMPTY_BODY", msg="Empty Body")
        for domain_rule in domain_rules:
            replied_rule = rules.get(str(domain_rule.id), None)
            if replied_rule is None:
                return response("BAD_REQUEST")
            if replied_rule["type"] != domain_rule.type:
                return response("BAD_REQUEST")
            if replied_rule["type"] == "choiceproblem":
                for replied_choiceproblem in replied_rule["choiceproblems"]:
                    choiceproblem = domain_rule.choiceproblems.filter_by(
                        id=replied_choiceproblem["id"]).first()
                    if choiceproblem is None:
                        return response("BAD_REQUEST")
                    if not choiceproblem.check_answer(
                            replied_choiceproblem["answer"]):
                        return response("CERTIFY_FAILED")
        domain.certify(current_user)
        return response("OK", msg="Certified")

    @jwt_required
    def delete(self):
        id = request.args.get('id', '').strip()
        try:
            id = int(id)
        except:
            return response("BAD_REQUEST")

        domain = Domain.query.get_or_404(id)
        domain.uncertify(current_user)
        return response("OK", msg="Certified")


class DomainHot(Resource):
    @jwt_required
    def get(self):
        domains = Domain.query.all()
        if len(domains) >= 10:
            domains = domains[0:9]
        domains = [
            domain.serialize(level=1, user=current_user) for domain in domains
        ]
        return response("OK", items=domains)


api.add_resource(DomainInstance, '/<int:id>')
api.add_resource(Domains, '')
api.add_resource(DomainWatch, '/<int:id>/watch')
api.add_resource(DomainPost, '/post')
api.add_resource(DomainCerification, '/certify')
api.add_resource(DomainHot, '/hot')
