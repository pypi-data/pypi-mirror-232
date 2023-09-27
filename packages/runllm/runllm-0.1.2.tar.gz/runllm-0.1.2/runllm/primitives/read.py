from typing import List, Optional, Union, Any

from runllm.constants.enums import ImplementationType, PrimitiveType, ResourceType
from runllm.exceptions import (
    InvalidConfigurationException,
    InvalidResourceParamsException,
    UnknownImplementationTypeException,
)
from runllm.primitives.primitive import Primitive, initialize_primitive_within_task
from runllm.primitives.spec import CustomSpec, DefaultReadSpec, FunctionSpec
from runllm.resources.parameters import (
    GithubReadParams,
    GoogleDocsReadParams,
    NotionReadParams,
    ReadParams,
    RelationalDBReadParams,
)
from runllm.resources.resources import Resource


class ReadPrimitive(Primitive):
    inputs: List[Any]
    implementation_spec: Union[DefaultReadSpec, CustomSpec]

    def __init__(
        self,
        implementation_type: ImplementationType,
        resource: Optional[Resource] = None,
        params: Optional[ReadParams] = None,
        function_spec: Optional[FunctionSpec] = None,
    ):
        spec = self._construct_primitive_spec(
            implementation_type,
            resource,
            params,
            function_spec,
        )

        super().__init__(
            type=PrimitiveType.READ,
            implementation_type=implementation_type,
            dependencies=[],
            context_keys=[],
            inputs=[],  # type: ignore
            implementation_spec=spec,
        )

        initialize_primitive_within_task(self)

    def _construct_primitive_spec(
        self,
        implementation_type: ImplementationType,
        resource: Optional[Resource],
        params: Optional[ReadParams],
        function_spec: Optional[FunctionSpec],
    ) -> Union[DefaultReadSpec, CustomSpec]:
        if implementation_type == ImplementationType.DEFAULT:
            if not (resource and params):
                raise Exception(
                    "Both resource and resource params need to be specified for the Default implementation"
                )
            self._verify_default_implementation(
                resource,
                params,
            )
            return DefaultReadSpec(
                resource_id=resource.id,
                params=params,
            )
        elif implementation_type == ImplementationType.CUSTOM:
            # We already verify the custom implementation in the decorator
            if not function_spec:
                raise InvalidConfigurationException(
                    "CUSTOM type implementation expects a function spec passed in."
                )

            return CustomSpec(
                function_spec=function_spec,
            )
        else:
            raise UnknownImplementationTypeException("Unknown type of implementation")

    def _verify_default_implementation(self, resource: Resource, params: ReadParams) -> None:
        if resource.type == ResourceType.NOTION:
            if not isinstance(params, NotionReadParams):
                raise InvalidResourceParamsException(
                    "Parameters must be an instance of NotionReadParams."
                )
        elif resource.type == ResourceType.GOOGLE_DOCS:
            if not isinstance(params, GoogleDocsReadParams):
                raise InvalidResourceParamsException(
                    "Parameters must be an instance of GoogleDocsReadParams."
                )
        elif resource.type == ResourceType.GITHUB:
            if not isinstance(params, GithubReadParams):
                raise InvalidResourceParamsException(
                    "Parameters must be an instance of GithubReadParams."
                )
        elif resource.type == ResourceType.RELATIONAL_DB:
            if not isinstance(params, RelationalDBReadParams):
                raise InvalidResourceParamsException(
                    "Parameters must be an instance of RelationalDBReadParams."
                )
        else:
            raise InvalidConfigurationException(
                "Read Primitive expects a Notion, GoogleDocs, Github, or RelationalDB resource type."
            )
