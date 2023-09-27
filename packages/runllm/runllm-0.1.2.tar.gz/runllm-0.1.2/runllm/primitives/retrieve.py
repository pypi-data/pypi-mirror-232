from typing import List, Optional, Tuple, Union

from runllm.constants.enums import ImplementationType, PrimitiveType, ResourceType
from runllm.context import ContextKey
from runllm.exceptions import (
    InvalidConfigurationException,
    InvalidResourceParamsException,
    UnknownImplementationTypeException,
)
from runllm.primitives.custom_primitive import CustomPrimitive
from runllm.primitives.primitive import Primitive, initialize_primitive_within_task
from runllm.primitives.spec import CustomSpec, DefaultRetrieveSpec, FunctionSpec
from runllm.resources.parameters import EmbedParams, VectorDBRetrieveParams
from runllm.resources.resources import Resource


class RetrievePrimitive(Primitive):
    inputs: List[Union[str, ContextKey]]
    implementation_spec: Union[DefaultRetrieveSpec, CustomSpec]

    def __init__(
        self,
        data: Union[CustomPrimitive, ContextKey],
        implementation_type: ImplementationType,
        llm_resource: Optional[Resource] = None,
        llm_params: Optional[EmbedParams] = None,
        vector_db_resource: Optional[Resource] = None,
        vector_db_params: Optional[VectorDBRetrieveParams] = None,
        function_spec: Optional[FunctionSpec] = None,
    ):
        dependenices, context_keys, inputs = self._process_inputs(data)

        spec = self._construct_primitive_spec(
            implementation_type,
            llm_resource,
            llm_params,
            vector_db_resource,
            vector_db_params,
            function_spec,
        )

        # Pydantic's BaseModel is aware of all fields in both RetrievePrimitive and Primitive.
        # It properly processes the attributes to the correct classes and performs type-checking.
        super().__init__(
            type=PrimitiveType.RETRIEVE,
            implementation_type=implementation_type,
            dependencies=dependenices,
            context_keys=context_keys,
            inputs=inputs,  # type: ignore
            implementation_spec=spec,
        )

        initialize_primitive_within_task(self)

    def _process_inputs(
        self, data: Union[CustomPrimitive, ContextKey]
    ) -> Tuple[List[str], List[ContextKey], List[Union[str, ContextKey]]]:
        """
        Verify and process the input data for the Retrieve instance.

        Parameters:
            data (Union[CustomPrimitive, ContextKey]): The input data to be verified and processed.

        Raises:
            InvalidInputException: If the input data is not of the expected type (CustomPrimitive or ContextKey).
        """
        from runllm.primitives.utils import process_primitive_inputs

        target_types = CustomPrimitive
        return process_primitive_inputs(data, target_types)

    def _construct_primitive_spec(
        self,
        implementation_type: ImplementationType,
        llm_resource: Optional[Resource],
        llm_params: Optional[EmbedParams],
        vector_db_resource: Optional[Resource],
        vector_db_params: Optional[VectorDBRetrieveParams],
        function_spec: Optional[FunctionSpec],
    ) -> Union[DefaultRetrieveSpec, CustomSpec]:
        if implementation_type == ImplementationType.DEFAULT:
            if not (llm_resource and llm_params and vector_db_resource and vector_db_params):
                raise Exception(
                    "Both resource and resource params need to be specified for the Default implementation"
                )
            self._verify_default_implementation(
                llm_resource,
                llm_params,
                vector_db_resource,
                vector_db_params,
            )
            return DefaultRetrieveSpec(
                llm_resource_id=llm_resource.id,
                llm_params=llm_params,
                vector_db_resource_id=vector_db_resource.id,
                vector_db_params=vector_db_params,
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

    def _verify_default_implementation(
        self,
        llm_resource: Resource,
        llm_params: EmbedParams,
        vector_db_resource: Resource,
        vector_db_params: VectorDBRetrieveParams,
    ) -> None:
        if llm_resource.type == ResourceType.LLM:
            if not isinstance(llm_params, EmbedParams):
                raise InvalidResourceParamsException(
                    "Parameters must be an instance of EmbedParams."
                )
        else:
            raise InvalidConfigurationException("Retrieve Primitive expects a LLM resource type.")

        if vector_db_resource.type == ResourceType.VECTOR_DB:
            # Confirm the parameters provided match the service type
            if not isinstance(vector_db_params, VectorDBRetrieveParams):
                raise InvalidResourceParamsException(
                    "Parameters must be an instance of VectorDBRetrieveParams."
                )
        else:
            raise InvalidConfigurationException(
                "Retrieve Primitive expects a VectorDB resource type."
            )
