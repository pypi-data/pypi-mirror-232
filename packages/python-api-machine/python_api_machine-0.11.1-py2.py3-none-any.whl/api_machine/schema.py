from dataclasses import make_dataclass, field, asdict, fields
import json

from pydantic import create_model, ValidationError
from pydantic.dataclasses import dataclass
from pydantic.json import pydantic_encoder


def dataclass_to_model(dc):
    return dataclass(dc)


def serialize(i, to_string=False):
    d = asdict(i)
    version = getattr(i, '__version__', 0)

    if hasattr(i, "__pydantic_model__"):
        d = i.__pydantic_model__(**d).dict()

    d['__version__'] = version
    j = json.dumps(d, default=pydantic_encoder)
    if to_string:
        return j

    return json.loads(j)


def extract_schema(name, entity, include=None):
    fields = entity.fields(include, aslist=True)
    cls = type(
        name, (),
        dict((f[0], f[2]) for f in fields)
    )
    cls.__annotations__ = dict(
        (f[0], f[1]) for f in fields
    )
    return dataclass(cls)


def filter_dict_to_schema(entity: dataclass, payload: dict):
    fs = [
        f.name for f in fields(entity)
    ]
    return dict(
        (key, value) for key, value in payload.items()
        if key in fs
    )
