# -*- coding:utf-8 -*-


import json

from flask import abort
from flask_login import current_user

from api.extensions import db
from api.lib.cmdb.cache import AttributeCache
from api.lib.cmdb.cache import RelationTypeCache
from api.lib.cmdb.const import OperateType
from api.lib.cmdb.cache import CITypeCache
from api.lib.cmdb.perms import CIFilterPermsCRUD
from api.lib.cmdb.resp_format import ErrFormat
from api.lib.perm.acl.cache import UserCache
from api.models.cmdb import CI
from api.models.cmdb import Attribute
from api.models.cmdb import AttributeHistory
from api.models.cmdb import CIRelationHistory
from api.models.cmdb import CITriggerHistory
from api.models.cmdb import CITypeHistory
from api.models.cmdb import CITypeTrigger
from api.models.cmdb import CITypeUniqueConstraint
from api.models.cmdb import OperationRecord
from api.lib.cmdb.utils import TableMap


class AttributeHistoryManger(object):
    @staticmethod
    def get_records_for_attributes(start, end, username, page, page_size, operate_type, type_id,
                                   ci_id=None, attr_id=None, ci_ids=None, more=False):

        records = db.session.query(OperationRecord, AttributeHistory).join(
            AttributeHistory, OperationRecord.id == AttributeHistory.record_id)
        if start:
            records = records.filter(OperationRecord.created_at >= start)
        if end:
            records = records.filter(OperationRecord.created_at <= end)
        if type_id:
            records = records.filter(OperationRecord.type_id == type_id)
        if username:
            user = UserCache.get(username)
            if user:
                records = records.filter(OperationRecord.uid == user.uid)
            else:
                return abort(404, ErrFormat.user_not_found.format(username))
        if operate_type:
            records = records.filter(AttributeHistory.operate_type == operate_type)

        if ci_id is not None:
            records = records.filter(AttributeHistory.ci_id == ci_id)

        if ci_ids and isinstance(ci_ids, list):
            records = records.filter(AttributeHistory.ci_id.in_(ci_ids))

        if attr_id is not None:
            records = records.filter(AttributeHistory.attr_id == attr_id)

        records = records.order_by(AttributeHistory.id.desc()).offset(page_size * (page - 1)).limit(page_size).all()
        total = len(records)

        res = {}
        show_attr_set = {}
        show_attr_cache = {}
        for record in records:
            record_id = record.OperationRecord.id
            type_id = record.OperationRecord.type_id
            ci_id = record.AttributeHistory.ci_id
            show_attr_set[ci_id] = None
            show_attr = show_attr_cache.setdefault(
                type_id, 
                AttributeCache.get(
                    CITypeCache.get(type_id).show_id or CITypeCache.get(type_id).unique_id) if CITypeCache.get(type_id) else None
            )
            if show_attr:
                attr_table = TableMap(attr=show_attr).table
                attr_record = attr_table.get_by(attr_id=show_attr.id, ci_id=ci_id, first=True, to_dict=False)
                show_attr_set[ci_id] = attr_record.value if attr_record else None
    
            attr_hist = record.AttributeHistory.to_dict()
            attr_hist['attr'] = AttributeCache.get(attr_hist['attr_id'])
            if attr_hist['attr']:
                attr_hist['attr_name'] = attr_hist['attr'].name
                attr_hist['attr_alias'] = attr_hist['attr'].alias
                if more:
                    attr_hist['is_list'] = attr_hist['attr'].is_list
                    attr_hist['is_computed'] = attr_hist['attr'].is_computed
                    attr_hist['is_password'] = attr_hist['attr'].is_password
                    attr_hist['default'] = attr_hist['attr'].default
                attr_hist['value_type'] = attr_hist['attr'].value_type
                attr_hist.pop("attr")

            if record_id not in res:
                record_dict = record.OperationRecord.to_dict()
                record_dict['show_attr_value'] = show_attr_set.get(ci_id)
                record_dict["user"] = UserCache.get(record_dict.get("uid"))
                if record_dict["user"]:
                    record_dict['user'] = record_dict['user'].nickname

                res[record_id] = [record_dict, [attr_hist]]
            else:
                res[record_id][1].append(attr_hist)

        attr_filter = CIFilterPermsCRUD.get_attr_filter(type_id)
        if attr_filter:
            res = [i for i in res if i.get('attr_name') in attr_filter]

        res = [res[i] for i in sorted(res.keys(), reverse=True)]

        return total, res

    @staticmethod
    def get_records_for_relation(start, end, username, page, page_size, operate_type, type_id,
                                 first_ci_id=None, second_ci_id=None):

        records = db.session.query(OperationRecord, CIRelationHistory).join(
            CIRelationHistory, OperationRecord.id == CIRelationHistory.record_id)
        if start:
            records = records.filter(OperationRecord.created_at >= start)
        if end:
            records = records.filter(OperationRecord.created_at <= end)
        if type_id:
            records = records.filter(OperationRecord.type_id == type_id)
        if username:
            user = UserCache.get(username)
            if user:
                records = records.filter(OperationRecord.uid == user.uid)
            else:
                return abort(404, ErrFormat.user_not_found.format(username))
        if operate_type:
            records = records.filter(CIRelationHistory.operate_type == operate_type)

        if first_ci_id is not None:
            records = records.filter(CIRelationHistory.first_ci_id == first_ci_id)

        if second_ci_id is not None:
            records = records.filter(CIRelationHistory.second_ci_id == second_ci_id)

        records = records.order_by(CIRelationHistory.id.desc()).offset(page_size * (page - 1)).limit(page_size).all()
        total = len(records)

        res = {}
        ci_ids = set()
        for record in records:
            record_id = record.OperationRecord.id
            rel_hist = record.CIRelationHistory.to_dict()

            ci_ids.add(rel_hist['first_ci_id'])
            ci_ids.add(rel_hist['second_ci_id'])
            if record_id not in res:
                record_dict = record.OperationRecord.to_dict()
                record_dict["user"] = UserCache.get(record_dict.get("uid"))
                if record_dict["user"]:
                    record_dict['user'] = record_dict['user'].nickname

                res[record_id] = [record_dict, [rel_hist]]
            else:
                res[record_id][1].append(rel_hist)

        res = [res[i] for i in sorted(res.keys(), reverse=True)]

        from api.lib.cmdb.ci import CIManager
        cis = CIManager().get_cis_by_ids(list(ci_ids),
                                         unique_required=True)
        cis = {i['_id']: i for i in cis if i}

        return total, res, cis

    @staticmethod
    def get_by_ci_id(ci_id):
        res = db.session.query(AttributeHistory, Attribute, OperationRecord).join(
            Attribute, Attribute.id == AttributeHistory.attr_id).join(
            OperationRecord, OperationRecord.id == AttributeHistory.record_id).filter(
            AttributeHistory.ci_id == ci_id).order_by(AttributeHistory.id.desc())

        from api.lib.cmdb.ci import CIManager
        ci = CIManager.get_by_id(ci_id)

        attr_filter = CIFilterPermsCRUD.get_attr_filter(ci.type_id) if ci else None
        result = []
        for i in res:
            attr = i.Attribute
            if attr_filter and attr.name not in attr_filter:
                continue

            user = UserCache.get(i.OperationRecord.uid)
            hist = i.AttributeHistory
            record = i.OperationRecord
            item = dict(attr_name=attr.name,
                        attr_alias=attr.alias,
                        value_type=attr.value_type,
                        operate_type=hist.operate_type,
                        username=user and user.nickname,
                        old=hist.old,
                        new=hist.new,
                        created_at=record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        record_id=record.id,
                        ticket_id=record.ticket_id,
                        hid=hist.id
                        )
            result.append(item)

        return result

    @staticmethod
    def get_record_detail(record_id):
        from api.lib.cmdb.ci import CIManager

        record = (OperationRecord.get_by_id(record_id) or
                  abort(404, ErrFormat.record_not_found.format("id={}".format(record_id))))

        username = UserCache.get(record.uid).nickname or UserCache.get(record.uid).username
        timestamp = record.created_at.strftime("%Y-%m-%d %H:%M:%S")
        attr_history = AttributeHistory.get_by(record_id=record_id, to_dict=False)
        rel_history = CIRelationHistory.get_by(record_id=record_id, to_dict=False)

        attr_dict, rel_dict = dict(), {"add": [], "delete": []}
        for attr_h in attr_history:
            attr_dict[AttributeCache.get(attr_h.attr_id).alias] = dict(
                old=attr_h.old,
                new=attr_h.new,
                operate_type=attr_h.operate_type)

        for rel_h in rel_history:
            first = CIManager.get_ci_by_id(rel_h.first_ci_id)
            second = CIManager.get_ci_by_id(rel_h.second_ci_id)
            rel_dict[rel_h.operate_type].append((first, RelationTypeCache.get(rel_h.relation_type_id).name, second))

        return username, timestamp, attr_dict, rel_dict

    @staticmethod
    def add(record_id, ci_id, history_list, type_id=None, ticket_id=None, flush=False, commit=True):
        if record_id is None:
            record = OperationRecord.create(uid=current_user.uid, type_id=type_id, ticket_id=ticket_id)
            record_id = record.id

        for attr_id, operate_type, old, new in history_list or []:
            AttributeHistory.create(attr_id=attr_id,
                                    operate_type=operate_type,
                                    old=json.dumps(old) if isinstance(old, (dict, list)) else old,
                                    new=json.dumps(new) if isinstance(new, (dict, list)) else new,
                                    ci_id=ci_id,
                                    record_id=record_id,
                                    flush=flush,
                                    commit=commit)

        return record_id


class CIRelationHistoryManager(object):
    @staticmethod
    def add(rel_obj, operate_type=OperateType.ADD, uid=None):
        record = OperationRecord.create(uid=uid or current_user.uid)

        CIRelationHistory.create(relation_id=rel_obj.id,
                                 record_id=record.id,
                                 operate_type=operate_type,
                                 first_ci_id=rel_obj.first_ci_id,
                                 second_ci_id=rel_obj.second_ci_id,
                                 relation_type_id=rel_obj.relation_type_id)


class CITypeHistoryManager(object):
    @staticmethod
    def get(page, page_size, username=None, type_id=None, operate_type=None):
        query = CITypeHistory.get_by(only_query=True)
        if type_id is not None:
            query = query.filter(CITypeHistory.type_id == type_id)

        if username:
            user = UserCache.get(username)
            if user:
                query = query.filter(CITypeHistory.uid == user.uid)
            else:
                return abort(404, ErrFormat.user_not_found.format(username))

        if operate_type is not None:
            query = query.filter(CITypeHistory.operate_type == operate_type)

        numfound = query.count()

        query = query.order_by(CITypeHistory.id.desc())
        result = query.offset((page - 1) * page_size).limit(page_size)
        result = [i.to_dict() for i in result]
        for res in result:
            res["user"] = UserCache.get(res.get("uid"))
            if res["user"]:
                res['user'] = res['user'].nickname
            if res.get('attr_id'):
                attr = AttributeCache.get(res['attr_id'])
                res['attr'] = attr and attr.to_dict()
            elif res.get('trigger_id'):
                trigger = CITypeTrigger.get_by_id(res['trigger_id'])
                res['trigger'] = trigger and trigger.to_dict()
            elif res.get('unique_constraint_id'):
                unique_constraint = CITypeUniqueConstraint.get_by_id(res['unique_constraint_id'])
                res['unique_constraint'] = unique_constraint and unique_constraint.to_dict()

        return numfound, result

    @staticmethod
    def add(operate_type, type_id, attr_id=None, trigger_id=None, unique_constraint_id=None, change=None, rc_id=None):
        if type_id is None and attr_id is not None:
            from api.models.cmdb import CITypeAttribute
            type_ids = [i.type_id for i in CITypeAttribute.get_by(attr_id=attr_id, to_dict=False)]
        else:
            type_ids = [type_id]

        for _type_id in type_ids:
            payload = dict(operate_type=operate_type,
                           type_id=_type_id,
                           uid=current_user.uid,
                           attr_id=attr_id,
                           trigger_id=trigger_id,
                           rc_id=rc_id,
                           unique_constraint_id=unique_constraint_id,
                           change=change)

            CITypeHistory.create(**payload)


class CITriggerHistoryManager(object):
    @staticmethod
    def get(page, page_size, type_id=None, trigger_id=None, operate_type=None):
        query = CITriggerHistory.get_by(only_query=True)
        if type_id:
            query = query.join(CI, CI.id == CITriggerHistory.ci_id).filter(CI.type_id == type_id)

        if trigger_id:
            query = query.filter(CITriggerHistory.trigger_id == trigger_id)

        if operate_type:
            query = query.filter(CITriggerHistory.operate_type == operate_type)

        numfound = query.count()

        query = query.order_by(CITriggerHistory.id.desc())
        result = query.offset((page - 1) * page_size).limit(page_size)
        result = [i.to_dict() for i in result]
        for res in result:
            if res.get('trigger_id'):
                trigger = CITypeTrigger.get_by_id(res['trigger_id'])
                res['trigger'] = trigger and trigger.to_dict()

        return numfound, result

    @staticmethod
    def get_by_ci_id(ci_id):
        res = db.session.query(CITriggerHistory, CITypeTrigger).join(
            CITypeTrigger, CITypeTrigger.id == CITriggerHistory.trigger_id).filter(
            CITriggerHistory.ci_id == ci_id).order_by(CITriggerHistory.id.desc())

        result = []
        id2trigger = dict()
        for i in res:
            hist = i.CITriggerHistory
            item = dict(is_ok=hist.is_ok,
                        operate_type=hist.operate_type,
                        notify=hist.notify,
                        trigger_id=hist.trigger_id,
                        trigger_name=hist.trigger_name,
                        webhook=hist.webhook,
                        created_at=hist.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        record_id=hist.record_id,
                        hid=hist.id
                        )
            if i.CITypeTrigger.id not in id2trigger:
                id2trigger[i.CITypeTrigger.id] = i.CITypeTrigger.to_dict()

            result.append(item)

        return dict(items=result, id2trigger=id2trigger)

    @staticmethod
    def add(operate_type, record_id, ci_id, trigger_id, trigger_name, is_ok=False, notify=None, webhook=None):

        CITriggerHistory.create(operate_type=operate_type,
                                record_id=record_id,
                                ci_id=ci_id,
                                trigger_id=trigger_id,
                                trigger_name=trigger_name,
                                is_ok=is_ok,
                                notify=notify,
                                webhook=webhook)
