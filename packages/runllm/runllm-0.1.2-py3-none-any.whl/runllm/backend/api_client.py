import json
from typing import Any, Dict, Optional, List

import requests

from runllm.application import Application
from runllm.constants.types import service_to_resource_type
from runllm.resources.resources import Resource
from runllm.task import Task


class APIClient:
    """
    Internal client class used to send requests to the runllm backend.
    """

    HTTP_PREFIX = "http://"
    HTTPS_PREFIX = "https://"

    # Routes
    LIST_RESOURCES_ROUTE = "/api/resources"
    RESOURCE_ROUTE = "/api/resource"
    LIST_APPLICATIONS_NAMES_ROUTE = "/api/applications/names"
    TEST_TASK_ROUTE = "/api/task"
    TRIGGER_TASK_ROUTE_TEMPLATE = "/api/application/%s/task/%s"

    GET_APPLICATION_ROUTE = "/api/applications/appname"
    APPLICATION_ROUTE = "/api/application"

    # Auth header
    API_KEY_HEADER = "x-api-key"

    configured = False

    def raise_errors(self, response: requests.Response) -> None:
        def _extract_err_msg() -> str:
            resp_json = response.json()
            if "message" not in resp_json:
                raise Exception("No 'message' field on response: %s" % json.dumps(resp_json))
            return str(resp_json["message"])

        if response.status_code != 200:
            raise Exception(_extract_err_msg())

    def configure(self, api_key: str, runllm_address: str) -> None:
        self.api_key = api_key
        self.runllm_address = runllm_address

        # Clean URL
        if self.runllm_address.endswith("/"):
            self.runllm_address = self.runllm_address[:-1]

        self.configured = True

        if self.runllm_address.startswith(self.HTTP_PREFIX):
            self.runllm_address = self.runllm_address[len(self.HTTP_PREFIX) :]
            self.use_https = False
        elif self.runllm_address.startswith(self.HTTPS_PREFIX):
            self.runllm_address = self.runllm_address[len(self.HTTPS_PREFIX) :]
            self.use_https = True
        else:
            # If no http(s) prefix is provided, we prompt the user to provide a prefix
            # and default to using http.
            print(
                """Warning: No `http` or `https` prefix has been provided for the RunLLM server address.
We default to using `http://`. Please confirm that this is the correct address."""
            )
            self.use_https = False

    def _check_config(self) -> None:
        if not self.configured:
            raise Exception(
                "API client has not been configured, please complete the configuration "
                "by initializing a runllm client via: "
                "`client = runllm.Client(api_key, runllm_address)`"
            )

    def _generate_auth_headers(self) -> Dict[str, str]:
        self._check_config()
        return {self.API_KEY_HEADER: self.api_key}

    def construct_base_url(self, use_https: Optional[bool] = None) -> str:
        self._check_config()
        if use_https is None:
            use_https = self.use_https
        protocol_prefix = self.HTTPS_PREFIX if use_https else self.HTTP_PREFIX
        return "%s%s" % (protocol_prefix, self.runllm_address)

    def construct_full_url(self, route_suffix: str, use_https: Optional[bool] = None) -> str:
        self._check_config()
        if use_https is None:
            use_https = self.use_https
        return "%s%s" % (self.construct_base_url(use_https), route_suffix)

    def list_resources(self) -> Dict[str, Resource]:
        url = self.construct_full_url(self.LIST_RESOURCES_ROUTE)
        headers = self._generate_auth_headers()
        resp = requests.get(url, headers=headers)
        self.raise_errors(resp)

        return {
            resource_info["name"]: Resource(
                id=resource_info["id"],
                name=resource_info["name"],
                service=resource_info["service"],
                type=service_to_resource_type[resource_info["service"]],
            )
            for resource_info in resp.json()["resources"]
        }

    def delete_resource(self, resource_id: int) -> None:
        url = self.construct_full_url(self.RESOURCE_ROUTE)
        headers = self._generate_auth_headers()
        headers["Content-Type"] = "application/json"
        body = {
            "resource_id": resource_id,
        }
        resp = requests.delete(url, headers=headers, json=body)
        self.raise_errors(resp)

    def list_applications(self) -> Any:
        url = self.construct_full_url(self.LIST_APPLICATIONS_NAMES_ROUTE)
        headers = self._generate_auth_headers()
        resp = requests.get(url, headers=headers)
        self.raise_errors(resp)

        return resp.json()["applications"]

    def get_application(self, name: str) -> Optional[Application]:
        url = self.construct_full_url(self.GET_APPLICATION_ROUTE)
        headers = self._generate_auth_headers()
        body = {
            "application_name": name,
        }
        resp = requests.get(url, headers=headers, json=body)
        self.raise_errors(resp)

        app = resp.json()["application"]
        tasks = app["tasks"]

        client_task_list = []
        for task in tasks:
            client_task_list.append(Task(**task))

        application = Application(
            name=app["name"],
            description=app["description"],
            tasks=client_task_list,
        )

        return application

    def create_application(self, application_request: Application) -> None:
        url = self.construct_full_url(self.APPLICATION_ROUTE)
        headers = self._generate_auth_headers()
        headers["Content-Type"] = "application/json"
        headers["type"] = "general"
        body = {
            "application": application_request.json(),
        }
        resp = requests.post(url, headers=headers, json=body)
        self.raise_errors(resp)

    def test_task(self, test_task_request_body: str) -> Any:
        url = self.construct_full_url(self.TEST_TASK_ROUTE)
        headers = self._generate_auth_headers()
        headers["Content-Type"] = "application/json"
        headers["type"] = "general"
        body = {
            "task": test_task_request_body,
        }
        resp = requests.post(url, headers=headers, json=body)
        self.raise_errors(resp)

        return resp.json()["response"]

    def trigger_task(
        self, application_id: int, task_id: int, context: Optional[Dict[str, Any]] = None
    ) -> Any:
        if context is None:
            context = {}

        url = self.construct_full_url(self.TRIGGER_TASK_ROUTE_TEMPLATE % (application_id, task_id))
        headers = self._generate_auth_headers()
        headers["Content-Type"] = "application/json"
        body = context
        resp = requests.post(url, headers=headers, json=body)
        self.raise_errors(resp)

        return resp.json()["response"]

    def delete_application(self, application_name: str) -> None:
        url = self.construct_full_url(self.APPLICATION_ROUTE)
        headers = self._generate_auth_headers()
        headers["Content-Type"] = "application/json"
        body = {
            "application_name": application_name,
        }
        resp = requests.delete(url, headers=headers, json=body)
        self.raise_errors(resp)

    def get_task(self, application: str, task: str) -> Optional[Task]:
        app = self.get_application(name=application)
        if app is not None:
            for app_task in app.tasks:
                if app_task.name == task:
                    return app_task
            raise Exception(
                f"Task `{task}` is not part of application `{app.name}`. "
                "You can check the tasks in this application by running `application.describe()`."
            )
        return None
