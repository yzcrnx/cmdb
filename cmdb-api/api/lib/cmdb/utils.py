# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import datetime
import json
import re

import six
from flask import current_app

import api.models.cmdb as model
from api.lib.cmdb.cache import AttributeCache
from api.lib.cmdb.const import ValueTypeEnum
from api.lib.cmdb.resp_format import ErrFormat

TIME_RE = re.compile(r'(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d')


class ValueDeserializeError(Exception):
    pass


def string2int(x):
    v = int(float(x))
    if v > 2147483647:
        raise ValueDeserializeError(ErrFormat.attribute_value_out_of_range)

    return v


def str2date(x):

    try:
        return datetime.datetime.strptime(x, "%Y-%m-%d").date()
    except ValueError:
        pass

    try:
        return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").date()
    except ValueError:
        pass


def str2datetime(x):

    x = x.replace('T', ' ')
    x = x.replace('Z', '')

    try:
        return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass

    return datetime.datetime.strptime(x, "%Y-%m-%d %H:%M")


class ValueTypeMap(object):
    deserialize = {
        ValueTypeEnum.INT: string2int,
        ValueTypeEnum.FLOAT: float,
        ValueTypeEnum.TEXT: lambda x: x,
        ValueTypeEnum.TIME: lambda x: TIME_RE.findall(x)[0],
        ValueTypeEnum.DATETIME: str2datetime,
        ValueTypeEnum.DATE: str2date,
        ValueTypeEnum.JSON: lambda x: json.loads(x) if isinstance(x, six.string_types) and x else x,
        ValueTypeEnum.BOOL: lambda x: x in current_app.config.get('BOOL_TRUE'),
    }

    serialize = {
        ValueTypeEnum.INT: int,
        ValueTypeEnum.FLOAT: float,
        ValueTypeEnum.TEXT: lambda x: x if isinstance(x, six.string_types) else str(x),
        ValueTypeEnum.TIME: lambda x: x if isinstance(x, six.string_types) else str(x),
        ValueTypeEnum.DATE: lambda x: x.strftime("%Y-%m-%d") if not isinstance(x, six.string_types) else x,
        ValueTypeEnum.DATETIME: lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if not isinstance(x, six.string_types) else x,
        ValueTypeEnum.JSON: lambda x: json.loads(x) if isinstance(x, six.string_types) and x else x,
        ValueTypeEnum.BOOL: lambda x: x in current_app.config.get('BOOL_TRUE'),
    }

    serialize2 = {
        ValueTypeEnum.INT: int,
        ValueTypeEnum.FLOAT: float,
        ValueTypeEnum.TEXT: lambda x: x.decode() if not isinstance(x, six.string_types) else x,
        ValueTypeEnum.TIME: lambda x: x.decode() if not isinstance(x, six.string_types) else x,
        ValueTypeEnum.DATE: lambda x: (x.decode() if not isinstance(x, six.string_types) else x).split()[0],
        ValueTypeEnum.DATETIME: lambda x: x.decode() if not isinstance(x, six.string_types) else x,
        ValueTypeEnum.JSON: lambda x: json.loads(x) if isinstance(x, six.string_types) and x else x,
        ValueTypeEnum.BOOL: lambda x: x in current_app.config.get('BOOL_TRUE'),
    }

    choice = {
        ValueTypeEnum.INT: model.IntegerChoice,
        ValueTypeEnum.FLOAT: model.FloatChoice,
        ValueTypeEnum.TEXT: model.TextChoice,
        ValueTypeEnum.TIME: model.TextChoice,
        ValueTypeEnum.DATE: model.TextChoice,
        ValueTypeEnum.DATETIME: model.TextChoice,
    }

    table = {
        ValueTypeEnum.TEXT: model.CIValueText,
        ValueTypeEnum.JSON: model.CIValueJson,
        'index_{0}'.format(ValueTypeEnum.INT): model.CIIndexValueInteger,
        'index_{0}'.format(ValueTypeEnum.TEXT): model.CIIndexValueText,
        'index_{0}'.format(ValueTypeEnum.DATETIME): model.CIIndexValueDateTime,
        'index_{0}'.format(ValueTypeEnum.DATE): model.CIIndexValueDateTime,
        'index_{0}'.format(ValueTypeEnum.TIME): model.CIIndexValueText,
        'index_{0}'.format(ValueTypeEnum.FLOAT): model.CIIndexValueFloat,
        'index_{0}'.format(ValueTypeEnum.JSON): model.CIValueJson,
        'index_{0}'.format(ValueTypeEnum.BOOL): model.CIIndexValueInteger,
    }

    table_name = {
        ValueTypeEnum.TEXT: 'c_value_texts',
        ValueTypeEnum.JSON: 'c_value_json',
        'index_{0}'.format(ValueTypeEnum.INT): 'c_value_index_integers',
        'index_{0}'.format(ValueTypeEnum.TEXT): 'c_value_index_texts',
        'index_{0}'.format(ValueTypeEnum.DATETIME): 'c_value_index_datetime',
        'index_{0}'.format(ValueTypeEnum.DATE): 'c_value_index_datetime',
        'index_{0}'.format(ValueTypeEnum.TIME): 'c_value_index_texts',
        'index_{0}'.format(ValueTypeEnum.FLOAT): 'c_value_index_floats',
        'index_{0}'.format(ValueTypeEnum.JSON): 'c_value_json',
        'index_{0}'.format(ValueTypeEnum.BOOL): 'c_value_index_integers',
    }

    es_type = {
        ValueTypeEnum.INT: 'long',
        ValueTypeEnum.TEXT: 'text',
        ValueTypeEnum.DATETIME: 'text',
        ValueTypeEnum.DATE: 'text',
        ValueTypeEnum.TIME: 'text',
        ValueTypeEnum.FLOAT: 'float',
        ValueTypeEnum.JSON: 'object',
    }


class TableMap(object):
    def __init__(self, attr_name=None, attr=None, is_index=None):
        self.attr_name = attr_name
        self.attr = attr
        self.is_index = is_index

    @property
    def table(self):
        attr = AttributeCache.get(self.attr_name) if not self.attr else self.attr
        if attr.is_password or attr.is_link:
            self.is_index = False
        elif attr.value_type not in {ValueTypeEnum.TEXT, ValueTypeEnum.JSON}:
            self.is_index = True
        elif self.is_index is None:
            self.is_index = attr.is_index

        i = "index_{0}".format(attr.value_type) if self.is_index else attr.value_type

        return ValueTypeMap.table.get(i)

    @property
    def table_name(self):
        attr = AttributeCache.get(self.attr_name) if not self.attr else self.attr
        if attr.is_password or attr.is_link:
            self.is_index = False
        elif attr.value_type not in {ValueTypeEnum.TEXT, ValueTypeEnum.JSON}:
            self.is_index = True
        elif self.is_index is None:
            self.is_index = attr.is_index

        i = "index_{0}".format(attr.value_type) if self.is_index else attr.value_type

        return ValueTypeMap.table_name.get(i)
