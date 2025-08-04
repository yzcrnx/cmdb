# -*- coding:utf-8 -*- 

import base64

import elasticsearch
import redis
import six
from Crypto.Cipher import AES
from elasticsearch import Elasticsearch
from flask import current_app

from api.lib.secrets.inner import InnerCrypt
from api.lib.secrets.inner import KeyManage


class BaseEnum(object):
    _ALL_ = set()  # type: Set[str]

    @classmethod
    def is_valid(cls, item):
        return item in cls.all()

    @classmethod
    def all(cls):
        if not cls._ALL_:
            cls._ALL_ = {
                getattr(cls, attr)
                for attr in dir(cls)
                if not attr.startswith("_") and not callable(getattr(cls, attr))
            }
        return cls._ALL_


def get_page(page):
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1
    return page if page >= 1 else 1


def get_page_size(page_size):
    if page_size == "all":
        return page_size

    try:
        page_size = int(page_size)
    except (ValueError, TypeError):
        page_size = current_app.config.get("DEFAULT_PAGE_COUNT")
    return page_size if page_size >= 1 else current_app.config.get("DEFAULT_PAGE_COUNT")


def handle_bool_arg(arg):
    if arg in current_app.config.get("BOOL_TRUE"):
        return True
    return False


def handle_arg_list(arg):
    if isinstance(arg, (list, dict)):
        return arg

    if arg == 0:
        return [0]

    if not arg:
        return []

    if isinstance(arg, (six.integer_types, float)):
        return [arg]
    return list(filter(lambda x: x != "", arg.strip().split(","))) if isinstance(arg, six.string_types) else arg


class RedisHandler(object):
    def __init__(self, flask_app=None):
        self.flask_app = flask_app
        self.r = None

    def init_app(self, app):
        self.flask_app = app
        config = self.flask_app.config
        try:
            pool = redis.ConnectionPool(
                max_connections=config.get("REDIS_MAX_CONN"),
                host=config.get("CACHE_REDIS_HOST"),
                port=config.get("CACHE_REDIS_PORT"),
                password=config.get("CACHE_REDIS_PASSWORD"),
                db=config.get("REDIS_DB") or 0)
            self.r = redis.Redis(connection_pool=pool)
        except Exception as e:
            current_app.logger.warning(str(e))
            current_app.logger.error("init redis connection failed")

    def get(self, key_ids, prefix):
        try:
            value = self.r.hmget(prefix, key_ids)
        except Exception as e:
            current_app.logger.error("get redis error, {0}".format(str(e)))
            return
        return value

    def _set(self, obj, prefix):
        try:
            self.r.hmset(prefix, obj)
        except Exception as e:
            current_app.logger.error("set redis error, {0}".format(str(e)))

    def create_or_update(self, obj, prefix):
        self._set(obj, prefix)

    def delete(self, key_id, prefix):
        try:
            ret = self.r.hdel(prefix, key_id)
            if not ret:
                current_app.logger.warning("[{0}] is not in redis".format(key_id))
        except Exception as e:
            current_app.logger.error("delete redis key error, {0}".format(str(e)))

    def set_str(self, key, value, expired=None):
        try:
            if expired:
                self.r.setex(key, expired, value)
            else:
                self.r.set(key, value)
        except Exception as e:
            current_app.logger.error("set redis error, {0}".format(str(e)))

    def get_str(self, key):
        try:
            value = self.r.get(key)
        except Exception as e:
            current_app.logger.error("get redis error, {0}".format(str(e)))
            return
        return value


class ESHandler(object):
    def __init__(self, flask_app=None):
        self.flask_app = flask_app
        self.es = None
        self.index = "cmdb"

    def init_app(self, app):
        self.flask_app = app
        config = self.flask_app.config
        if config.get('ES_USER') and config.get('ES_PASSWORD'):
            uri = "http://{}:{}@{}:{}/".format(config.get('ES_USER'), config.get('ES_PASSWORD'),
                                               config.get('ES_HOST'), config.get('ES_PORT'))
        else:
            uri = "{}:{}".format(config.get('ES_HOST'), config.get('ES_PORT') or 9200)
        self.es = Elasticsearch(uri,
                                timeout=10,
                                max_retries=3,
                                retry_on_timeout=True,
                                retry_on_status=(502, 503, 504, "N/A"),
                                maxsize=10)
        try:
            if not self.es.indices.exists(index=self.index):
                self.es.indices.create(index=self.index)
        except elasticsearch.exceptions.RequestError as ex:
            if ex.error != 'resource_already_exists_exception':
                raise

    def update_mapping(self, field, value_type, other):
        body = {
            "properties": {
                field: {"type": value_type},
            }}
        body['properties'][field].update(other)

        self.es.indices.put_mapping(
            index=self.index,
            body=body
        )

    def get_index_id(self, ci_id):
        try:
            return self._get_index_id(ci_id)
        except:
            return self._get_index_id(ci_id)

    def _get_index_id(self, ci_id):
        query = {
            'query': {
                'match': {'ci_id': ci_id}
            },
        }
        res = self.es.search(index=self.index, body=query)
        if res['hits']['hits']:
            return res['hits']['hits'][-1].get('_id')

    def create(self, body):
        return self.es.index(index=self.index, body=body).get("_id")

    def update(self, ci_id, body):
        _id = self.get_index_id(ci_id)

        if _id:
            return self.es.index(index=self.index, id=_id, body=body).get("_id")

    def create_or_update(self, ci_id, body):
        try:
            self.update(ci_id, body) or self.create(body)
        except KeyError:
            self.create(body)

    def delete(self, ci_id):
        try:
            _id = self.get_index_id(ci_id)
        except KeyError:
            return

        if _id:
            self.es.delete(index=self.index, id=_id)

    def read(self, query, filter_path=None):
        filter_path = filter_path or []
        if filter_path:
            filter_path.append('hits.total')

        res = self.es.search(index=self.index, body=query, filter_path=filter_path)
        if res['hits'].get('hits'):
            return (res['hits']['total']['value'],
                    [i['_source'] for i in res['hits']['hits']],
                    res.get("aggregations", {}))
        else:
            return 0, [], {}


class AESCrypto(object):
    BLOCK_SIZE = 16  # Bytes
    pad = lambda s: s + ((AESCrypto.BLOCK_SIZE - len(s) % AESCrypto.BLOCK_SIZE) *
                         chr(AESCrypto.BLOCK_SIZE - len(s) % AESCrypto.BLOCK_SIZE))
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    iv = '0102030405060708'

    @staticmethod
    def key():
        key = current_app.config.get("SECRET_KEY")[:16]
        if len(key) < 16:
            key = "{}{}".format(key, (16 - len(key)) * "x")

        return key.encode('utf8')

    @classmethod
    def encrypt(cls, data):
        data = cls.pad(data)
        cipher = AES.new(cls.key(), AES.MODE_CBC, cls.iv.encode('utf8'))

        return base64.b64encode(cipher.encrypt(data.encode('utf8'))).decode('utf8')

    @classmethod
    def decrypt(cls, data):
        encode_bytes = base64.decodebytes(data.encode('utf8'))
        cipher = AES.new(cls.key(), AES.MODE_CBC, cls.iv.encode('utf8'))
        text_decrypted = cipher.decrypt(encode_bytes)

        return cls.unpad(text_decrypted).decode('utf8')


class Crypto(AESCrypto):
    @classmethod
    def encrypt(cls, data):
        from api.lib.secrets.secrets import InnerKVManger

        if not KeyManage(backend=InnerKVManger()).is_seal():
            res, status = InnerCrypt().encrypt(data)
            if status:
                return res

        return AESCrypto().encrypt(data)

    @classmethod
    def decrypt(cls, data):
        from api.lib.secrets.secrets import InnerKVManger

        if not KeyManage(backend=InnerKVManger()).is_seal():
            try:
                res, status = InnerCrypt().decrypt(data)
                if status:
                    return res
            except:
                pass

        try:
            return AESCrypto().decrypt(data)
        except:
            return data
