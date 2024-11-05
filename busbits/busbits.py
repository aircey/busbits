import yaml

from busbits.models.device import Device
from busbits.models.library import DimensionScope, Library


def parse_busbits_yaml(file_path):
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

    return Device(data)


def main():
    yaml_file_path = "./busbits/devices/testdevice/_root.yaml"
    try:
        device = parse_busbits_yaml(yaml_file_path)
        print("YAML parsed and validated successfully:")
        # print(device)

        lib = Library("test")
        lib.add_device("testdevice", device)
        print(lib)

        for domain in lib.domains.values():
            for dimension in domain.dimensions.values():
                if dimension.scope == DimensionScope.UNDEFINED:
                    continue
                can_read = dimension.has_read_action
                can_write = dimension.has_write_action
                domain_only = dimension.scope == DimensionScope.DOMAIN_ONLY

                if can_read:
                    if domain.is_root and domain_only:
                        print(f"get_{dimension.slug}()")
                    elif domain.is_root and not domain_only:
                        print(f"get_{dimension.slug}(root::)")
                    elif not domain.is_root and domain_only:
                        print(f"get_{domain.slug}_{dimension.slug}()")
                    elif not domain.is_root and not domain_only:
                        print(f"get_{domain.slug}_{dimension.slug}({domain.slug}::)")
                if can_write:
                    if domain.is_root and domain_only:
                        print(f"set_{dimension.slug}(val)")
                    elif domain.is_root and not domain_only:
                        print(f"set_{dimension.slug}(root::, val)")
                    elif not domain.is_root and domain_only:
                        print(f"set_{domain.slug}_{dimension.slug}(val)")
                    elif not domain.is_root and not domain_only:
                        print(
                            f"set_{domain.slug}_{dimension.slug}({domain.slug}::, val)"
                        )

    except Exception as e:
        print(f"Validation error: {e}")
        raise e


if __name__ == "__main__":
    main()
