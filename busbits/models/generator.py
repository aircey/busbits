import abc
from typing import TYPE_CHECKING, Dict, Type

from busbits.models import WithSchema, vol

if TYPE_CHECKING:
    from busbits.models.library import Library


class BusbitsGenerator(WithSchema):
    library: "Library"

    AUTO_PROPS = ["engine"]
    AUTO_OPTIONS = []
    slug: str
    engine: str

    def __init__(self, props: Dict) -> None:
        super().__init__(props)
        cls = self.__class__
        if "options" not in self.validated_props:
            raise Exception("Missing options")

        for key in cls.AUTO_OPTIONS:
            if key not in self.validated_props["options"]:
                raise Exception(f"Missing required property: {key}")
            setattr(self, f"opt_{key}", self.validated_props["options"][key])

    @abc.abstractmethod
    def generate(self) -> bool:
        pass

    @classmethod
    @abc.abstractmethod
    def _build_options_schema(cls) -> vol.Schema:
        pass

    @classmethod
    def _build_schema(cls):
        return vol.Schema(
            {
                vol.Required("engine"): str,
                vol.Required("options"): cls._build_options_schema(),
            }
        )


def generator_loader(eng: str) -> Type[BusbitsGenerator]:
    eng_cls = None
    if eng == "datasheet_md":
        from busbits.generators.datasheet_md import DatasheetMdGenerator

        eng_cls = DatasheetMdGenerator

    if eng_cls is not None:
        if not issubclass(eng_cls, BusbitsGenerator):
            raise ValueError(f"Generator engine '{eng}' is not a subclass of Generator")
        return eng_cls

    raise ValueError(f"Could not find generator engine '{eng}'")


def generator_loader_schema(data: Dict) -> vol.Schema:
    eng = data.get("engine", None)
    if not isinstance(eng, str):
        raise vol.ValueInvalid("Generator engine is not defined")

    try:
        cls = generator_loader(eng)
    except ValueError as e:
        raise vol.ValueInvalid(str(e))

    cls = generator_loader(eng)

    return cls.vol_may_coerce()(data)
