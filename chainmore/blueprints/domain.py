# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api, Resource

from ..utils import (response)
from ..models import (Domain, Depend, Aggregate)
from ..extensions import db
from ..decorators import admin_required, permission_required

domain_bp = Blueprint('domain', __name__)
api = Api(domain_bp)


class DomainInstance(Resource):
    def get(self):
        id = request.args.get('id')
        r = Domain.query.get_or_404(id)
        return response('OK', items=[r.s])

    # Cost: 5
    @jwt_required
    def post(self):
        data = request.get_json()

        kwargs = dict(
            title=data['title'],
            intro=data.get('intro', ''),
            creator_id=current_user.id,
        )
        dependeds = data['dependeds']
        assert (len(dependeds) > 0)

        aggregators = data['aggregators']
        assert (len(aggregators) == 1)

        r = Domain(**kwargs)
        db.session.add(r)
        db.session.commit()

        for depended in dependeds:
            depended = Domain.query.get_or_404(depended)
            assert (depended.is_certified(current_user))
            depended.dep(r)
        for aggregator in aggregators:
            aggregator = Domain.query.get_or_404(aggregator)
            assert (aggregator.is_certified(current_user))
            aggregator.agg(r)

        db.session.commit()
        return response('OK', items=[r.s])

    # Cost: 10
    @jwt_required
    def put(self):
        r = Collection.query.get_or_404(data['id'])
        r.title = data['title']
        r.intro = data.get('intro', '')

        new_dependeds = set(data['dependeds'])
        assert (len(new_dependeds) > 0)

        new_aggregators = set(data['aggregators'])
        assert (len(new_aggregators) == 1)

        old_dependeds = set(
            [dep.id for dep in r.dependeds.filter_by(distance=1).all()])
        r.dependeds.filter(
            Depend.descendant_id._in(old_dependeds - new_dependeds)).delete(
                synchronize_session=False)
        for depended in new_dependeds - old_dependeds:
            depended = Domain.query.get_or_404(depended)
            assert (depended.is_certified(current_user))
            depended.dep(r)

        old_aggregators = set(
            [agg.id for agg in r.aggregators.filter_by(distance=1).all()])
        r.aggregators.filter(
            Aggregate.descendant_id._in(old_aggregators -
                                        new_aggregators)).delete(
                                            synchronize_session=False)
        for aggregator in new_aggregators - old_aggregators:
            aggregator = Domain.query.get_or_404(aggregator)
            assert (aggregator.is_certified(current_user))
            aggregator.agg(r)

        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        id = request.args.get('id')
        r = Resource.query.get_or_404(id)
        assert (r.author_id == current_user.id)
        r.deleting = True
        return response('OK', items=[r.s])


class DomainWatch(Resource):
    @jwt_required
    def post(self):
        data = request.get_json()
        domain = Domain.query.get_or_404(data['id'])
        current_user.watch(domain)
        return response('OK')

    @jwt_required
    def delete(self):
        id = request.args.get('id')
        domain = Domain.query.get_or_404(id)
        current_user.unwatch(domain)
        return response('OK')


class DomainCollections(Resource):
    def get(self):
        id = request.args.get('id')
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        order = request.args.get('order')

        domain = Domain.query.get_or_404(id)

        if order == 'time_desc':
            order_by = Collection.timestamp.desc()
        elif order == 'time_incr':
            order_by = Collection.timestamp.incr()
        elif order == 'collect':
            order_by = Collection.collectors.count()
        else:
            order_by = Collection.timestamp.desc()

        collections = Collection.query.filter(
            Collection.domain_id.in_([
                agg.descendant_id for agg in domain.aggregateds
            ])).order_by(order_by).paginate(offset, limit).items

        rs = [collection.s for collection in collections]
        return response("OK", items=rs)


# class DomainCerification(Resource):
#     @jwt_required
#     def get(self):
#         id = request.args.get('id', '').strip()
#         try:
#             id = int(id)
#         except:
#             return response("BAD_REQUEST")

#         domain = Domain.query.get_or_404(id)
#         rules = domain.get_rules()

#         return response("OK", items=rules)

#     @jwt_required
#     def post(self):
#         data = request.get_json()
#         if data is None:
#             return response("EMPTY_BODY", msg="Empty Body")
#         domain = data.get("domain", None)
#         domain = Domain.query.get_or_404(domain)
#         domain_rules = domain.rules
#         rules = data.get("rules", None)
#         if rules is None:
#             return response("EMPTY_BODY", msg="Empty Body")
#         for domain_rule in domain_rules:
#             replied_rule = rules.get(str(domain_rule.id), None)
#             if replied_rule is None:
#                 return response("BAD_REQUEST")
#             if replied_rule["type"] != domain_rule.type:
#                 return response("BAD_REQUEST")
#             if replied_rule["type"] == "choiceproblem":
#                 for replied_choiceproblem in replied_rule["choiceproblems"]:
#                     choiceproblem = domain_rule.choiceproblems.filter_by(
#                         id=replied_choiceproblem["id"]).first()
#                     if choiceproblem is None:
#                         return response("BAD_REQUEST")
#                     if not choiceproblem.check_answer(
#                             replied_choiceproblem["answer"]):
#                         return response("CERTIFY_FAILED")
#         domain.certify(current_user)
#         return response("OK", msg="Certified")

#     @jwt_required
#     def delete(self):
#         try:
#             id = int(request.args.get('id', '').strip())
#         except:
#             return response("BAD_REQUEST")

#         domain = Domain.query.get_or_404(id)
#         domain.uncertify(current_user)
#         return response("OK", msg="Certified")

# class DomainHot(Resource):
#     @jwt_required
#     def get(self):
#         domains = Domain.query.paginate(1, 10).items
#         domains = [
#             domain.serialize(level=1, user=current_user, depended=True)
#             for domain in domains
#         ]
#         return response("OK", items=domains)


class DomainAggregators(Resource):
    @jwt_required
    @admin_required
    def get(self):
        id = request.args.get('id')
        distances = request.args.get('distances', [0, 999999])
        domain = Domain.query.get_or_404(id)
        rs = [
            agg.s for agg in Aggregate.query.filter(
                Aggregate.descendant_id == domain.id, Aggregate.distance >=
                distances[0], Aggregate.distance <= distances[1]).all()
        ]
        return response('OK', items=rs)


class DomainAggregateds(Resource):
    @jwt_required
    @admin_required
    def get(self):
        id = request.args.get('id')
        distances = request.args.get('distances', [0, 999999])
        domain = Domain.query.get_or_404(id)
        rs = [
            agg.s for agg in Aggregate.query.filter(
                Aggregate.ancestor_id == domain.id, Aggregate.distance >=
                distances[0], Aggregate.distance <= distances[1]).all()
        ]
        return response('OK', items=rs)


class DomainDependeds(Resource):
    @jwt_required
    @admin_required
    def get(self):
        id = request.args.get('id')
        distances = request.args.get('distances', [0, 999999])
        domain = Domain.query.get_or_404(id)
        rs = [
            dep.s for dep in Depend.query.filter(
                Depend.descendant_id == domain.id, Depend.distance >=
                distances[0], Depend.distance <= distances[1]).all()
        ]
        return response('OK', items=rs)


class DomainDependants(Resource):
    @jwt_required
    @admin_required
    def get(self):
        id = request.args.get('id')
        distances = request.args.get('distances', [0, 999999])
        domain = Domain.query.get_or_404(id)
        rs = [
            dep.s for dep in Depend.query.filter(
                Depend.ancestor_id == domain.id, Depend.distance >=
                distances[0], Depend.distance <= distances[1]).all()
        ]
        return response('OK', items=rs)


# class RoadMapInstance(Resource):
#     @jwt_required
#     def post(self):
#         data = request.get_json()
#         try:
#             title = data["title"]
#             intro = data.get("intro", "")
#             heads = data["heads"]
#         except:
#             return response("BAD_REQUEST")

#         roadmap = RoadMap(title=title, intro=intro, creator=current_user)
#         roadmap.head(heads)

#         return response("OK")

#     def get(self):
#         try:
#             roadmap = RoadMap.query.get_or_404(request.args["roadmap"])
#         except:
#             return response("BAD_REQUEST")

#         return response("OK", roadmap=roadmap.serialize(level=1))

#     @jwt_required
#     def delete(self):
#         try:
#             roadmap = RoadMap.query.get_or_404(request.args["roadmap"])
#         except:
#             return response("BAD_REQUEST")
#         return response("OK")

#     @jwt_required
#     def put(self):
#         data = request.get_json()
#         try:
#             roadmap = RoadMap.query.get_or_404(data["roadmap"])
#             title = data.get("title", None)
#             intro = data.get("intro", None)
#             heads = data.get(heads, None)
#         except:
#             return response("BAD_REQUEST")

#         if title is not None:
#             roadmap.title = title
#         if intro is not None:
#             roadmap.intro = intro
#         if heads is not None:
#             roadmap.update_head(heads)
#         return response("OK")

# class RoadMapLearn(Resource):
#     @jwt_required
#     def post(self):
#         try:
#             roadmap = RoadMap.query.get_or_404(request.args["roadmap"])
#         except:
#             return response("BAD_REQUEST")

#         current_user.learn(roadmap)

#         return response("OK")

#     @jwt_required
#     def delete(self):
#         try:
#             roadmap = RoadMap.query.get_or_404(request.args["roadmap"])
#         except:
#             return response("BAD_REQUEST")

#         current_user.unlearn(roadmap)

#         return response("OK")

api.add_resource(DomainInstance, '')
api.add_resource(DomainWatch, '/watch')
api.add_resource(DomainCollections, '/collections')
# api.add_resource(DomainCerification, '/certify')
# api.add_resource(DomainHot, '/hot')
api.add_resource(DomainAggregators, '/aggregators')
api.add_resource(DomainAggregateds, '/aggregateds')
api.add_resource(DomainDependeds, '/dependeds')
api.add_resource(DomainDependants, '/dependants')
# api.add_resource(RoadMapInstance, '/roadmap')
# api.add_resource(RoadMapLearn, '/roadmap/learn')
