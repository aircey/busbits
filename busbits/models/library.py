from enum import Enum
from typing import Dict, List

from busbits.models import DOMAIN_ONLY_ENTITY, ROOT_DOMAIN, WithSchema, vol
from busbits.models.device import BindingDefinition, Device, Field
from busbits.models.generator import BusbitsGenerator, generator_loader_schema


class Action:
    dimension: "Dimension"
    device_slug: str
    entity_slug: str
    field: Field

    def __init__(
        self, dimension: "Dimension", device_slug: str, entity_slug: str, field: Field
    ):
        self.dimension = dimension
        self.device_slug = device_slug
        self.entity_slug = entity_slug
        self.field = field

    def __repr__(self):
        return (
            f"Action(device_slug={self.device_slug}, "
            f"entity_slug={self.entity_slug}, field={self.field})"
        )


class DimensionScope(Enum):
    UNDEFINED = 0
    DOMAIN_ONLY = 1
    ENTITY = 2


class Dimension:
    domain: "Domain"
    slug: str
    scope: DimensionScope
    actions: Dict[tuple[str, str], Action]

    def __init__(self, domain: "Domain", slug: str):
        self.domain = domain
        self.slug = slug
        self.scope = DimensionScope.UNDEFINED
        self.actions = {}

    def add_action(self, device_slug: str, entity_slug: str, field: Field):
        if (device_slug, entity_slug) in self.actions:
            raise ValueError("Action has already been defined.")

        entity = self.domain.fetch_entity(entity_slug)

        if self.scope == DimensionScope.DOMAIN_ONLY and not entity.is_domain_only:
            raise ValueError(
                "Action for defined entity in domain-only dimension is not allowed."
            )
        if self.scope == DimensionScope.ENTITY and entity.is_domain_only:
            raise ValueError(
                "Action for domain-only entity in defined dimension is not allowed."
            )
        if self.scope == DimensionScope.UNDEFINED:
            self.scope = (
                DimensionScope.DOMAIN_ONLY
                if entity.is_domain_only
                else DimensionScope.ENTITY
            )
        action = Action(self, device_slug, entity_slug, field)
        self.actions[(device_slug, entity_slug)] = action
        return action

    @property
    def has_read_action(self) -> bool:
        for action in self.actions.values():
            if action.field.can_read:
                return True
        return False

    @property
    def has_write_action(self) -> bool:
        for action in self.actions.values():
            if action.field.can_write:
                return True
        return False

    def __repr__(self):
        return (
            f"Dimension(slug={self.slug}, scope={self.scope}, actions={self.actions})"
        )


class Entity:
    domain: "Domain"
    slug: str
    is_domain_only: bool

    def __init__(self, domain: "Domain", slug: str):
        self.domain = domain
        self.slug = slug
        self.is_domain_only = slug == DOMAIN_ONLY_ENTITY

    def __repr__(self):
        return f"Entity(slug={self.slug}), "


class Domain:
    lib: "Library"
    slug: str
    is_root: bool
    dimensions: Dict[str, Dimension]
    domain_only_entity: Entity
    entities: Dict[str, Entity]

    def __init__(self, lib: "Library", slug: str):
        self.lib = lib
        self.is_root = slug == ROOT_DOMAIN
        self.slug = slug
        self.dimensions = {}
        self.domain_only_entity = Entity(self, DOMAIN_ONLY_ENTITY)
        self.entities = {}

    def fetch_entity(self, entity_slug: str) -> Entity:
        if entity_slug == DOMAIN_ONLY_ENTITY:
            return self.domain_only_entity
        if entity_slug in self.entities:
            return self.entities[entity_slug]

        entity = Entity(self, entity_slug)
        self.entities[entity_slug] = entity
        return entity

    def fetch_dimension(self, dimension_slug: str) -> Dimension:
        if dimension_slug in self.dimensions:
            return self.dimensions[dimension_slug]

        dimension = Dimension(self, dimension_slug)
        self.dimensions[dimension_slug] = dimension
        return dimension

    def __repr__(self):
        return (
            f"Domain(slug={self.slug}, dimensions={self.dimensions}, "
            f"entities={self.entities})"
        )


class Library(WithSchema):
    AUTO_PROPS = ["name", "description", "slug", "generators"]
    name: str
    description: str
    generators: List[BusbitsGenerator]

    devices: Dict[str, Device]
    domains: Dict[str, Domain]

    @classmethod
    def _build_schema(cls) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("description"): str,
                vol.Required("slug"): str,
                vol.Required("devices"): [
                    {
                        vol.Required("slug"): str,
                        vol.Required("definition"): Device.vol_may_coerce(),
                    }
                ],
                vol.Required("generators"): [generator_loader_schema],
            }
        )

    def __init__(self, props: Dict):
        super().__init__(props)
        self.devices = {}
        self.domains = {}

        for device in self.validated_props["devices"]:
            device["definition"].library = self
            self.add_device(device["slug"], device["definition"])

    def add_device(self, device_slug: str, device: Device):
        if device_slug in self.devices:
            raise ValueError(f"Device with slug '{device_slug}' already exists.")
        for register in device.registers:
            for field in register.fields:
                binding_def = field.binding
                if not isinstance(binding_def, BindingDefinition):
                    continue
                self.fetch_domain(binding_def.domain).fetch_dimension(
                    binding_def.dimension
                ).add_action(device_slug, binding_def.entity, field)

        self.devices[device_slug] = device

    def fetch_domain(self, domain_slug: str) -> Domain:
        if domain_slug in self.domains:
            return self.domains[domain_slug]

        domain = Domain(self, domain_slug)
        self.domains[domain_slug] = domain
        return domain

    def __repr__(self):
        return (
            f"Library(name={self.name}, devices={self.devices},"
            f"domains={self.domains}, generators={self.generators})"
        )
