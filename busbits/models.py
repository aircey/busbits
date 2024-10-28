from typing import List, Optional, Dict


class Range:
    def __init__(self, offset: int, step: int, unit: str):
        self.offset = offset
        self.step = step
        self.unit = unit

    def __repr__(self):
        return f"Range(offset={self.offset}, step={self.step}, unit={self.unit})"

    @classmethod
    def from_dict(cls, data):
        d = dict(data)
        return cls(**d)


class Values:
    def __init__(
        self,
        range: Optional[Range] = None,
        enum: Optional[Dict[str, int]] = None,
        boolean: Optional[Dict[bool, int]] = None,
    ):
        self.range = range
        self.enum = enum
        self.boolean = boolean

    def __repr__(self):
        return f"Values(range={self.range}, enum={self.enum}, boolean={self.boolean})"

    @classmethod
    def from_dict(cls, data):
        d = dict(data)
        d["range"] = Range.from_dict(d.get("range")) if d.get("range") else None
        return cls(**d)


class Field:
    def __init__(
        self,
        name: str,
        bit_offset: int,
        bit_length: int,
        values: Optional[Values] = None,
    ):
        self.name = name
        self.bit_offset = bit_offset
        self.bit_length = bit_length
        self.values = values

    def __repr__(self):
        return (
            f"Field(name={self.name}, bit_offset={self.bit_offset},"
            f"bit_length={self.bit_length}, values={self.values},)"
        )

    @classmethod
    def from_dict(cls, data):
        d = dict(data)
        d["values"] = Values.from_dict(d.get("values")) if d.get("values") else None
        return cls(**d)


class Register:
    def __init__(
        self,
        name: str,
        address: int,
        size: int,
        access: str,
        description: str,
        fields: Optional[List[Field]] = None,
    ):
        self.name = name
        self.address = address
        self.size = size
        self.access = access
        self.description = description
        self.fields = fields or []

    def __repr__(self):
        return (
            f"Register(name={self.name}, address={hex(self.address)},"
            f"size={self.size}, access={self.access}, description={self.description},"
            f"fields={self.fields})"
        )

    @classmethod
    def from_dict(cls, data):
        d = dict(data)
        d["fields"] = [Field.from_dict(field) for field in d.get("fields", [])]
        return cls(**d)


class CommandParameter:
    def __init__(
        self,
        name: str,
        description: str,
        values: Optional[Values] = None,
    ):
        self.name = name
        self.description = description
        self.values = values

    def __repr__(self):
        return (
            f"CommandParameter(name={self.name}, description={self.description},"
            f"values={self.values})"
        )

    @classmethod
    def from_dict(cls, data):
        d = dict(data)
        d["values"] = Values.from_dict(d.get("values")) if d.get("values") else None
        return cls(**d)


class Command:
    def __init__(
        self,
        name: str,
        command_code: int,
        description: str,
        parameters: Optional[List[CommandParameter]] = None,
    ):
        self.name = name
        self.command_code = command_code
        self.description = description
        self.parameters = parameters or []

    def __repr__(self):
        return (
            f"Command(name={self.name}, command_code={hex(self.command_code)},"
            f"description={self.description}, parameters={self.parameters})"
        )

    @classmethod
    def from_dict(cls, data):
        d = dict(data)
        d["parameters"] = [
            CommandParameter.from_dict(param) for param in d.get("parameters", [])
        ]
        return cls(**d)


class Device:
    def __init__(
        self,
        name: str,
        description: str,
        registers: Optional[List[Register]] = None,
        commands: Optional[List[Command]] = None,
    ):
        self.name = name
        self.description = description
        self.registers = registers or []
        self.commands = commands or []

    def __repr__(self):
        return (
            f"Device(name={self.name}, description={self.description},"
            f"registers={self.registers}, commands={self.commands})"
        )

    @classmethod
    def from_dict(cls, data):
        d = dict(data)
        d["registers"] = [Register.from_dict(reg) for reg in d.get("registers", [])]
        d["commands"] = [Command.from_dict(cmd) for cmd in d.get("commands", [])]
        return cls(**d)
