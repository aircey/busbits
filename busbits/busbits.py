import yaml

from busbits.models.device import Device


def parse_busbits_yaml(file_path):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

    return Device(data)


def main():
    yaml_file_path = "./busbits/devices/testdevice/_root.yaml"
    try:
        device = parse_busbits_yaml(yaml_file_path)
        print("YAML parsed and validated successfully:")
        print(device)

    except Exception as e:
        print(f"Validation error: {e}")
        raise e


if __name__ == "__main__":
    main()
