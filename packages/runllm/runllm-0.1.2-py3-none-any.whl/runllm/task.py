import inspect
import textwrap
from typing import Any, Dict, List, Optional, Callable

from pydantic import BaseModel

from runllm import globals
from runllm.constants.enums import Mode
from runllm.context import Context
from runllm.primitives.primitive import Primitive
from runllm.utils.utils import format_header_for_print


class Task(BaseModel):
    name: str
    mode: Mode
    primitives: Dict[str, Primitive] = {}
    cron_schedule: Optional[str]
    paused: Optional[bool]
    primitive_outputs: Optional[List[str]] = None
    id: Optional[int] = None
    application_id: Optional[int] = None

    def add_primitive(self, primitive: Primitive) -> None:
        self.primitives[primitive.id] = primitive

    def __call__(self, context: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        if self.mode == Mode.BATCH:
            assert context is None, "Batch task must not have a context"
        elif self.mode == Mode.REAL_TIME:
            assert context is not None, "Real-time task must have a context"
            assert isinstance(context, Dict), "Context must be a dictionary"

            # Extracting all keys required by primitives
            required_keys = set()
            for _, primitive in self.primitives.items():
                required_keys.update([context_key.key for context_key in primitive.context_keys])

            # Checking if all required keys are present in context
            if not all(key in context for key in required_keys):
                missing_keys = [key for key in required_keys if key not in context]
                raise ValueError(f"Context is missing the following required keys: {missing_keys}")

        if self.application_id is not None and self.id is not None:
            # Task is already published, so we invoke the trigger endpoint
            return globals.__GLOBAL_API_CLIENT__.trigger_task(
                application_id=self.application_id,
                task_id=self.id,
                context=context,
            )

        # Task is not published, so we invoke the test endpoint
        assert self.application_id is None and self.id is None, "Task must not be published"
        print("Warning: Testing a task can take a few minutes due to infrastructure setup.")
        print(
            "Any primitive that is a write or downstream of a write will be skipped during testing to avoid side-effects."
        )

        response = globals.__GLOBAL_API_CLIENT__.test_task(
            test_task_request_body=TestTask(
                name=self.name,
                mode=self.mode,
                primitives=self.primitives,
                primitive_outputs=self.primitive_outputs,
                context=context,
            ).json()
        )

        print(f"Successfully tested task {self.name}!")
        if self.mode == Mode.REAL_TIME:
            return response

        return None

    def describe(self) -> None:
        """Prints out a human-readable description of the task."""

        task_description = textwrap.dedent(
            f"""
            {format_header_for_print(f"'{self.name}' Task")}
            Mode: '{self.mode}'
            Schedule: {self.cron_schedule}
            """
        )
        print(task_description)

        # Iterate through primitives and add their descriptions to the main description
        for _, primitive_obj in self.primitives.items():
            primitive_obj.describe()


class TestTask(BaseModel):
    """
    Defines the simplified Task structure expected by the backend when testing
    a task.
    """

    name: str
    mode: Mode
    primitives: Dict[str, Primitive] = {}
    primitive_outputs: Optional[List[str]] = None
    context: Optional[Dict[str, Any]]

    def describe(self) -> None:
        """Prints out a human-readable description of the task."""

        task_description = textwrap.dedent(
            f"""
            {format_header_for_print(f"'{self.name}' Task")}
            Mode: '{self.mode}'
            """
        )
        print(task_description)

        # Iterate through primitives and add their descriptions to the main description
        for _, primitive_obj in self.primitives.items():
            primitive_obj.describe()


def task(name: str, mode_str: str, schedule: Optional[str] = None) -> Callable[[Callable[..., Any]], Task]:
    mode = Mode(mode_str)
    if mode not in Mode:  # Check if the mode is valid
        raise ValueError(f"Invalid mode: {mode}")

    paused = False
    if not schedule:
        # Dummy schedule is ignored by the backend since we set paused=True.
        schedule = "1 1 1 1 1"
        paused = True

    def decorator(func: Callable[..., Any]) -> Task:
        sig = inspect.signature(func)
        if mode == Mode.REAL_TIME:
            if len(sig.parameters) != 1 or "context" not in sig.parameters:
                raise TypeError("Real-time task function must accept a single argument 'context'")
        elif mode == Mode.BATCH:
            if len(sig.parameters) != 0:
                raise TypeError("Batch task function must accept no arguments")

        try:
            globals.current_task = Task(name=name, mode=mode, cron_schedule=schedule, paused=paused)
            if mode == Mode.REAL_TIME:
                context = Context()
                result = func(context)
                assert isinstance(result, Primitive), "Real-time task must return a Primitive"
                globals.current_task.primitive_outputs = [result.id]
            else:
                result = func()
                assert result is None, "Batch task must not return anything"
            task_instance = globals.current_task
        finally:
            # Always set current_task to None, even if an exception was thrown
            globals.current_task = None
        return task_instance

    return decorator
