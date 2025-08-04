# -*- coding:utf-8 -*-


import datetime
from sqlalchemy.dialects.mysql import DOUBLE

from api.extensions import db
from api.lib.cmdb.const import AutoDiscoveryType
from api.lib.cmdb.const import CIStatusEnum
from api.lib.cmdb.const import CITypeOperateType
from api.lib.cmdb.const import ConstraintEnum
from api.lib.cmdb.const import OperateType
from api.lib.cmdb.const import RelationSourceEnum
from api.lib.cmdb.const import ValueTypeEnum
from api.lib.database import Model
from api.lib.database import Model2
from api.lib.utils import Crypto


# template

class RelationType(Model):
    __tablename__ = "c_relation_types"

    name = db.Column(db.String(16), index=True, nullable=False)


class CITypeGroup(Model):
    __tablename__ = "c_ci_type_groups"

    name = db.Column(db.String(32), nullable=False)
    order = db.Column(db.Integer, default=0)


class CITypeGroupItem(Model):
    __tablename__ = "c_ci_type_group_items"

    group_id = db.Column(db.Integer, db.ForeignKey("c_ci_type_groups.id"), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey("c_ci_types.id"), nullable=False)
    order = db.Column(db.SmallInteger, default=0)


class CIType(Model):
    __tablename__ = "c_ci_types"

    name = db.Column(db.String(32), nullable=False)
    alias = db.Column(db.String(32), nullable=False)
    unique_id = db.Column(db.Integer, db.ForeignKey("c_attributes.id"), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey("c_attributes.id"))
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    is_attached = db.Column(db.Boolean, default=False, nullable=False)
    icon = db.Column(db.Text)
    order = db.Column(db.SmallInteger, default=0, nullable=False)
    default_order_attr = db.Column(db.String(33))

    unique_key = db.relationship("Attribute", backref="c_ci_types.unique_id",
                                 primaryjoin="Attribute.id==CIType.unique_id", foreign_keys=[unique_id])
    show_key = db.relationship("Attribute", backref="c_ci_types.show_id",
                               primaryjoin="Attribute.id==CIType.show_id", foreign_keys=[show_id])

    uid = db.Column(db.Integer, index=True)


class CITypeInheritance(Model):
    __tablename__ = "c_ci_type_inheritance"

    parent_id = db.Column(db.Integer, db.ForeignKey("c_ci_types.id"), nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey("c_ci_types.id"), nullable=False)

    parent = db.relationship("CIType", primaryjoin="CIType.id==CITypeInheritance.parent_id")
    child = db.relationship("CIType", primaryjoin="CIType.id==CITypeInheritance.child_id")


class CITypeRelation(Model):
    __tablename__ = "c_ci_type_relations"

    parent_id = db.Column(db.Integer, db.ForeignKey("c_ci_types.id"), nullable=False)  # source
    child_id = db.Column(db.Integer, db.ForeignKey("c_ci_types.id"), nullable=False)  # dst
    relation_type_id = db.Column(db.Integer, db.ForeignKey("c_relation_types.id"), nullable=False)
    constraint = db.Column(db.Enum(*ConstraintEnum.all()), default=ConstraintEnum.One2Many)

    parent_attr_id = db.Column(db.Integer, db.ForeignKey("c_attributes.id"))  # CMDB > 2.4.5: deprecated
    child_attr_id = db.Column(db.Integer, db.ForeignKey("c_attributes.id"))  # CMDB > 2.4.5: deprecated

    parent_attr_ids = db.Column(db.JSON)  # [parent_attr_id, ]
    child_attr_ids = db.Column(db.JSON)  # [child_attr_id, ]

    parent = db.relationship("CIType", primaryjoin="CIType.id==CITypeRelation.parent_id")
    child = db.relationship("CIType", primaryjoin="CIType.id==CITypeRelation.child_id")
    relation_type = db.relationship("RelationType", backref="c_ci_type_relations.relation_type_id")


class Attribute(Model):
    __tablename__ = "c_attributes"

    name = db.Column(db.String(32), nullable=False)
    alias = db.Column(db.String(32), nullable=False)
    value_type = db.Column(db.Enum(*ValueTypeEnum.all()), default=ValueTypeEnum.TEXT, nullable=False)

    is_choice = db.Column(db.Boolean, default=False)
    is_list = db.Column(db.Boolean, default=False)
    is_unique = db.Column(db.Boolean, default=False)
    is_index = db.Column(db.Boolean, default=False)
    is_link = db.Column(db.Boolean, default=False)
    is_password = db.Column(db.Boolean, default=False)
    is_sortable = db.Column(db.Boolean, default=False)
    is_dynamic = db.Column(db.Boolean, default=False)
    is_bool = db.Column(db.Boolean, default=False)

    is_reference = db.Column(db.Boolean, default=False)
    reference_type_id = db.Column(db.Integer, db.ForeignKey('c_ci_types.id'))

    default = db.Column(db.JSON)  # {"default": None}

    is_computed = db.Column(db.Boolean, default=False)
    compute_expr = db.Column(db.Text)
    compute_script = db.Column(db.Text)

    _choice_web_hook = db.Column('choice_web_hook', db.JSON)
    choice_other = db.Column(db.JSON)

    re_check = db.Column(db.Text)

    uid = db.Column(db.Integer, index=True)

    option = db.Column(db.JSON)

    def _get_webhook(self):
        if self._choice_web_hook:
            if self._choice_web_hook.get('headers') and "Cookie" in self._choice_web_hook['headers']:
                self._choice_web_hook['headers']['Cookie'] = Crypto.decrypt(self._choice_web_hook['headers']['Cookie'])

            if self._choice_web_hook.get('authorization'):
                for k, v in self._choice_web_hook['authorization'].items():
                    self._choice_web_hook['authorization'][k] = Crypto.decrypt(v)

        return self._choice_web_hook

    def _set_webhook(self, data):
        if data:
            if data.get('headers') and "Cookie" in data['headers']:
                data['headers']['Cookie'] = Crypto.encrypt(data['headers']['Cookie'])

            if data.get('authorization'):
                for k, v in data['authorization'].items():
                    data['authorization'][k] = Crypto.encrypt(v)

        self._choice_web_hook = data

    choice_web_hook = db.synonym("_choice_web_hook", descriptor=property(_get_webhook, _set_webhook))


class CITypeAttribute(Model):
    __tablename__ = "c_ci_type_attributes"

    type_id = db.Column(db.Integer, db.ForeignKey("c_ci_types.id"), nullable=False)
    attr_id = db.Column(db.Integer, db.ForeignKey("c_attributes.id"), nullable=False)
    order = db.Column(db.Integer, default=0)
    is_required = db.Column(db.Boolean, default=False)
    default_show = db.Column(db.Boolean, default=True)

    attr = db.relationship("Attribute", backref="c_ci_type_attributes.attr_id")


class CITypeAttributeGroup(Model):
    __tablename__ = "c_ci_type_attribute_groups"

    name = db.Column(db.String(64), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey("c_ci_types.id"), nullable=False)
    order = db.Column(db.SmallInteger, default=0)


class CITypeAttributeGroupItem(Model):
    __tablename__ = "c_ci_type_attribute_group_items"

    group_id = db.Column(db.Integer, db.ForeignKey("c_ci_type_attribute_groups.id"), nullable=False)
    attr_id = db.Column(db.Integer, db.ForeignKey("c_attributes.id"), nullable=False)
    order = db.Column(db.SmallInteger, default=0)


class CITypeTrigger(Model):
    __tablename__ = "c_c_t_t"

    type_id = db.Column(db.Integer, db.ForeignKey('c_ci_types.id'), nullable=False)
    attr_id = db.Column(db.Integer, db.ForeignKey("c_attributes.id"))
    _option = db.Column('notify', db.JSON)

    def _get_option(self):
        if self._option and self._option.get('webhooks'):
            if self._option['webhooks'].get('authorization'):
                for k, v in self._option['webhooks']['authorization'].items():
                    self._option['webhooks']['authorization'][k] = Crypto.decrypt(v)

        return self._option

    def _set_option(self, data):
        if data and data.get('webhooks'):
            if data['webhooks'].get('authorization'):
                for k, v in data['webhooks']['authorization'].items():
                    data['webhooks']['authorization'][k] = Crypto.encrypt(v)

        self._option = data

    option = db.synonym("_option", descriptor=property(_get_option, _set_option))


class CITriggerHistory(Model):
    __tablename__ = "c_ci_trigger_histories"

    operate_type = db.Column(db.Enum(*OperateType.all(), name="operate_type"))
    record_id = db.Column(db.Integer, db.ForeignKey("c_records.id"))
    ci_id = db.Column(db.Integer, index=True, nullable=False)
    trigger_id = db.Column(db.Integer, db.ForeignKey("c_c_t_t.id"))
    trigger_name = db.Column(db.String(64))
    is_ok = db.Column(db.Boolean, default=False)
    notify = db.Column(db.Text)
    webhook = db.Column(db.Text)


class TopologyViewGroup(Model):
    __tablename__ = 'c_topology_view_groups'

    name = db.Column(db.String(64), index=True)
    order = db.Column(db.Integer, default=0)


class TopologyView(Model):
    __tablename__ = 'c_topology_views'

    name = db.Column(db.String(64), index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('c_topology_view_groups.id'))
    category = db.Column(db.String(32))
    central_node_type = db.Column(db.Integer)
    central_node_instances = db.Column(db.Text)
    path = db.Column(db.JSON)
    order = db.Column(db.Integer, default=0)
    option = db.Column(db.JSON)


class CITypeUniqueConstraint(Model):
    __tablename__ = "c_c_t_u_c"

    type_id = db.Column(db.Integer, db.ForeignKey('c_ci_types.id'), nullable=False)
    attr_ids = db.Column(db.JSON)  # [attr_id, ]


# instance

class CI(Model):
    __tablename__ = "c_cis"

    type_id = db.Column(db.Integer, db.ForeignKey("c_ci_types.id"), nullable=False)
    status = db.Column(db.Enum(*CIStatusEnum.all(), name="status"))
    heartbeat = db.Column(db.DateTime, default=lambda: datetime.datetime.now())
    is_auto_discovery = db.Column('a', db.Boolean, default=False)
    updated_by = db.Column(db.String(64))

    ci_type = db.relationship("CIType", backref="c_cis.type_id")


class CIRelation(Model):
    __tablename__ = "c_ci_relations"

    first_ci_id = db.Column(db.Integer, db.ForeignKey("c_cis.id"), nullable=False)
    second_ci_id = db.Column(db.Integer, db.ForeignKey("c_cis.id"), nullable=False)
    relation_type_id = db.Column(db.Integer, db.ForeignKey("c_relation_types.id"), nullable=False)
    more = db.Column(db.Integer, db.ForeignKey("c_cis.id"))
    source = db.Column(db.Enum(*RelationSourceEnum.all()), name="source")

    ancestor_ids = db.Column(db.String(128), index=True)

    first_ci = db.relationship("CI", primaryjoin="CI.id==CIRelation.first_ci_id")
    second_ci = db.relationship("CI", primaryjoin="CI.id==CIRelation.second_ci_id")
    relation_type = db.relationship("RelationType", backref="c_ci_relations.relation_type_id")


class IntegerChoice(Model):
    __tablename__ = 'c_choice_integers'

    attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    option = db.Column(db.JSON)

    attr = db.relationship("Attribute", backref="c_choice_integers.attr_id")


class FloatChoice(Model):
    __tablename__ = 'c_choice_floats'

    attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'), nullable=False)
    value = db.Column(DOUBLE, nullable=False)
    option = db.Column(db.JSON)

    attr = db.relationship("Attribute", backref="c_choice_floats.attr_id")


class TextChoice(Model):
    __tablename__ = 'c_choice_texts'

    attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'), nullable=False)
    value = db.Column(db.Text, nullable=False)
    option = db.Column(db.JSON)

    attr = db.relationship("Attribute", backref="c_choice_texts.attr_id")


class CIIndexValueInteger(Model):
    __tablename__ = "c_value_index_integers"

    ci_id = db.Column(db.Integer, db.ForeignKey('c_cis.id'), nullable=False)
    attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)

    ci = db.relationship("CI", backref="c_value_index_integers.ci_id")
    attr = db.relationship("Attribute", backref="c_value_index_integers.attr_id")

    __table_args__ = (db.Index("integer_attr_value_index", "attr_id", "value"),)


class CIIndexValueFloat(Model):
    __tablename__ = "c_value_index_floats"

    ci_id = db.Column(db.Integer, db.ForeignKey('c_cis.id'), nullable=False)
    attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'), nullable=False)
    value = db.Column(DOUBLE, nullable=False)

    ci = db.relationship("CI", backref="c_value_index_floats.ci_id")
    attr = db.relationship("Attribute", backref="c_value_index_floats.attr_id")

    __table_args__ = (db.Index("float_attr_value_index", "attr_id", "value"),)


class CIIndexValueText(Model):
    __tablename__ = "c_value_index_texts"

    ci_id = db.Column(db.Integer, db.ForeignKey('c_cis.id'), nullable=False)
    attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'), nullable=False)
    value = db.Column(db.String(128), nullable=False)

    ci = db.relationship("CI", backref="c_value_index_texts.ci_id")
    attr = db.relationship("Attribute", backref="c_value_index_texts.attr_id")

    __table_args__ = (db.Index("text_attr_value_index", "attr_id", "value"),)


class CIIndexValueDateTime(Model):
    __tablename__ = "c_value_index_datetime"

    ci_id = db.Column(db.Integer, db.ForeignKey('c_cis.id'), nullable=False)
    attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'), nullable=False)
    value = db.Column(db.DateTime, nullable=False)

    ci = db.relationship("CI", backref="c_value_index_datetime.ci_id")
    attr = db.relationship("Attribute", backref="c_value_index_datetime.attr_id")

    __table_args__ = (db.Index("datetime_attr_value_index", "attr_id", "value"),)


class CIValueInteger(Model):
    """
    Deprecated in a future version
    """
    __tablename__ = "c_value_integers"

    ci_id = db.Column(db.Integer, db.ForeignKey('c_cis.id'), nullable=False)
    attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)

    ci = db.relationship("CI", backref="c_value_integers.ci_id")
    attr = db.relationship("Attribute", backref="c_value_integers.attr_id")


class CIValueFloat(Model):
    """
    Deprecated in a future version
    """
    __tablename__ = "c_value_floats"

    ci_id = db.Column(db.Integer, db.ForeignKey('c_cis.id'), nullable=False)
    attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'), nullable=False)
    value = db.Column(DOUBLE, nullable=False)

    ci = db.relationship("CI", backref="c_value_floats.ci_id")
    attr = db.relationship("Attribute", backref="c_value_floats.attr_id")


class CIValueText(Model):
    __tablename__ = "c_value_texts"

    ci_id = db.Column(db.Integer, db.ForeignKey('c_cis.id'), nullable=False)
    attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'), nullable=False)
    value = db.Column(db.Text, nullable=False)

    ci = db.relationship("CI", backref="c_value_texts.ci_id")
    attr = db.relationship("Attribute", backref="c_value_texts.attr_id")


class CIValueDateTime(Model):
    """
    Deprecated in a future version
    """
    __tablename__ = "c_value_datetime"

    ci_id = db.Column(db.Integer, db.ForeignKey('c_cis.id'), nullable=False)
    attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'), nullable=False)
    value = db.Column(db.DateTime, nullable=False)

    ci = db.relationship("CI", backref="c_value_datetime.ci_id")
    attr = db.relationship("Attribute", backref="c_value_datetime.attr_id")


class CIValueJson(Model):
    __tablename__ = "c_value_json"

    ci_id = db.Column(db.Integer, db.ForeignKey('c_cis.id'), nullable=False)
    attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'), nullable=False)
    value = db.Column(db.JSON, nullable=False)

    ci = db.relationship("CI", backref="c_value_json.ci_id")
    attr = db.relationship("Attribute", backref="c_value_json.attr_id")


# history
class OperationRecord(Model2):
    __tablename__ = "c_records"

    uid = db.Column(db.Integer, index=True, nullable=False)
    origin = db.Column(db.String(32), nullable=True)
    ticket_id = db.Column(db.String(32), nullable=True)
    reason = db.Column(db.Text)

    type_id = db.Column(db.Integer, index=True)


class AttributeHistory(Model):
    __tablename__ = "c_attribute_histories"

    operate_type = db.Column(db.Enum(*OperateType.all(), name="operate_type"))
    record_id = db.Column(db.Integer, db.ForeignKey("c_records.id"), nullable=False)
    ci_id = db.Column(db.Integer, index=True, nullable=False)
    attr_id = db.Column(db.Integer, index=True)
    old = db.Column(db.Text)
    new = db.Column(db.Text)


class CIRelationHistory(Model):
    __tablename__ = "c_relation_histories"

    operate_type = db.Column(db.Enum(OperateType.ADD, OperateType.DELETE, name="operate_type"))
    record_id = db.Column(db.Integer, db.ForeignKey("c_records.id"), nullable=False)
    first_ci_id = db.Column(db.Integer)
    second_ci_id = db.Column(db.Integer)
    relation_type_id = db.Column(db.Integer, db.ForeignKey("c_relation_types.id"))
    relation_id = db.Column(db.Integer, nullable=False)


class CITypeHistory(Model):
    __tablename__ = "c_ci_type_histories"

    operate_type = db.Column(db.Enum(*CITypeOperateType.all(), name="operate_type"))
    type_id = db.Column(db.Integer, index=True, nullable=False)

    attr_id = db.Column(db.Integer)
    trigger_id = db.Column(db.Integer)
    rc_id = db.Column(db.Integer)
    unique_constraint_id = db.Column(db.Integer)

    uid = db.Column(db.Integer, index=True)
    change = db.Column(db.JSON)


# preference
class PreferenceShowAttributes(Model):
    __tablename__ = "c_psa"

    uid = db.Column(db.Integer, index=True, nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey("c_ci_types.id"), nullable=False)
    attr_id = db.Column(db.Integer, db.ForeignKey("c_attributes.id"))
    builtin_attr = db.Column(db.String(256), nullable=True)
    order = db.Column(db.SmallInteger, default=0)
    is_fixed = db.Column(db.Boolean, default=False)

    ci_type = db.relationship("CIType", backref="c_psa.type_id")
    attr = db.relationship("Attribute", backref="c_psa.attr_id")


class PreferenceTreeView(Model):
    __tablename__ = "c_ptv"

    uid = db.Column(db.Integer, index=True, nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey("c_ci_types.id"), nullable=False)
    levels = db.Column(db.JSON)


class PreferenceRelationView(Model):
    __tablename__ = "c_prv"

    uid = db.Column(db.Integer, index=True, nullable=False)
    name = db.Column(db.String(64), index=True, nullable=False)
    cr_ids = db.Column(db.JSON)  # [{parent_id: x, child_id: y}]
    is_public = db.Column(db.Boolean, default=False)
    option = db.Column(db.JSON)


class PreferenceSearchOption(Model):
    __tablename__ = "c_pso"

    name = db.Column(db.String(64))

    prv_id = db.Column(db.Integer, db.ForeignKey("c_prv.id"))
    ptv_id = db.Column(db.Integer, db.ForeignKey("c_ptv.id"))
    type_id = db.Column(db.Integer, db.ForeignKey("c_ci_types.id"))

    uid = db.Column(db.Integer, index=True)

    option = db.Column(db.JSON)


class PreferenceCITypeOrder(Model):
    __tablename__ = "c_pcto"

    uid = db.Column(db.Integer, index=True, nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('c_ci_types.id'))
    order = db.Column(db.SmallInteger, default=0)
    is_tree = db.Column(db.Boolean, default=False)  # True is tree view, False is resource view


# custom
class CustomDashboard(Model):
    __tablename__ = "c_c_d"

    name = db.Column(db.String(64))
    category = db.Column(db.SmallInteger)  # 0: 总数统计, 1: 字段值统计, 2: 关系统计
    enabled = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)

    type_id = db.Column(db.Integer, db.ForeignKey('c_ci_types.id'))
    attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'))
    builtin_attr = db.Column(db.String(256), nullable=True)
    level = db.Column(db.Integer)

    options = db.Column(db.JSON)


class SystemConfig(Model):
    __tablename__ = "c_sc"

    name = db.Column(db.String(64), index=True)
    option = db.Column(db.JSON)


# auto discovery
class AutoDiscoveryRule(Model):
    __tablename__ = "c_ad_rules"

    name = db.Column(db.String(32))
    type = db.Column(db.Enum(*AutoDiscoveryType.all()), index=True)
    is_inner = db.Column(db.Boolean, default=False, index=True)
    owner = db.Column(db.Integer, index=True)

    option = db.Column(db.JSON)  # layout
    attributes = db.Column(db.JSON)

    is_plugin = db.Column(db.Boolean, default=False)
    plugin_script = db.Column(db.Text)
    unique_key = db.Column(db.String(64))


class AutoDiscoveryCIType(Model):
    __tablename__ = "c_ad_ci_types"

    type_id = db.Column(db.Integer, db.ForeignKey('c_ci_types.id'))
    adr_id = db.Column(db.Integer, db.ForeignKey('c_ad_rules.id'))

    attributes = db.Column(db.JSON)  # {ad_key: cmdb_key}

    relation = db.Column(db.JSON)  # [{ad_key: {type_id: x, attr_id: x}}], CMDB > 2.4.5: deprecated

    auto_accept = db.Column(db.Boolean, default=False)

    agent_id = db.Column(db.String(8), index=True)
    query_expr = db.Column(db.Text)

    interval = db.Column(db.Integer)  # seconds, > 2.4.5: deprecated
    cron = db.Column(db.String(128))

    extra_option = db.Column(db.JSON)
    uid = db.Column(db.Integer, index=True)
    enabled = db.Column(db.Boolean, default=True)


class AutoDiscoveryCITypeRelation(Model):
    __tablename__ = "c_ad_ci_type_relations"

    ad_type_id = db.Column(db.Integer, db.ForeignKey('c_ci_types.id'), nullable=False)
    ad_key = db.Column(db.String(128))
    peer_type_id = db.Column(db.Integer, db.ForeignKey('c_ci_types.id'), nullable=False)
    peer_attr_id = db.Column(db.Integer, db.ForeignKey('c_attributes.id'), nullable=False)


class AutoDiscoveryCI(Model):
    __tablename__ = "c_ad_ci"

    type_id = db.Column(db.Integer, db.ForeignKey('c_ci_types.id'))
    adt_id = db.Column(db.Integer, db.ForeignKey('c_ad_ci_types.id'))
    unique_value = db.Column(db.String(128), index=True)
    instance = db.Column(db.JSON)

    ci_id = db.Column(db.Integer, index=True)

    is_accept = db.Column(db.Boolean, default=False)
    accept_by = db.Column(db.String(64), index=True)
    accept_time = db.Column(db.DateTime)


class AutoDiscoveryRuleSyncHistory(Model2):
    __tablename__ = "c_ad_rule_sync_histories"

    adt_id = db.Column(db.Integer, db.ForeignKey('c_ad_ci_types.id'))
    oneagent_id = db.Column(db.String(8))
    oneagent_name = db.Column(db.String(64))
    sync_at = db.Column(db.DateTime, default=datetime.datetime.now())


class AutoDiscoveryExecHistory(Model2):
    __tablename__ = "c_ad_exec_histories"

    type_id = db.Column(db.Integer, index=True)
    stdout = db.Column(db.Text)


class AutoDiscoveryCounter(Model2):
    __tablename__ = "c_ad_counter"

    type_id = db.Column(db.Integer, index=True)
    rule_count = db.Column(db.Integer, default=0)
    exec_target_count = db.Column(db.Integer, default=0)
    instance_count = db.Column(db.Integer, default=0)
    accept_count = db.Column(db.Integer, default=0)
    this_month_count = db.Column(db.Integer, default=0)
    this_week_count = db.Column(db.Integer, default=0)
    last_month_count = db.Column(db.Integer, default=0)
    last_week_count = db.Column(db.Integer, default=0)


class AutoDiscoveryAccount(Model):
    __tablename__ = "c_ad_accounts"

    uid = db.Column(db.Integer, index=True)
    name = db.Column(db.String(64))
    adr_id = db.Column(db.Integer, db.ForeignKey('c_ad_rules.id'))
    config = db.Column(db.JSON)


class CIFilterPerms(Model):
    __tablename__ = "c_ci_filter_perms"

    name = db.Column(db.String(64), index=True)
    type_id = db.Column(db.Integer, db.ForeignKey('c_ci_types.id'))
    ci_filter = db.Column(db.Text)
    attr_filter = db.Column(db.Text)
    id_filter = db.Column(db.JSON)  # {node_path: unique_value}

    rid = db.Column(db.Integer, index=True)


class InnerKV(Model):
    __tablename__ = "c_kv"

    key = db.Column(db.String(128), index=True)
    value = db.Column(db.Text)


class IPAMSubnetScan(Model):
    __tablename__ = "c_ipam_subnet_scans"

    ci_id = db.Column(db.Integer, index=True, nullable=False)
    scan_enabled = db.Column(db.Boolean, default=True)
    rule_updated_at = db.Column(db.DateTime)
    last_scan_time = db.Column(db.DateTime)

    # scan rules
    agent_id = db.Column(db.String(8), index=True)
    cron = db.Column(db.String(128))


class IPAMSubnetScanHistory(Model2):
    __tablename__ = "c_ipam_subnet_scan_histories"

    subnet_scan_id = db.Column(db.Integer, index=True)
    exec_id = db.Column(db.String(64), index=True)
    cidr = db.Column(db.String(18), index=True)
    start_at = db.Column(db.DateTime)
    end_at = db.Column(db.DateTime)
    status = db.Column(db.Integer, default=0)  # 0 is ok
    stdout = db.Column(db.Text)
    ip_num = db.Column(db.Integer)
    ips = db.Column(db.JSON)  # keep only the last 10 records


class IPAMOperationHistory(Model2):
    __tablename__ = "c_ipam_operation_histories"

    from api.lib.cmdb.ipam.const import OperateTypeEnum

    uid = db.Column(db.Integer, index=True)
    cidr = db.Column(db.String(18), index=True)
    operate_type = db.Column(db.Enum(*OperateTypeEnum.all()))
    description = db.Column(db.Text)


class DCIMOperationHistory(Model2):
    __tablename__ = "c_dcim_operation_histories"

    from api.lib.cmdb.dcim.const import OperateTypeEnum

    uid = db.Column(db.Integer, index=True)
    rack_id = db.Column(db.Integer, index=True)
    ci_id = db.Column(db.Integer, index=True)
    operate_type = db.Column(db.Enum(*OperateTypeEnum.all()))
