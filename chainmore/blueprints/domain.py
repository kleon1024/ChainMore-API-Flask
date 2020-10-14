# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api, Resource

from ..utils import (response, merge)
from ..models import (
    Domain, Depend, Aggregate, Collection, Order, Mark,
    Collect,
    CertificationGroup, Certification, MultipleChoiceProblem, MultipleChoice,
    CertificationType, MultipleChoiceProblemType, DIGEST_LENGTH)
from ..extensions import db
from ..decorators import admin_required, permission_required

domain_bp = Blueprint('domain', __name__)
api = Api(domain_bp)


class Domains(Resource):
    # @jwt_required
    # @admin_required
    def get(self):
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 1))
        items = [d.s for d in Domain.query.order_by(
            Domain.modify_time.desc()).paginate(offset, limit).items]
        return response('OK', items=items)


class DomainMarked(Resource):
    @jwt_required
    def get(self):
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 1))
        order = request.args.get('order', Order.time_desc.value)
        if order == Order.time_desc.value:
            order_by = Mark.timestamp.desc()
        elif order == Order.time_asc.value:
            order_by = Mark.timestamp.asc()
        else:
            order_by = Mark.timestamp.desc()
        items = [merge(mark.domain.s, mark.s) for mark in
                 current_user.markeds.order_by(order_by).paginate(offset, limit).items]
        return response('OK', items=items)


class DomainCreated(Resource):
    @jwt_required
    def get(self):
        items = [domain.s for domain in
                 current_user.domains]
        return response('OK', items=items)


class DomainMark(Resource):
    @jwt_required
    def get(self):
        id = request.args['id']
        r = Domain.query.get_or_404(id)
        items = []
        if current_user.is_marking(r):
            items.append(r.s)
        return response('OK', items=items)

    @jwt_required
    def post(self):
        data = request.get_json()
        r = Domain.query.get_or_404(data['id'])
        current_user.mark(r)
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        id = request.args.get('id')
        r = Domain.query.get_or_404(id)
        current_user.unmark(r)
        return response('OK', items=[r.s])


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
        assert len(dependeds) > 0

        aggregators = data['aggregators']
        assert len(aggregators) == 1

        certified_dependeds = []
        for depended in dependeds:
            depended = Domain.query.get_or_404(depended)
            # assert depended.is_certified(current_user)
            certified_dependeds.append(depended)

        certified_aggregators = []
        for aggregator in aggregators:
            aggregator = Domain.query.get_or_404(aggregator)
            # assert aggregator.is_certified(current_user)
            certified_aggregators.append(aggregator)

        r = Domain(**kwargs)
        db.session.add(r)
        db.session.commit()

        depend_map = {}

        for depended in certified_dependeds:
            for depended in Depend.query.filter(
                    Depend.descendant_id == depended.id).all():
                key = (depended.ancestor_id, r.id)
                if key not in depend_map:
                    d = Depend(ancestor_id=depended.ancestor_id,
                               descendant_id=r.id,
                               distance=depended.distance + 1)
                    depend_map[key] = dict(
                        distance=depended.distance + 1,
                        depend=d
                    )
                    db.session.add(d)
                else:
                    value = depend_map[key]
                    if value['distance'] < depended.distance + 1:
                        value['depend'].distance = depended.distance + 1

        db.session.add(
            Depend(ancestor_id=r.id,
                   descendant_id=r.id,
                   distance=0))

        aggregate_map = {}

        for aggregator in certified_aggregators:
            for aggregator in Aggregate.query.filter(
                    Aggregate.descendant_id == aggregator.id):
                key = (aggregator.ancestor_id, r.id)
                if key not in aggregate_map:
                    a = Aggregate(ancestor_id=aggregator.ancestor_id,
                                  descendant_id=r.id,
                                  distance=aggregator.distance + 1)
                    aggregate_map[key] = dict(
                        distance=aggregator.distance + 1,
                        aggregate=a
                    )
                    db.session.add(a)
                else:
                    value = aggregate_map[key]
                    if value['distance'] < aggregator.distance + 1:
                        value['aggregate'].distance = aggregator.distance + 1

        db.session.add(
            Aggregate(ancestor_id=r.id,
                      descendant_id=r.id,
                      distance=0))

        db.session.commit()
        return response('OK', items=[r.s])

    # Cost: 100
    @jwt_required
    def put(self):
        data = request.get_json()

        r = Domain.query.get_or_404(data['id'])
        r.title = data['title']
        r.intro = data.get('intro', '')
        r.modify_time = datetime.utcnow()

        new_dependeds = set(data['dependeds'])
        assert len(new_dependeds) > 0

        new_aggregators = set(data['aggregators'])
        assert len(new_aggregators) == 1

        certified_dependeds = set()
        for depended in new_dependeds:
            depended = Domain.query.get_or_404(depended)
            # assert depended.is_certified(current_user)
            certified_dependeds.add(depended.id)

        certified_aggregators = set()
        for aggregator in new_aggregators:
            aggregator = Domain.query.get_or_404(aggregator)
            # assert aggregator.is_certified(current_user)
            certified_aggregators.add(aggregator.id)

        assert Depend.query.filter(
            Depend.ancestor_id == r.id,
            Depend.descendant_id.in_(
                certified_dependeds)).first() is None

        assert Aggregate.query.filter(
            Aggregate.ancestor_id == r.id,
            Aggregate.descendant_id.in_(
                certified_aggregators)).first() is None

        old_dependeds = set(
            [dep.ancestor_id for dep in r.dependeds.filter_by(distance=1).all()])
        removable_dependeds = old_dependeds - certified_dependeds

        for removable_depended in removable_dependeds:
            for (ancestor_id, ancestor_distance) in [(dep.ancestor_id, dep.distance) for dep in Depend.query.filter(
                    Depend.descendant_id == removable_depended).all()]:
                for (descendant_id, descendant_distance) in [(dep.descendant_id, dep.distance) for dep in r.dependants]:
                    d = Depend.query.filter(
                        Depend.ancestor_id == ancestor_id,
                        Depend.descendant_id == descendant_id,
                        Depend.distance == ancestor_distance + descendant_distance + 1).first()
                    if d is not None:
                        db.session.delete(d)
        db.session.commit()

        addable_dependeds = certified_dependeds - old_dependeds
        for depended in addable_dependeds:
            for ancestor_id, ancestor_distance in [(dep.ancestor_id, dep.distance) for dep in Depend.query.filter(
                Depend.descendant_id == depended
            ).all()]:
                for descendant_id, descendant_distance in [(dep.descendant_id, dep.distance) for dep in r.dependants]:
                    old_d = Depend.query.filter(
                        Depend.ancestor_id == ancestor_id,
                        Depend.descendant_id == descendant_id).order_by(Depend.distance.desc()).first()
                    if old_d is not None:
                        distance = 1
                        if ancestor_id in addable_dependeds:
                            distance += descendant_distance
                        else:
                            distance += ancestor_distance + descendant_distance
                        if old_d.distance < distance:
                            old_d.distance = distance
                    else:
                        distance = 1
                        if ancestor_id in addable_dependeds:
                            distance += descendant_distance
                        else:
                            distance += ancestor_distance + descendant_distance
                        d = Depend(ancestor_id=ancestor_id, descendant_id=descendant_id,
                                   distance=distance)
                        db.session.add(d)

        old_aggregators = set(
            [agg.ancestor_id for agg in r.aggregators.filter_by(distance=1).all()])
        removable_aggregates = old_aggregators - certified_aggregators
        for removable_aggregate in removable_aggregates:
            for (ancestor_id, ancestor_distance) in [(agg.ancestor_id, agg.distance) for agg in Aggregate.query.filter(
                    Aggregate.descendant_id == removable_aggregate).all()]:
                for (descendant_id, descendant_distance) in [(agg.descendant_id, agg.distance) for agg in r.aggregateds]:
                    d = Aggregate.query.filter(
                        Aggregate.ancestor_id == ancestor_id,
                        Aggregate.descendant_id == descendant_id,
                        Aggregate.distance == ancestor_distance + descendant_distance + 1).first()
                    if d is not None:
                        db.session.delete(d)
        db.session.commit()

        for aggregate in certified_aggregators - old_aggregators:
            for ancestor_id, ancestor_distance in [(agg.ancestor_id, agg.distance) for agg in Aggregate.query.filter(
                Aggregate.descendant_id == aggregate
            ).all()]:
                for descendant_id, descendant_distance in [(agg.descendant_id, agg.distance) for agg in r.aggregateds]:
                    old_a = Aggregate.query.filter(
                        Aggregate.ancestor_id == ancestor_id,
                        Aggregate.descendant_id == descendant_id).order_by(Aggregate.distance.desc()).first()
                    if old_a is not None:
                        if old_a.distance < ancestor_distance + descendant_distance + 1:
                            old_a.distance = ancestor_distance + descendant_distance + 1
                    else:
                        a = Aggregate(ancestor_id=ancestor_id, descendant_id=descendant_id,
                                      distance=ancestor_distance + descendant_distance + 1)
                        db.session.add(a)

        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        id = request.args.get('id')
        r = Domain.query.get_or_404(id)
        assert (r.author_id == current_user.id)
        r.deleting = True
        db.session.commit()
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
        offset = int(request.args.get('offset', 1))
        limit = int(request.args.get('limit', 10))
        order = request.args.get('order', 'time_desc')

        domain = Domain.query.get_or_404(id)

        if order == 'time_desc':
            order_by = Collection.modify_time.desc()
        elif order == 'time_asc':
            order_by = Collection.modify_time.asc()
        elif order == 'collect_count':
            order_by = Collection.collectors.count()
        else:
            order_by = Collection.modify_time.desc()

        aggs = [agg.descendant_id for agg in domain.aggregateds]

        collections = Collection.query.filter(
            Collection.domain_id.in_(aggs)).order_by(order_by).paginate(offset, limit).items

        rs = [collection.s for collection in collections]
        return response("OK", items=rs, aggs=aggs)


class DomainUserCollections(Resource):
    @jwt_required
    def get(self):
        domain = request.args.get('domain')
        domain = Domain.query.get_or_404(domain)

        rs = [c.collected.s for c in Collect.query.join(
                Collection, Collect.collected_id == Collection.id).filter(
                    Collect.collector_id == current_user.id,
                    Collection.domain_id == domain.id
                ).all()]

        return response('OK', items=rs)

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

class DomainNotInAggregateds(Resource):
    @jwt_required
    def post(self):
        data = request.get_json
        domain = Domain.quey.get_or_404(data['id'])
        agg_domains = [d.id for d in [
            Domain.quey.get_or_404(id) for id in data['aggregators']]]
        rs = [d.s for d in Aggregate.query.filter(Aggregate.ancestor_id == domain.id,
                                                  Aggregate.descendant_id.in_(agg_domains)).all()]
        return response('OK', items=rs)


class DomainNotInDependants(Resource):
    @jwt_required
    def post(self):
        data = request.get_json
        domain = Domain.quey.get_or_404(data['id'])
        dep_domains = [d.id for d in [
            Domain.quey.get_or_404(id) for id in data['dependeds']]]
        rs = [d.s for d in Depend.query.filter(Depend.ancestor_id == domain.id,
                                               Depend.descendant_id.in_(dep_domains)).all()]
        return response('OK', items=rs)


class DomainAggregators(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        distance = request.args.get('distance', 1)
        lower_distance = request.args.get('lower', 0)
        domain = Domain.query.get_or_404(id)
        rs = [
            agg.s for agg in Aggregate.query.filter(Aggregate.descendant_id == domain.id,
                                                    Aggregate.distance >= lower_distance,
                                                    Aggregate.distance <= distance).
            order_by(Aggregate.distance.desc()).all()
        ]
        return response('OK', items=rs)


class DomainAggregateds(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        distance = request.args.get('distance', 1)
        lower_distance = request.args.get('lower', 0)
        domain = Domain.query.get_or_404(id)
        rs = [
            agg.s for agg in Aggregate.query.filter(Aggregate.ancestor_id == domain.id,
                                                    Aggregate.distance >= lower_distance,
                                                    Aggregate.distance <= distance).
            order_by(Aggregate.distance.asc()).all()
        ]
        return response('OK', items=rs)


class DomainInstanceAggregators(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        distance = request.args.get('distance', 1)
        lower_distance = request.args.get('lower', 0)
        domain = Domain.query.get_or_404(id)
        rs = [
            agg.ancestor.s for agg in Aggregate.query.filter(Aggregate.descendant_id == domain.id,
                                                             Aggregate.distance >= lower_distance,
                                                             Aggregate.distance <= distance).
            order_by(Aggregate.distance.desc()).all()
        ]
        return response('OK', items=rs)


class DomainInstanceAggregateds(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        distance = request.args.get('distance', 1)
        lower_distance = request.args.get('lower', 0)
        domain = Domain.query.get_or_404(id)
        rs = [
            agg.descendant.s for agg in Aggregate.query.filter(Aggregate.ancestor_id == domain.id,
                                                               Aggregate.distance >= lower_distance,
                                                               Aggregate.distance <= distance).
            order_by(Aggregate.distance.asc()).all()
        ]
        return response('OK', items=rs)


class DomainAggregate(Resource):
    # @jwt_required
    # @admin_required
    def get(self):
        rs = [agg.s for agg in Aggregate.query.filter(
            Aggregate.distance == 1).all()]
        return response('OK', items=rs)


class DomainDependeds(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        distance = request.args.get('distance', 1)
        lower_distance = request.args.get('lower', 0)
        domain = Domain.query.get_or_404(id)
        rs = [
            dep.s
            for dep in Depend.query.filter(Depend.descendant_id == domain.id,
                                           Depend.distance >= lower_distance,
                                           Depend.distance <= distance).
            order_by(Depend.distance.desc()).all()
        ]
        return response('OK', items=rs)


class DomainDependants(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        distance = request.args.get('distance', 1)
        lower_distance = request.args.get('lower', 0)
        domain = Domain.query.get_or_404(id)
        rs = [
            dep.s
            for dep in Depend.query.filter(Depend.ancestor_id == domain.id,
                                           Depend.distance >= lower_distance,
                                           Depend.distance <= distance).
            order_by(Depend.distance.asc()).all()
        ]
        return response('OK', items=rs)


class DomainInstanceDependeds(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        distance = request.args.get('distance', 1)
        lower_distance = request.args.get('lower', 0)
        domain = Domain.query.get_or_404(id)
        certified_domains = [c.certified_id for c in current_user.certifieds.all()]
        skipped_domains = set([dep.ancestor_id for dep in Depend.query.filter(
            Depend.descendant_id.in_(certified_domains)).all()])
        recommend_domains = set([dep.descendant_id for dep in Depend.query.filter(
            Depend.ancestor_id.in_(certified_domains),
            Depend.distance == 1).all()])
        rs = [
            merge(dep.ancestor.s,
                  (dict(certified=dep.ancestor.is_certified(current_user),
                  recommend=dep.ancestor_id in recommend_domains,
                  skip=dep.ancestor_id in skipped_domains)))
            for dep in Depend.query.filter(Depend.descendant_id == domain.id,
                                           Depend.distance >= lower_distance,
                                           Depend.distance <= distance).
            order_by(Depend.distance.desc()).all()
        ]
        return response('OK', items=rs)


class DomainInstanceDependants(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        distance = request.args.get('distance', 1)
        lower_distance = request.args.get('lower', 0)
        domain = Domain.query.get_or_404(id)
        rs = [
            dep.descendant.s
            for dep in Depend.query.filter(Depend.ancestor_id == domain.id,
                                           Depend.distance >= lower_distance,
                                           Depend.distance <= distance).
            order_by(Depend.distance.asc()).all()
        ]
        return response('OK', items=rs)


class DomainDepend(Resource):
    # @jwt_required
    # @admin_required
    def get(self):
        rs = [dep.s for dep in Depend.query.filter(
            Depend.distance == 1).all()]
        return response('OK', items=rs)


class DomainRootDepend(Resource):
    def get(self):
        rs = [
            dep.s for dep in Depend.query.filter(
                Depend.ancestor_id == 1
            ).order_by(Depend.distance.asc()).all()
        ]
        return response('OK', items=rs)


class DomainDepends(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        domain = Domain.query.get_or_404(id)
        exist_ids = [
            certify.certified_id for certify in current_user.certifieds
        ]
        exclude_domains = set([
            dep.ancestor_id for dep in Depend.query.filter(
                Depend.descendant_id.in_(exist_ids)).all()
        ])

        rs = [
            dep.ancestor.s for dep in Depend.query.filter(
                Depend.descendant_id == domain.id, ~Depend.ancestor_id.in_(
                    exclude_domains)).order_by(Depend.distance.desc()).all()
        ]

        ol = {}
        for r in rs:
            if r['id'] not in ol:
                ol[r['id']] = r

        rs = list(ol.values())
        return response('OK', items=rs)


class DomainCertificationGroups(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        domain = Domain.query.get_or_404(id)
        rs = [merge(cg.s, dict(finished=cg.is_finished(current_user)))
              for cg in domain.certification_groups]
        return response('OK', items=rs)


class DomainCertificationGroupInstance(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        group = CertificationGroup.query.get_or_404(id)
        return response('OK', items=[group.s])

    @jwt_required
    def post(self):
        data = request.get_json()

        domain_id = data['domain']
        domain = Domain.query.get_or_404(domain_id)

        kwargs = dict(
            title=data['title'],
            intro=data.get('intro', ''),
            domain_id=domain.id,
        )

        r = CertificationGroup(**kwargs)
        db.session.add(r)
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def put(self):
        data = request.get_json()

        id = data['id']
        g = CertificationGroup.query.get_or_404(id)
        if 'title' in data:
            g.title = data['title']
        if 'intro' in data:
            g.intro = data['intro']
        if 'domain' in data:
            domain = Domain.query.get_or_404(data['domain'])
            g.domain_id = domain.id
        g.modify_time = datetime.utcnow()
        db.session.commit()
        return response('OK', items=[g.s])

    @jwt_required
    def delete(self):
        id = request.args.get('id')
        g = CertificationGroup.query.get_or_404(id)
        db.session.delete(g)
        db.session.commit()
        return response('OK', items=[g.s])


class DomainCertifications(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        group = CertificationGroup.query.get_or_404(id)
        rs = [c.s for c in group.certifications]
        return response('OK', items=rs)


class DomainManageCertifications(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        group = CertificationGroup.query.get_or_404(id)
        assert group.domain.is_certified(current_user)

        rs = [c.ss for c in group.certifications]
        return response('OK', items=rs)


class DomainCertificationInstance(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        c = Certification.query.get_or_404(id)
        return response('OK', items=[c.s])

    @jwt_required
    def post(self):
        data = request.get_json()

        kwargs = dict()
        group_id = data['group']
        group = CertificationGroup.query.get_or_404(group_id)

        kwargs['certification_group_id'] = group.id

        t = data['type']
        if t == CertificationType.MCP.value:
            mcp_id = data['mcp']
            mcp = MultipleChoiceProblem.query.get_or_404(mcp_id)
            kwargs['mcp_id'] = mcp.id
            kwargs['digest'] = mcp.text[:DIGEST_LENGTH]
            kwargs['type'] = t
        else:
            return response('BAD_REQUEST')

        r = Certification(**kwargs)
        db.session.add(r)
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def put(self):
        data = request.get_json()

        id = data['id']
        g = Certification.query.get_or_404(id)
        if 'group' in data:
            group_id = data['group']
            group = CertificationGroup.query.get_or_404(group_id)
            g.certification_group_id = group.id
        if 'digest' in data:
            g.digest = data['digest']
        if 'type' in data:
            t = data['type']
            if t == CertificationType.MCP.value:
                mcp_id = data['mcp']
                mcp = MultipleChoiceProblem.query.get_or_404(mcp_id)
                g.mcp_id = mcp.id
                g.type = t
            else:
                return response('BAD_REQUEST')
        g.modify_time = datetime.utcnow()

        db.session.commit()
        return response('OK', items=[g.s])

    @jwt_required
    def delete(self):
        id = request.args.get('id')
        r = Certification.query.get_or_404(id)

        if r.type == CertificationType.MCP.value:
            for c in r.mcp.choices:
                db.session.delete(c)
            db.session.delete(r.mcp)

        db.session.delete(r)
        db.session.commit()
        return response('OK', items=[r.s])


class DomainMCPInstance(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        mcp = MultipleChoiceProblem.query.get_or_404(id)
        return response('OK', items=[mcp.s])

    @jwt_required
    def post(self):
        data = request.get_json()

        text = data['text']
        t = data.get('type', MultipleChoiceProblemType.ANY_ANSWER.value)

        assert t in [
            MultipleChoiceProblemType.SINGLE_ANSWER.value,
            MultipleChoiceProblemType.MULTIPLE_ANSWER.value,
            MultipleChoiceProblemType.ANY_ANSWER.value,
        ]

        kwargs = dict(
            text=text,
            type=t
        )

        r = MultipleChoiceProblem(**kwargs)
        db.session.add(r)
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def put(self):
        data = request.get_json()

        id = data['id']
        r = MultipleChoiceProblem.query.get_or_404(id)

        if 'text' in data:
            r.text = data['text']
            r.certification.digest = r.text[:DIGEST_LENGTH]
        if 'type' in data:
            t = data['type']
            assert t in [
                MultipleChoiceProblemType.SINGLE_ANSWER.value,
                MultipleChoiceProblemType.MULTIPLE_ANSWER.value,
                MultipleChoiceProblemType.ANY_ANSWER.value,
            ]
            r.type = t

        r.modify_time = datetime.utcnow()

        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        id = request.args.get('id')

        r = MultipleChoiceProblem.query.get_or_404(id)
        db.session.delete(r)
        db.session.commit()
        return response('OK', items=[r.s])


class DomainMCPChoices(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        mcp = MultipleChoiceProblem.query.get_or_404(id)
        rs = [choice.s for choice in mcp.choices]
        return response('OK', items=rs)


class DomainMCPChoiceInstance(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        r = MultipleChoice.query.get_or_404(id)
        return response('OK', items=[r.s])

    @jwt_required
    def post(self):
        data = request.get_json()

        mcp_id = data.get('mcp')
        mcp = MultipleChoiceProblem.query.get_or_404(mcp_id)

        answer = data.get('answer', False)

        kwargs = dict(
            text=data['text'],
            choice_problem_id=mcp.id,
        )

        if answer:
            kwargs['answer_problem_id'] = mcp.id

        r = MultipleChoice(**kwargs)
        db.session.add(r)
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def put(self):
        data = request.get_json()

        id = data['id']
        r = MultipleChoice.query.get_or_404(id)

        if 'text' in data:
            r.text = data['text']

        if 'mcp' in data:
            mcp_id = data['mcp']
            mcp = MultipleChoiceProblem.query.get_or_404(mcp_id)
            r.choice_problem_id = mcp.id
            if r.answer_problem_id is not None:
                r.answer_problem_id = mcp.id

        if 'answer' in data:
            answer = data['answer']
            if answer:
                r.answer_problem_id = r.choice_problem_id
            else:
                r.answer_problem_id = None

        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        id = request.args.get('id')
        r = MultipleChoice.query.get_or_404(id)
        db.session.delete(r)
        db.session.commit()
        return response('OK', items=[r.s])


class DomainMCPAnwers(Resource):
    @admin_required
    @jwt_required
    def get(self):
        id = request.args.get('id')
        mcp = MultipleChoiceProblem.query.get_or_404(id)
        rs = [answer.s for answer in mcp.answers]
        return response('OK', items=rs)


class DomainCertificate(Resource):
    @jwt_required
    def post(self):
        data = request.get_json()
        id = data['id']
        answers = data['answers']
        group = CertificationGroup.query.get_or_404(id)
        assert len(list(answers.keys())) == group.certifications.count()
        for certification in group.certifications:
            certification.check_answer(answers[str(certification.id)])

        group.finish(current_user)
        return response('OK', items=[group.s])


class DomainCertifieds(Resource):
    @jwt_required
    def get(self):
        rs = [c.certified.s for c in current_user.certifieds]
        return response('OK', items=rs)


class DomainCertify(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('id')
        domain = Domain.query.get_or_404(id)
        rs = []
        if domain.is_certified(current_user):
            rs.append(domain.s)
        return response('OK', items=rs)

    @jwt_required
    def post(self):
        data = request.get_json()
        id = data['id']
        domain = Domain.query.get_or_404(id)
        for group in domain.certification_groups:
            assert group.is_finished(current_user)

        domain.certify(current_user)
        return response('OK', items=[domain.s])

    @jwt_required
    def delete(self):
        domain = request.args.get('domain')
        domain = Domain.query.get_or_404(domain)

        for group in domain.certification_groups:
            group.unfinish(current_user)
        
        domain.uncertify(current_user)
        return response('OK', items=[domain.s])


class DomainLearn(Resource):
    @jwt_required
    def get(self):
        id = request.args.get('domain')
        domain = Domain.query.get_or_404(id)
        rs = []
        if current_user.is_learning_domain(domain):
            rs = [domain.s]
        return response('OK', items=rs)

    @jwt_required
    def post(self):
        data = request.get_json()
        id = data['domain']
        domain = Domain.query.get_or_404(id)
        current_user.learn_domain(domain)
        return response('OK', items=[domain.s])

    @jwt_required
    def delete(self):
        id = request.args.get('domain')
        domain = Domain.query.get_or_404(id)
        current_user.unlearn_domain(domain)
        return response('OK', items=[domain.s])


class DomainTargetDomains(Resource):
    @jwt_required
    def get(self):
        rs = [d.learning.s for d in current_user.target_domains.all()]
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


class DomainExistence(Resource):
    @jwt_required
    def get(self):
        title = request.args.get('title')
        # TODO check domain validation
        r = Domain.query.filter_by(title=title).first()
        rt = []
        if r is not None:
            rt.append(r.s)
        return response('OK', items=rt)


api.add_resource(DomainInstance, '')
api.add_resource(DomainWatch, '/watch')
api.add_resource(DomainCollections, '/collections')
api.add_resource(DomainUserCollections, '/user/collections')
# api.add_resource(DomainCerification, '/certify')
# api.add_resource(DomainHot, '/hot')
api.add_resource(DomainAggregators, '/aggregators')
api.add_resource(DomainAggregateds, '/aggregateds')
api.add_resource(DomainDependeds, '/dependeds')
api.add_resource(DomainDependants, '/dependants')

api.add_resource(DomainInstanceAggregators, '/i/aggregators')
api.add_resource(DomainInstanceAggregateds, '/i/aggregateds')
api.add_resource(DomainInstanceDependeds, '/i/dependeds')
api.add_resource(DomainInstanceDependants, '/i/dependants')

api.add_resource(DomainAggregate, '/aggregate/all')
api.add_resource(DomainDepend, '/depend/all')
api.add_resource(DomainRootDepend, '/depend/root')

api.add_resource(DomainDepends, '/depends')
# api.add_resource(RoadMapInstance, '/roadmap')
# api.add_resource(RoadMapLearn, '/roadmap/learn')
api.add_resource(DomainLearn, '/learn')
api.add_resource(DomainTargetDomains, '/targets')
api.add_resource(DomainMarked, '/marked')
api.add_resource(DomainCreated, '/created')
api.add_resource(DomainMark, '/mark')

api.add_resource(Domains, '/all')

api.add_resource(DomainExistence, '/exist')

api.add_resource(DomainCertificationGroups, '/groups')
api.add_resource(DomainCertificationGroupInstance, '/group')
api.add_resource(DomainCertifications, '/certifications')
api.add_resource(DomainManageCertifications, '/manage/certifications')
api.add_resource(DomainCertificationInstance, '/certification')
api.add_resource(DomainMCPInstance, '/mcp')
api.add_resource(DomainMCPChoices, '/mcp/choices')
api.add_resource(DomainMCPChoiceInstance, '/mcp/choice')
api.add_resource(DomainMCPAnwers, '/mcp/answers')
api.add_resource(DomainCertificate, '/certificate')
api.add_resource(DomainCertify, '/certify')
api.add_resource(DomainCertifieds, '/certifieds')
