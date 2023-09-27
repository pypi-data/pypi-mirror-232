import textwrap
import uuid
from typing import List

from pydantic import BaseModel, Field

from runllm.constants.enums import ImplementationType, PrimitiveType
from runllm.context import ContextKey
from runllm.utils.utils import format_header_for_print


class Primitive(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: PrimitiveType
    implementation_type: ImplementationType
    dependencies: List[str]
    context_keys: List[ContextKey]

    def describe(self) -> None:
        """Prints out a human-readable description of the primitive."""

        print(
            textwrap.dedent(
                f"""
            {format_header_for_print(f"'{self.type}' Primitive")}
            ID: '{self.id}'
            Implementation Type: '{self.implementation_type}'
            Dependencies: {self.dependencies}
            Context Keys: {self.context_keys}
            """
            )
        )


def initialize_primitive_within_task(primitive: Primitive) -> None:
    """
    Initialize a primitive instance within the current task.

    This function assumes that globals.current_task is set and is an instance of Task.

    Parameters:
        primitive (Primitive): The instance of the Primitive class to be initialized within the task.

    Raises:
        AssertionError: If globals.current_task is not set or is not an instance of Task.
    """
    from runllm import globals
    from runllm.task import Task

    assert globals.current_task is not None, "No current task"
    assert isinstance(globals.current_task, Task), "Current task is not a Task"
    globals.current_task.add_primitive(primitive)
