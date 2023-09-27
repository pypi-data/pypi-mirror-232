from pydantic import BaseModel

from runllm.constants.enums import ResourceType, Service


class Resource(BaseModel):
    id: int
    name: str
    service: Service
    type: ResourceType
