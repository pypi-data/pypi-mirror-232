import os
from typing import Dict, List, Optional, Any

from runllm import globals
from runllm.application import Application
from runllm.resources.resources import Resource
from runllm.task import Task

API_KEY_ENV_VAR = "RUNLLM_API_KEY"
RUNLLM_SERVER_ADDRESS = "https://api.llm.run"


class Client:
    """
    Client class for interacting with the RUNLLM server API.

    This class provides methods for managing resources and applications on the RUNLLM server.

    Args:
        api_key (str): The API key for authenticating with the RUNLLM server. If not provided,
            the client will attempt to read it from the 'RUNLLM_API_KEY' environment variable.
        runllm_address (str): The address of the RUNLLM server. Defaults to the value of
            'RUNLLM_SERVER_ADDRESS' constant.

    Attributes:
        connected_resources (Dict[str, Resource]): A dictionary containing connected resources,
            where keys are resource names and values are Resource objects.

    Raises:
        ValueError: If the API key is not provided and cannot be found in the environment
            variable 'RUNLLM_API_KEY'.

    """

    def __init__(self, api_key: str = "", runllm_address: str = RUNLLM_SERVER_ADDRESS):
        if api_key == "":
            if API_KEY_ENV_VAR in os.environ:
                print("Using RUNLLM_API_KEY from environment variable")
                api_key = os.environ[API_KEY_ENV_VAR]
            else:
                raise ValueError("Api key must be provided")

        globals.__GLOBAL_API_CLIENT__.configure(api_key, runllm_address)

        self.connected_resources: Dict[
            str, Resource
        ] = globals.__GLOBAL_API_CLIENT__.list_resources()

    def publish_application(self, name: str, tasks: List[Task], description: str = "") -> None:
        """
        Publishes an application to the RUNLLM server.

        Args:
            name (str): The name of the application.
            tasks (List[Task]): A list of Task objects defining the tasks within the application.
            description (str, optional): A description of the application (default is "").

        Returns:
            None

        """
        globals.__GLOBAL_API_CLIENT__.create_application(
            Application(
                name=name,
                description=description,
                tasks=tasks,
            )
        )
        return None

    def resource(self, name: str) -> Resource:
        """
        Retrieves a connected resource by name.

        Args:
            name (str): The name of the resource to retrieve.

        Returns:
            Resource: The Resource object representing the connected resource.

        Raises:
            ValueError: If the specified resource is not connected to the client.

        """
        if name in self.connected_resources:
            return self.connected_resources[name]
        else:
            self.connected_resources = globals.__GLOBAL_API_CLIENT__.list_resources()
            if name in self.connected_resources:
                return self.connected_resources[name]
            else:
                raise ValueError(f"Resource {name} is not connected")

    def delete_resource(self, name: str) -> None:
        """
        Deletes the provided resource only if it is not in use by an active application.

        Args:
            name (str): The name of the resource to delete.

        Raises:
            ValueError: If the specified resource is not connected.
        """
        if name in self.connected_resources:
            globals.__GLOBAL_API_CLIENT__.delete_resource(self.connected_resources[name].id)
        else:
            self.connected_resources = globals.__GLOBAL_API_CLIENT__.list_resources()
            if name in self.connected_resources:
                globals.__GLOBAL_API_CLIENT__.delete_resource(self.connected_resources[name].id)
            else:
                raise ValueError(f"Resource {name} is not connected")

    def list_applications(self) -> Any:
        """
        Returns a list containing the names of applications published.

        Returns:
            List[str]: List of names of published applications
            The list is empty if there are no published applications
        """
        return globals.__GLOBAL_API_CLIENT__.list_applications()

    def get_application(self, name: str) -> Optional[Application]:
        """
        Returns details of application by name

        Args:
            name (str): Name of the application

        Returns:
            A json representation of the application including the
            task names and primitive names associated with those tasks

        Raises:
            ValueError: If application name is empty or not specified.
        """
        if name is None or name.strip() == "":
            raise ValueError("Application name must be provided")

        return globals.__GLOBAL_API_CLIENT__.get_application(name)

    def delete_application(self, application_name: str) -> None:
        """
        Deletes application with provided name.

        Args:
            name (str): The name of the application to delete.
        """
        return globals.__GLOBAL_API_CLIENT__.delete_application(application_name)

    def get_task(self, application_name: str, task_name: str) -> Optional[Task]:
        """
        Returns the Task associated with the given application

        Args:
            application_name (str): Name of the application
            task_name (str): Name of the task

        Returns:
            Task: Task associated with the application with a given name.
            None if no such task exists or application name does not exist

        Raises:
            ValueError: If application name or task name is empty or not specified.
        """
        return globals.__GLOBAL_API_CLIENT__.get_task(application=application_name, task=task_name)
