# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api, Resource

from ..utils import (response)
from ..models import (Domain, RoadMap)
from ..extensions import db

domain_bp = Blueprint('domain', __name__)
api = Api(domain_bp)


class DomainInstance(Resource):
    @jwt_required
    def post(self):
        data = request.get_json()
        if data is None:
            return response("EMPTY_BODY", msg="Empty Body")
        title = data.get("title", None)
        intro = data.get("intro", "")
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
            intro=intro,
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
    def put(self):
        data = request.get_json()
        if data is None:
            return response("EMPTY_BODY", msg="Empty Body")
        title = data.get("title", None)
        intro = data.get("intro", None)
        bio = data.get("bio", None)
        try:
            depended_domain = Domain.query.get_or_404(int(data["depended"]))
            aggregator_domain = Domain.query.get_or_404(int(
                data["aggregator"]))
            domain = Domain.query.get_or_404(int(data["domain"]))
        except:
            return response("BAD_REQUEST")

        if title is not None:
            domain.title = title
        if intro is not None:
            domain.intro = intro
        if bio is not None:
            domain.bio = bio

        if depended_domain.id in domain.depdomains():
            return response("DEPEND_NOT_ALLOWED")
        domain.update_dependeds([depended_domain.id])
        if aggregator_domain.id in domain.subdomains():
            return response("AGGREGATE_NOT_ALLOWED")
        domain.update_aggregator(aggregator_domain)

        db.session.commit()

        return response("OK", msg="Domain Updated")

    @jwt_required
    def get(self):
        try:
            id = int(request.args.get('id', '').strip())
        except:
            return response("BAD_REQUEST")

        domain = Domain.query.get_or_404(id)
        result = domain.serialize(level=0, user=current_user)
        return response("OK", item=result)


class DomainWatch(Resource):
    @jwt_required
    def post(self):
        try:
            id = int(request.args.get('id', '').strip())
        except:
            return response("BAD_REQUEST")
        domain = Domain.query.get_or_404(id)
        current_user.watch(domain)
        return response("OK", msg="Domain watched")

    @jwt_required
    def delete(self):
        try:
            id = int(request.args.get('id', '').strip())
        except:
            return response("BAD_REQUEST")
        domain = Domain.query.get_or_404(id)
        current_user.unwatch(domain)
        return response("OK", msg="Domain unwatched")


class DomainPost(Resource):
    def get(self):
        try:
            id = int(request.args.get('id', '').strip())
            offset = int(request.args.get('offset', 1))
            limit = int(request.args.get('limit', 5))
        except:
            return response("BAD_REQUEST")
        domain = Domain.query.get_or_404(id)
        subdomains = [id]
        subdomains.extend(domain.subdomains())
        posts = Post.query.filter(Post.domain_id.in_(subdomains))\
            .order_by(Post.timestamp.desc()).paginate(offset, limit).items

        posts = [post.serialize(level=1) for post in posts]
        return response("OK", items=posts)


class DomainCerification(Resource):
    @jwt_required
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
        if (domain.id == 1):
            current_user.root_certified = True
            db.session.commit()
        return response("OK", msg="Certified")

    @jwt_required
    def delete(self):
        try:
            id = int(request.args.get('id', '').strip())
        except:
            return response("BAD_REQUEST")

        domain = Domain.query.get_or_404(id)
        domain.uncertify(current_user)
        return response("OK", msg="Certified")


class DomainHot(Resource):
    @jwt_required
    def get(self):
        domains = Domain.query.paginate(1, 10).items
        domains = [
            domain.serialize(level=1, user=current_user, depended=True)
            for domain in domains
        ]
        return response("OK", items=domains)


class DomainAggregate(Resource):
    @jwt_required
    def get(self):
        try:
            id = int(request.args.get('id', '').strip())
        except:
            return response("BAD_REQUEST")

        domain = Domain.query.get_or_404(id)
        aggregate = domain.aggregate_structures()
        return response("OK", aggregate=aggregate)


class DomainDependent(Resource):
    @jwt_required
    def get(self):
        try:
            id = int(request.args.get('id', '').strip())
        except:
            return response("BAD_REQUEST")

        domain = Domain.query.get_or_404(id)
        dependent = domain.dependent_supdomains()
        return response("OK", dependent=dependent)


class RoadMapInstance(Resource):
    @jwt_required
    def post(self):
        data = request.get_json()
        try:
            title = data["title"]
            intro = data.get("intro", "")
            heads = data["heads"]
        except:
            return response("BAD_REQUEST")

        roadmap = RoadMap(title=title, intro=intro, creator=current_user)
        roadmap.head(heads)

        return response("OK")

    def get(self):
        try:
            roadmap = RoadMap.query.get_or_404(request.args["roadmap"])
        except:
            return response("BAD_REQUEST")

        return response("OK", roadmap=roadmap.serialize(level=1))

    @jwt_required
    def delete(self):
        try:
            roadmap = RoadMap.query.get_or_404(request.args["roadmap"])
        except:
            return response("BAD_REQUEST")
        return response("OK")

    @jwt_required
    def put(self):
        data = request.get_json()
        try:
            roadmap = RoadMap.query.get_or_404(data["roadmap"])
            title = data.get("title", None)
            intro = data.get("intro", None)
            heads = data.get(heads, None)
        except:
            return response("BAD_REQUEST")

        if title is not None:
            roadmap.title = title
        if intro is not None:
            roadmap.intro = intro
        if heads is not None:
            roadmap.update_head(heads)
        return response("OK")


class RoadMapLearn(Resource):
    @jwt_required
    def post(self):
        try:
            roadmap = RoadMap.query.get_or_404(request.args["roadmap"])
        except:
            return response("BAD_REQUEST")

        current_user.learn(roadmap)

        return response("OK")

    @jwt_required
    def delete(self):
        try:
            roadmap = RoadMap.query.get_or_404(request.args["roadmap"])
        except:
            return response("BAD_REQUEST")

        current_user.unlearn(roadmap)

        return response("OK")


api.add_resource(DomainInstance, '/')
api.add_resource(DomainWatch, '/watch')
api.add_resource(DomainPost, '/post')
api.add_resource(DomainCerification, '/certify')
api.add_resource(DomainHot, '/hot')
api.add_resource(DomainAggregate, '/aggregate')
api.add_resource(DomainDependent, '/dependent')
api.add_resource(RoadMapInstance, '/roadmap')
api.add_resource(RoadMapLearn, '/roadmap/learn')
