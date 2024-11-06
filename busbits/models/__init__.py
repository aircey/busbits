import abc
from typing import Dict, List, Optional

import voluptuous as vol

ROOT_DOMAIN = "_root"
DOMAIN_ONLY_ENTITY = "_domain_only"


class WithSchema(metaclass=abc.ABCMeta):
    _SCHEMA: Optional[vol.Schema] = None
    AUTO_PROPS: List = []

    validated_props: Dict = {}

    def __init__(self, props: Dict) -> None:
        cls = self.__class__
        self.validated_props = cls.validate_schema(props)
        for key in cls.AUTO_PROPS:
            if key not in self.validated_props:
                raise Exception(f"Missing required property: {key}")
            setattr(self, key, self.validated_props[key])

    @classmethod
    @abc.abstractmethod
    def _build_schema(cls) -> vol.Schema:
        pass

    @classmethod
    def validate_schema(cls, data) -> Dict:
        if cls._SCHEMA is None:
            cls._SCHEMA = cls._build_schema()
        return cls._SCHEMA(data)

    @classmethod
    def vol_isinstance(cls, obj):
        if not isinstance(obj, cls):
            raise ValueError
        return obj

    @classmethod
    def vol_may_coerce(cls):
        return vol.Any(cls.vol_isinstance, vol.Coerce(cls))

    @classmethod
    def vol_may_coerce_nullable(cls):
        return vol.Any(cls.vol_may_coerce(), None)
