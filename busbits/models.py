from enum import Enum
from typing import List, Optional, Dict
import abc

import voluptuous as vol


class WithSchema(metaclass=abc.ABCMeta):
    _SCHEMA: Optional[vol.Schema] = None
    AUTO_PROPS: Dict = []

    validated_props: Dict = {}

    def __init__(self, props: Dict) -> None:
        cls = self.__class__
        self.validated_props = cls.validate_schema(props)
        for key in cls.AUTO_PROPS:
            if key not in self.validated_props:
                raise ValueError(f"Missing required property: {key}")
            setattr(self, key, self.validated_props[key])

    @classmethod
    @abc.abstractmethod
    def _build_schema(cls) -> vol.Schema:
        pass

    @classmethod
    def validate_schema(cls, data) -> vol.Schema:
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


class Access(Enum):
    READ = "r"
    WRITE = "w"
    READ_WRITE = "rw"


class ValuesHolder(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def size(self) -> int:
        pass


class Range(WithSchema):
    values: "Values"

    AUTO_PROPS = ["offset", "step", "unit"]
    offset: int
    step: int
    unit: str

    @classmethod
    def _build_schema(cls) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("offset"): int,
                vol.Required("step"): int,
                vol.Required("unit"): str,
            }
        )

    def __init__(self, props: Dict):
        super().__init__(props)

    def __repr__(self) -> str:
        return f"Range(offset={self.offset}, step={self.step}, unit={self.unit})"


class Values(WithSchema):
    value_holder: ValuesHolder

    AUTO_PROPS = ["range", "enum", "boolean"]
    range: Optional[Range]
    enum: Optional[Dict[str, int]]
    boolean: Optional[Dict[bool, int]]

    @classmethod
    def _build_schema(cls) -> vol.Schema:
        return vol.Schema(
            {
                vol.Optional("range", default=None): Range.vol_may_coerce_nullable(),
                # TODO: Enum and boolean should be objects
                vol.Optional("enum", default=None): vol.Any({str: int}, None),
                vol.Optional("boolean", default=None): vol.Any({bool: int}, None),
            }
        )

    def __init__(self, props: Dict):
        super().__init__(props)

        if self.range is not None:
            self.range.values = self

    def __repr__(self):
        return f"Values(range={self.range}, enum={self.enum}, boolean={self.boolean})"


class Field(ValuesHolder, WithSchema):
    register: "Register"

    AUTO_PROPS = ["name", "bit_offset", "bit_length", "values"]
    name: str
    bit_offset: int
    bit_length: int
    values: Values

    @classmethod
    def _build_schema(cls) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("bit_offset"): vol.All(int, vol.Range(min=0)),
                vol.Required("bit_length"): vol.All(int, vol.Range(min=1)),
                vol.Optional("values", default={}): Values.vol_may_coerce(),
            }
        )

    def __init__(self, props: Dict):
        super().__init__(props)

        self.values.value_holder = self

    @property
    def size(self) -> int:
        return self.bit_length

    def __repr__(self):
        return (
            f"Field(name={self.name}, bit_offset={self.bit_offset},"
            f"bit_length={self.bit_length}, values={self.values},)"
        )


class Register(WithSchema):
    device: "Device"

    AUTO_PROPS = ["name", "address", "size", "access", "description", "fields"]
    name: str
    address: int
    size: int
    access: Access
    description: str
    fields: List[Field]

    @classmethod
    def _build_schema(cls) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("address"): int,
                vol.Required("size"): vol.All(int, vol.Range(min=1)),
                vol.Required("access"): vol.Coerce(Access),
                vol.Required("description"): str,
                vol.Optional("fields", default=[]): [Field.vol_may_coerce()],
            }
        )

    def __init__(self, props: Dict):
        super().__init__(props)

        for field in self.fields:
            field.register = self

    def __repr__(self):
        return (
            f"Register(name={self.name}, address={hex(self.address)},"
            f"size={self.size}, access={self.access}, description={self.description},"
            f"fields={self.fields})"
        )


class CommandParameter(ValuesHolder, WithSchema):
    command: "Command"

    AUTO_PROPS = ["name", "description", "values"]
    name: str
    description: str
    values: Values

    @classmethod
    def _build_schema(cls) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("description"): str,
                vol.Optional("values", default={}): Values.vol_may_coerce(),
            }
        )

    def __init__(self, props: Dict):
        super().__init__(props)

        self.values.value_holder = self

    @property
    def size(self) -> int:
        # TODO: Implement size calculation
        return 0

    def __repr__(self):
        return (
            f"CommandParameter(name={self.name}, description={self.description},"
            f"values={self.values})"
        )


class Command(WithSchema):
    device: "Device"

    AUTO_PROPS = ["name", "command_code", "description", "parameters"]
    name: str
    command_code: int
    description: str
    parameters: List[CommandParameter]

    @classmethod
    def _build_schema(cls) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("command_code"): int,
                vol.Required("description"): str,
                vol.Optional("parameters", default=[]): [
                    CommandParameter.vol_may_coerce()
                ],
            }
        )

    def __init__(self, props: Dict):
        super().__init__(props)

        for param in self.parameters:
            param.command = self

    def __repr__(self):
        return (
            f"Command(name={self.name}, command_code={hex(self.command_code)},"
            f"description={self.description}, parameters={self.parameters})"
        )


class Device(WithSchema):
    AUTO_PROPS = ["name", "description", "registers", "commands"]
    name: str
    description: str
    registers: List[Register]
    commands: List[Command]

    @classmethod
    def _build_schema(cls) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("description"): str,
                vol.Optional("registers", default=[]): [Register.vol_may_coerce()],
                vol.Optional("commands", default=[]): [Command.vol_may_coerce()],
            }
        )

    def __init__(self, props: Dict):
        super().__init__(props)

        for reg in self.registers:
            reg.device = self

        for cmd in self.commands:
            cmd.device = self

    def __repr__(self):
        return (
            f"Device(name={self.name}, description={self.description},"
            f"registers={self.registers}, commands={self.commands})"
        )
