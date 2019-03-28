"""
Custom serializer tools
"""

from datetime import datetime
from dateutil.parser import parse as parse_date
import json


class PyJSONEncoder(json.JSONEncoder):
    """
    Convert python objects to a standards-based* JSON representation

    *Standard is flexible, but try to pick something that is well understood
    and has high adoption across a wide set of tools.  For example, dates are
    fairly well understood in ISO8601 format so it would be a good choice.

    Notes:
      * If encoding to a "complex" or object type include:
        * __type__ - type identifier
        * __value__ - value
        * (optional) __format__ - A specific encoding format, generally used
          for informative use
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return {
                '__type__': 'datetime',
                '__format__': 'iso8601',
                '__value__': obj.isoformat(),
            }
        else:
            return super(PyJSONEncoder, self).default(obj)


def py_json_decoder_hook(obj):
    """
    Decoder hook for complex object types output by PyJSONEncoder
    """
    if obj.get('__type__') == 'datetime':
        return parse_date(obj['__value__'])
    return obj


def py_json_serialize(data):
    return json.dumps(data, cls=PyJSONEncoder)


def py_json_deserialize(data):
    return json.loads(data, object_hook=py_json_decoder_hook)
