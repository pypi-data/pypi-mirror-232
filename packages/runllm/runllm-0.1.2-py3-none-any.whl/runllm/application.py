import textwrap
from typing import List

from pydantic import BaseModel

from runllm.task import Task
from runllm.utils.utils import format_header_for_print


class Application(BaseModel):
    name: str
    description: str
    tasks: List[Task]

    def describe(self) -> None:
        """Prints out a human-readable description of the application."""
        app_description = textwrap.dedent(
            f"""
            {format_header_for_print(f"'{self.name}' Application")}
            Description: {self.description}
            """
        )
        print(app_description)
        # Iterate through tasks and add their descriptions to the main description
        for task in self.tasks:
            task.describe()
