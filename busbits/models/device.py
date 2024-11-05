import abc
from enum import Enum
from typing import Dict, List, Optional

import voluptuous as vol

from busbits.models import WithSchema


class Access(Enum):
    READ = "r"
    WRITE = "w"
    READ_WRITE = "rw"


class ValuesHolder(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def size(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def can_read(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def can_write(self) -> bool:
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


class BindingDefinition(WithSchema):
    value_holder: ValuesHolder

    AUTO_PROPS = ["domain", "dimension", "entity"]
    domain: str
    dimension: str
    entity: str

    @classmethod
    def _build_schema(cls) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("domain"): str,
                vol.Required("dimension"): str,
                vol.Required("entity"): str,
            }
        )

    def __init__(self, props: Dict):
        super().__init__(props)

    def __repr__(self):
        return (
            f"BindingDefinition(domain={self.domain}, dimension={self.dimension}, "
            f"entity={self.entity})"
        )


class Field(ValuesHolder, WithSchema):
    register: "Register"

    AUTO_PROPS = ["name", "bit_offset", "bit_length", "access", "binding", "values"]
    name: str
    bit_offset: int
    bit_length: int
    access: Access
    binding: Optional[BindingDefinition]
    values: Values

    @classmethod
    def _build_schema(cls) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("bit_offset"): vol.All(int, vol.Range(min=0)),
                vol.Required("bit_length"): vol.All(int, vol.Range(min=1)),
                vol.Required("access"): vol.Coerce(Access),
                vol.Optional(
                    "binding", default=None
                ): BindingDefinition.vol_may_coerce_nullable(),
                vol.Optional("values", default={}): Values.vol_may_coerce(),
            }
        )

    def __init__(self, props: Dict):
        super().__init__(props)

        if self.binding is not None:
            self.binding.value_holder = self

        self.values.value_holder = self

    @property
    def size(self) -> int:
        return self.bit_length

    @property
    def can_read(self) -> bool:
        return self.access in [Access.READ, Access.READ_WRITE]

    @property
    def can_write(self) -> bool:
        return self.access in [Access.WRITE, Access.READ_WRITE]

    def __repr__(self):
        return (
            f"Field(name={self.name}, bit_offset={self.bit_offset}, "
            f"bit_length={self.bit_length}, access={self.access}, "
            f"binding={self.binding}, values={self.values})"
        )


class Register(WithSchema):
    device: "Device"

    AUTO_PROPS = ["name", "address", "size", "description", "fields"]
    name: str
    address: int
    size: int
    description: str
    fields: List[Field]

    @classmethod
    def _build_schema(cls) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("address"): int,
                vol.Required("size"): vol.All(int, vol.Range(min=1)),
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
            f"Register(name={self.name}, address={hex(self.address)}, "
            f"size={self.size}, description={self.description}, "
            f"fields={self.fields})"
        )


class CommandParameter(ValuesHolder, WithSchema):
    command: "Command"

    AUTO_PROPS = ["name", "description", "access", "values"]
    name: str
    description: str
    access: Access
    values: Values

    @classmethod
    def _build_schema(cls) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("description"): str,
                vol.Required("access"): vol.Coerce(Access),
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

    @property
    def can_read(self) -> bool:
        return self.access in [Access.READ, Access.READ_WRITE]

    @property
    def can_write(self) -> bool:
        return self.access in [Access.WRITE, Access.READ_WRITE]

    def __repr__(self):
        return (
            f"CommandParameter(name={self.name}, description={self.description}, "
            f"access={self.access}, values={self.values})"
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
            f"Command(name={self.name}, command_code={hex(self.command_code)}, "
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
            f"Device(name={self.name}, description={self.description}, "
            f"registers={self.registers}, commands={self.commands})"
        )
