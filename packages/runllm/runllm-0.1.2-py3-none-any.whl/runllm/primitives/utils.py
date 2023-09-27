from typing import List, Tuple, Type, Union

from runllm.context import ContextKey
from runllm.exceptions import InvalidInputException
from runllm.primitives.primitive import Primitive


def process_primitive_inputs(
    data: Union[Primitive, ContextKey],
    target_types: Union[Type[Primitive], Tuple[Type[Primitive], ...]],
) -> Tuple[List[str], List[ContextKey], List[Union[str, ContextKey]]]:
    """
    Process input data to extract dependencies, context keys, and inputs for further operations.

    This function takes input data and a list of target primitive types. It categorizes the input data into dependencies,
    context keys, and inputs based on their types.

    Args:
        data (Union[Primitive, ContextKey]): The input data to be processed. Can be an instance of Primitive or ContextKey.
        target_types (Union[Type[Primitive], Tuple[Type[Primitive], ...]]): The target primitive types to consider when categorizing data.

    Returns:
        Tuple[List[str], List[ContextKey], List[Union[str, ContextKey]]]: A tuple containing three lists:
            - List of str(UUIDs) representing dependencies.
            - List of ContextKey instances.
            - List of str(UUIDs) and ContextKey instances combined, representing inputs.

    Raises:
        InvalidInputException: If the input data is not of the expected target types or ContextKey.
    """
    dependencies = []
    context_keys = []
    inputs: List[Union[str, ContextKey]] = []

    if isinstance(data, target_types):
        assert isinstance(data, Primitive)
        dependencies.append(data.id)
        inputs.append(data.id)
    elif isinstance(data, ContextKey):
        context_keys.append(data)
        inputs.append(data)
    else:
        raise InvalidInputException(
            f"Input data is of the wrong type. Expected {target_types} or ContextKey."
        )

    return dependencies, context_keys, inputs
