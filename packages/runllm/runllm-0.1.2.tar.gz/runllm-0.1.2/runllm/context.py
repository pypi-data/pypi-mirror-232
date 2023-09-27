from pydantic import BaseModel


class ContextKey(BaseModel):
    key: str


class Context:
    def __getitem__(self, key: str) -> ContextKey:
        return ContextKey(key=key)
