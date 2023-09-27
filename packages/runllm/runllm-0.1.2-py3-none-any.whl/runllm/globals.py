from typing import Optional

from runllm.backend.api_client import APIClient
from runllm.task import Task

current_task: Optional[Task] = None

# Initialize an unconfigured api client. It will be configured when the user construct a runllm client.
__GLOBAL_API_CLIENT__ = APIClient()
