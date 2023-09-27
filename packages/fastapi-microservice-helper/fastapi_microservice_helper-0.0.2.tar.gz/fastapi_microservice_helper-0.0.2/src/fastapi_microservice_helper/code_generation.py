import dataclasses
import typing
from dataclasses import field, dataclass, is_dataclass, _MISSING_TYPE
from enum import Enum
from types import GenericAlias

from pydantic.fields import ModelField
from pydantic.main import ModelMetaclass
from pydash import group_by

from .helper import oneline, tab, get_generic_type


@dataclass
class GenerationImportModuleDetail:
    module: str
    type: str


@dataclass
class GenerationPropertyDetail:
    name: str
    type: typing.Optional[str] = None
    default_value: typing.Optional[any] = None
    default_factory: typing.Optional[any] = None
    allow_none: bool = False


@dataclass
class GenerationMethodDetail:
    name: str
    params: list[GenerationPropertyDetail] = field(default_factory=list)
    body: str = None
    response: str = None


@dataclass
class GenerationClassDetail:
    class_name: str
    parent_name: str = None
    methods: list[GenerationMethodDetail] = field(default_factory=list)
    properties: list[GenerationPropertyDetail] = field(default_factory=list)
    is_dataclass: bool = False


class Generation:
    def generate(self, class_detail: GenerationClassDetail):
        return self.generate_class(class_detail)

    def generate_import_modules(self, list_import_module: list[GenerationImportModuleDetail]):
        content = ''
        import_modules = group_by(list_import_module, 'module')
        for key in import_modules.keys():
            types = map(lambda import_module: import_module.type, import_modules[key])
            content += oneline(f'from {key} import {",".join(types)}')
        return content

    def generate_class(self, class_detail: GenerationClassDetail):
        parent_name = f'({class_detail.parent_name})' if class_detail.parent_name else ''
        content = oneline('@dataclass') if class_detail.is_dataclass else ''
        content += oneline(f'class {class_detail.class_name}{parent_name}:')
        content += self.generate_properties(class_detail.properties)
        content += self.generate_methods(class_detail.methods)
        return content

    def generate_methods(self, methods: list[GenerationMethodDetail]):
        content = ''
        for method in methods:
            content += tab(self.generate_method(method))
            content += '\r\n'
        return content

    def generate_method(self, method: GenerationMethodDetail):
        paramList = ", ".join(map(lambda param: f'{param.name}: {param.type}', method.params))
        content = oneline(
            f'def {method.name}(self, {paramList}, option: MicroserviceOption = None) -> {method.response}:')
        content += oneline(tab(method.body))

        return content

    def generate_properties(self, properties: list[GenerationPropertyDetail]):
        content = ''
        for property in properties:
            content += tab(self.generate_property(property))
            content += '\r\n'
        return content

    def generate_property(self, property: GenerationPropertyDetail):
        content = f'{property.name}: {property.type}' if property.type else property.name
        if property.default_value:
            content += f'={property.default_value}'
        if property.default_value is None and property.allow_none:
            content += f'=None'
        elif property.default_factory:
            content += f'=field(default_factory={property.default_factory})'
        return content


class CloneGeneration:
    def clone_class_to_dataclass(self, ref_class):
        if type(ref_class) is ModelMetaclass:
            class_detail = GenerationClassDetail(class_name=ref_class.__name__, is_dataclass=True)
            for key in ref_class.__fields__.keys():
                property: ModelField = ref_class.__fields__[key]
                type_name = property.type_.__name__
                if isinstance(property.annotation, GenericAlias):
                    type_name = get_generic_type(property.annotation)
                property_detail = GenerationPropertyDetail(
                    property.name,
                    type=type_name,
                    default_value=property.default,
                    default_factory=property.default_factory,
                    allow_none=property.allow_none
                )
                class_detail.properties.append(property_detail)

            return Generation().generate(class_detail)
        else:
            if issubclass(ref_class, Enum):
                return self.clone_enum(ref_class)
            elif is_dataclass(ref_class):
                return self.clone_dataclass(ref_class)
            else:
                print(type(ref_class))
                print("Need to implement this type", ref_class)

        return ''

    def clone_enum(self, ref_class: type[Enum]):
        class_detail = GenerationClassDetail(class_name=ref_class.__name__, parent_name=Enum.__name__)
        for member in ref_class:
            class_detail.properties.append(GenerationPropertyDetail(
                name=member.name,
                default_value=member.value
            ))
        return Generation().generate(class_detail)

    def clone_dataclass(self, ref_class: type[dataclasses]):
        class_detail = GenerationClassDetail(class_name=ref_class.__name__,
                                             is_dataclass=True)
        for field in dataclasses.fields(ref_class):
            type_name = field.type.__name__
            if isinstance(field.type, GenericAlias):
                type_name = get_generic_type(field.type)
            property_detail = GenerationPropertyDetail(
                name=field.name,
                type=type_name,
                default_value=field.default if not type(field.default) is _MISSING_TYPE else None,
                default_factory=field.default_factory if not type(field.default_factory) is _MISSING_TYPE else None
            )
            class_detail.properties.append(property_detail)
        return Generation().generate(class_detail)
