# -*- coding: utf-8 -*-
"""
    :author: Kleon
    :url: https://github.com/kleon1024
"""
import random

from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import (jwt_required, current_user)
from flask_restful import Api
from flask_restful import Resource as RestfulResource

from ..utils import (response, merge)
from ..models import (
Domain, Collection, Resource, Action,
Track, Group, Tag, TagStick, TagGroup,
AggAction, DepAction, TrackType, RemindCycleType,
COLOR_MAX
)
from ..extensions import db
from ..decorators import admin_required, permission_required

action_bp = Blueprint('group', __name__)
api = Api(action_bp)


class Actions(RestfulResource):
    @jwt_required
    def get(self):
        group = request.args.get('group')
        group = Group.query.get_or_404(group)
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 1))
        items = [d.s for d in group.actions.order_by(
            Action.modify_time.desc()).paginate(offset, limit).items]
        return response('OK', items=items)


class ActionItem(RestfulResource):
    @jwt_required
    def get(self):
        action = request.args.get('action')
        r = Action.query.get_or_404(action)
        return response('OK', items=[r.s])

    @jwt_required
    def post(self):
        data = request.get_json()
        kwargs = {}
        assert data['title'] != ''
        kwargs['title'] = data['title']

        group = Group.query.get_or_404(data['group'])
        kwargs['group_id'] = group.id

        r = Action(**kwargs)
        db.session.add(r)
        db.session.commit()

        if 'deps' in data:
            deps = data['deps']
            assert len(deps) > 0
            deps = Action.query.filter(Action.id.in_(deps)).all()

            depend_map = {}

            for depended in deps:
                for depended in DepAction.query.filter(
                        DepAction.descendant_id == depended.id).all():
                    key = (depended.ancestor_id, r.id)
                    if key not in depend_map:
                        d = DepAction(ancestor_id=depended.ancestor_id,
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
                DepAction(ancestor_id=r.id,
                            descendant_id=r.id,
                            distance=0))

        if 'aggs' in data:
            aggs = set(data['deps'])
            assert len(aggs) == 1
            aggs = Action.query.filter(Action.id.in_(aggs)).all()

            aggregate_map = {}

            for aggregator in aggs:
                for aggregator in AggAction.query.filter(
                        AggAction.descendant_id == aggregator.id):
                    key = (aggregator.ancestor_id, r.id)
                    if key not in aggregate_map:
                        a = AggAction(ancestor_id=aggregator.ancestor_id,
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
                AggAction(ancestor_id=r.id,
                        descendant_id=r.id,
                        distance=0))
        
        db.session.commit()
        return response('OK', items=[r.s])


    @jwt_required
    def put(self):
        data =request.get_json()
        r = Action.query.get_or_404(data['action'])

        if 'title' in data:
            r.title = data['title']

        deps = []
        if 'deps' in data:
            deps = data['deps']
            assert len(deps) > 0
            assert DepAction.query.filter(
                DepAction.ancestor_id == r.id,
                DepAction.descendant_id.in_(
                    deps)).first() is None
            deps = Action.query.filter(Action.id.in_(deps)).all()

        aggs = []
        if 'aggs' in data:
            aggs = set(data['deps'])
            assert len(aggs) == 1
            assert AggAction.query.filter(
                AggAction.ancestor_id == r.id,
                AggAction.descendant_id.in_(
                    aggs)).first() is None
            aggs = Action.query.filter(Action.id.in_(aggs)).all()

        old_dependeds = set(
            [dep.ancestor_id for dep in r.dependeds.filter_by(distance=1).all()])
        removable_dependeds = old_dependeds - deps

        for removable_depended in removable_dependeds:
            for (ancestor_id, ancestor_distance) in [(dep.ancestor_id, dep.distance) for dep in DepAction.query.filter(
                    DepAction.descendant_id == removable_depended).all()]:
                for (descendant_id, descendant_distance) in [(dep.descendant_id, dep.distance) for dep in r.dependants]:
                    d = DepAction.query.filter(
                        DepAction.ancestor_id == ancestor_id,
                        DepAction.descendant_id == descendant_id,
                        DepAction.distance == ancestor_distance + descendant_distance + 1).first()
                    if d is not None:
                        db.session.delete(d)

        addable_dependeds = deps
        for depended in addable_dependeds:
            for ancestor_id, ancestor_distance in [(dep.ancestor_id, dep.distance) for dep in DepAction.query.filter(
                DepAction.descendant_id == depended
            ).all()]:
                for descendant_id, descendant_distance in [(dep.descendant_id, dep.distance) for dep in r.dependants]:
                    old_d = DepAction.query.filter(
                        DepAction.ancestor_id == ancestor_id,
                        DepAction.descendant_id == descendant_id).order_by(DepAction.distance.desc()).first()
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
                        d = DepAction(ancestor_id=ancestor_id, descendant_id=descendant_id,
                                   distance=distance)
                        db.session.add(d)

        old_aggregators = set(
            [agg.ancestor_id for agg in r.aggregators.filter_by(distance=1).all()])
        removable_aggregates = old_aggregators - aggs
        for removable_aggregate in removable_aggregates:
            for (ancestor_id, ancestor_distance) in [(agg.ancestor_id, agg.distance) for agg in AggAction.query.filter(
                    AggAction.descendant_id == removable_aggregate).all()]:
                for (descendant_id, descendant_distance) in [(agg.descendant_id, agg.distance) for agg in r.aggregateds]:
                    d = AggAction.query.filter(
                        AggAction.ancestor_id == ancestor_id,
                        AggAction.descendant_id == descendant_id,
                        AggAction.distance == ancestor_distance + descendant_distance + 1).first()
                    if d is not None:
                        db.session.delete(d)

        for aggregate in aggs - old_aggregators:
            for ancestor_id, ancestor_distance in [(agg.ancestor_id, agg.distance) for agg in AggAction.query.filter(
                AggAction.descendant_id == aggregate
            ).all()]:
                for descendant_id, descendant_distance in [(agg.descendant_id, agg.distance) for agg in r.aggregateds]:
                    old_a = AggAction.query.filter(
                        AggAction.ancestor_id == ancestor_id,
                        AggAction.descendant_id == descendant_id).order_by(AggAction.distance.desc()).first()
                    if old_a is not None:
                        if old_a.distance < ancestor_distance + descendant_distance + 1:
                            old_a.distance = ancestor_distance + descendant_distance + 1
                    else:
                        a = AggAction(ancestor_id=ancestor_id, descendant_id=descendant_id,
                                      distance=ancestor_distance + descendant_distance + 1)
                        db.session.add(a)

        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        action = request.args.get('action')
        r = Action.query.get_or_404(action)
        db.session.delete(r)
        db.session.commit()
        return response('OK', items=[r.s])

class ActionTrackItem(RestfulResource):
    @jwt_required
    def get(self):
        track = request.args.get('track')
        r = Track.query.get_or_404(track)
        return response('OK', items=[r.s])

    @jwt_required
    def post(self):
        data = request.get_json()
        track_type = data['type']
        assert track_type in [e.value for e in TrackType]
        action = Action.query.get_or_404(data['action'])
        kwargs = {}
        kwargs['type'] = track_type
        kwargs['action_id'] = action.id
        if track_type == TrackType.DOMAIN.value:
            d = Domain.query.get_or_404(data['domain'])
            kwargs['domain_id'] = d.id
        if track_type == TrackType.COLLECTION.value:
            c = Collection.query.get_or_404(data['collection'])
            kwargs['collection_id'] = c.id
        if track_type == TrackType.RESOURCE.value:
            r = Resource.query.get_or_404(data['resource'])
            kwargs['resource_id'] = r.id
        r = Track(**kwargs)
        db.session.add(r)
        return response('OK', items=[r.s])

    @jwt_required
    def put(self):
        data = request.get_json()
        r = Track.query.get_or_404(data['track'])

        if 'type' in data:
            track_type = data['type']
            assert track_type in [e.value for e in TrackType]
            if r.track_type != track_type:
                if track_type == TrackType.DOMAIN.value:
                    d = Domain.query.get_or_404(data['domain'])
                    r.domain_id = d.id
                if track_type == TrackType.COLLECTION.value:
                    c = Collection.query.get_or_404(data['collection'])
                    r.collection_id = c.id
                if track_type == TrackType.RESOURCE.value:
                    r = Resource.query.get_or_404(data['resource'])
                    r.resource_id = r.id

        if 'action' in data:
            action = Action.query.get_or_404(data['action'])
            r.action_id = action.id
        
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        track = request.args.get('track')
        r = Track.query.get_or_404(track)
        db.session.delete(r)
        db.session.commit()
        return response('OK', items=[r.s])


class GroupTagItem(RestfulResource):
    @jwt_required
    def get(self):
        tag = request.args.get('tag')
        r = Tag.query.get_or_404(tag)
        return response('OK', items=[r.s])

    @jwt_required
    def post(self):
        data = request.get_json()
        group = Group.query.get_or_404(data['group'])
        kwargs = {}
        kwargs['title'] = data['title']
        if 'color' in data:
            color = int(data['color'])
            assert color >= 0 and color <= COLOR_MAX
        else:
            color = random.randint(0, COLOR_MAX)
        kwargs['color'] = color
        r = Tag(**kwargs)
        db.session.add(r)
        db.session.commit()

        group.add_tag(r)
        return response('OK', items=[r.s])
    
    @jwt_required
    def put(self):
        data =request.get_json()
        group = Group.query.get_or_404(data['group'])
        assert group.is_member(current_user)
        r = Tag.query.get_or_404(data['tag'])
        assert r.modifiable

        if 'title' in data:
            r.title = data['title']
        if 'color' in data:
            color = int(color)
            assert color >= 0 and color <= COLOR_MAX
            r.color = color
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        tag = request.args.get('tag')
        group = request.args.get('group')
        group = Group.query.get_or_404(group)
        r = Tag.query.get_or_404(tag)
        assert group.is_member(current_user)
        group.remove_tag(tag)

        if r.groups.count() == 0 and r.modifiable:
            db.session.delete(r)
            db.session.commit()

        return response('OK', items=[r.s])


class ActionTagItem(RestfulResource):
    @jwt_required
    def post(self):
        data = request.get_json()
        r = Action.query.get_or_404(data['action'])
        tag = Tag.query.get_or_404(data['tag'])

        assert r.group.is_member(current_user)
        r.add_tag(tag)
        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        data =request.get_json()
        r = Action.query.get_or_404(data['action'])
        tag = Tag.query.get_or_404(data['tag'])

        assert r.group.is_member(current_user)
        r.remove_tag(tag)
        return response('OK', items=[r.s])

class UserGroup(RestfulResource):
    @jwt_required
    def get(self):
        r = current_user.groups.filter_by(user_only=True).first()
        rs = []
        if r is not None:
            rs = [r.group.s]
        return response('OK', items=rs)
    
    @jwt_required
    def post(self):
        r = current_user.groups.filter_by(user_only=True).first()
        assert r is None
        kwargs = {}
        kwargs['title'] = current_user.username
        kwargs['private'] = True
        r = Group(**kwargs)
        db.session.add(r)
        db.session.commit()
        r.add_member(current_user, user_only=True)
        
        return response('OK', items=[r.s])

    @jwt_required
    def put(self):
        data = request.get_json()
        r = current_user.groups.filter_by(user_only=True).first()
        assert r is not None
        if 'title' in data:
            r.title = data['title']

        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        r = current_user.groups.filter_by(user_only=True).first()
        assert r is not None
        r.deleted = True
        r.remove_member(current_user)
        db.session.commit()
        return response('OK', items=[r.s])

class DomainGroup(RestfulResource):
    @jwt_required
    def get(self):
        group = request.args.get('group')
        r = Group.query.get_or_404(group)
        return response('OK', items=[r.s])
    
    @jwt_required
    def post(self):
        data = request.get_json()
        domain = Domain.query.get_or_404(data['domain'])
        assert domain.is_certified(current_user)
        assert domain.group_id is None

        kwargs = {}
        kwargs['title'] = current_user.username
        kwargs['private'] = False
        r = Group(**kwargs)
        db.session.add(r)
        db.session.commit()
        domain.group_id = r.id
        db.session.commit()
        return response('OK', items=[r.s])

    @jwt_required
    def put(self):
        data = request.get_json()
        r = Group.query.get_or_404(data['group'])
        assert r.domain.is_certified(current_user)

        if 'title' in data:
            r.title = data['title']

        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        group = request.args.get('group')
        r = Group.query.get_or_404(group)
        r.deleted = True
        r.domain.group_id = None
        db.session.commit()
        return response('OK', items=[r.s])
                

class GroupItem(RestfulResource):
    @jwt_required
    def get(self):
        group = request.args.get('group')
        r = Group.query.get_or_404(group)
        return response('OK', items=[r.s])

    @jwt_required
    def post(self):
        data = request.get_json()
        kwargs = {}
        kwargs['title'] = data['title']
        kwargs['private'] = data['private']
        assert data['private'] in [True, False]
        if data['private'] is True:
            assert current_user.vip
        r = Group(**kwargs)
        db.session.add(r)
        db.session.commit()

        r.add_member(current_user)
    
        return response('OK', items=[r.s])
    
    @jwt_required
    def put(self):
        data = request.get_json()
        r = Group.query.get_or_404(data['group'])
        assert r.is_member(current_user)

        if 'title' in data:
            r.title = data['title']

        return response('OK', items=[r.s])

    @jwt_required
    def delete(self):
        group = request.args.get('group')
        r = Group.query.get_or_404(group)
        r.remove_member(current_user)
        return response('OK', items=[r.s])


api.add_resource(GroupItem, '')
api.add_resource(ActionItem, '/action')
api.add_resource(Actions, '/actions')
api.add_resource(ActionTrackItem, '/action/track')
api.add_resource(GroupTagItem, '/tag')
api.add_resource(ActionTagItem, '/action/tag')
api.add_resource(UserGroup, '/user')
api.add_resource(DomainGroup, '/domain')