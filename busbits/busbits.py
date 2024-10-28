import yaml

from busbits.models import Device
from .yaml_schemas.device import DEVICE_SCHEMA


def parse_busbits_yaml(file_path):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

    validated_data = DEVICE_SCHEMA(data)
    return validated_data


def main():
    yaml_file_path = "./busbits/devices/testdevice/_root.yaml"
    try:
        validated_data = parse_busbits_yaml(yaml_file_path)
        print("YAML parsed and validated successfully:")
    except Exception as e:
        print(f"Validation error: {e}")

    device = Device.from_dict(validated_data["device"])
    print(device)


if __name__ == "__main__":
    main()
