import pathlib

import yaml
import yaml_include

from busbits.models.library import DimensionScope, Library

py_include = yaml_include.Constructor()
yaml.add_constructor("!include", py_include)


def parse_busbits_yaml(file_path):
    py_include.base_dir = pathlib.Path(file_path).parent
    with open(file_path, "r") as file:
        data = yaml.full_load(file)

    if "library" in data:
        return Library(data["library"])
    else:
        raise Exception("Missing library definition")


def main():

    # return test()
    yaml_file_path = "./busbits/axpdoc.yaml"
    try:
        lib = parse_busbits_yaml(yaml_file_path)

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
