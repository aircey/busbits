from typing import Dict

from busbits.models import vol
from busbits.models.generator import BusbitsGenerator


class DatasheetMdGenerator(BusbitsGenerator):
    AUTO_OPTIONS = ["output"]
    opt_output: str

    def __init__(self, props: Dict) -> None:
        super().__init__(props)

    def generate(self) -> bool:
        return True

    @classmethod
    def _build_options_schema(cls):
        return vol.Schema({vol.Required("output"): str})

    def __repr__(self):
        return f"DatasheetMdGenerator(output={self.opt_output})"
