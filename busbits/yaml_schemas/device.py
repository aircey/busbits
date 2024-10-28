from voluptuous import Schema, Required, Optional, All, Any, Range

VALUES_SCHEMA = Schema(
    {
        Optional("range"): {
            Required("offset"): int,
            Required("step"): int,
            Required("unit"): str,
        },
        Optional("enum"): {str: int},
        Optional("boolean"): {bool: int},
    }
)


DEVICE_SCHEMA = Schema(
    {
        Required("device"): {
            Required("name"): str,
            Required("description"): str,
            Optional("registers"): [
                {
                    Required("name"): str,
                    Required("address"): int,
                    Required("size"): All(int, Range(min=1)),
                    Required("access"): Any("r", "w", "rw"),
                    Required("description"): str,
                    Optional("fields"): [
                        {
                            Required("name"): str,
                            Required("bit_offset"): All(int, Range(min=0)),
                            Required("bit_length"): All(int, Range(min=1)),
                            Optional("values"): VALUES_SCHEMA,
                        }
                    ],
                }
            ],
            Optional("commands"): [
                {
                    Required("name"): str,
                    Required("command_code"): int,
                    Required("description"): str,
                    Optional("parameters"): [
                        {
                            Required("name"): str,
                            Required("description"): str,
                            Optional("values"): VALUES_SCHEMA,
                        }
                    ],
                }
            ],
        },
    }
)
