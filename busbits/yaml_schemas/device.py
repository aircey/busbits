from voluptuous import Schema, Required, Optional, All, Any, Range

VALUE_HOLDER = {
    Optional("range"): {
        Required("offset"): int,
        Required("step"): int,
        Required("unit"): str,
    },
    Optional("values"): {str: int},
    Optional("boolean"): {bool: int},
}


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
                        Schema(
                            {
                                Required("name"): str,
                                Required("bit_offset"): All(int, Range(min=0)),
                                Required("bit_length"): All(int, Range(min=1)),
                            }
                        ).extend(VALUE_HOLDER)
                    ],
                }
            ],
            Optional("commands"): [
                {
                    Required("name"): str,
                    Required("command_code"): int,
                    Required("description"): str,
                    Optional("parameters"): [
                        Schema(
                            {
                                Required("name"): str,
                                Required("description"): str,
                            }
                        ).extend(VALUE_HOLDER)
                    ],
                }
            ],
        },
    }
)
