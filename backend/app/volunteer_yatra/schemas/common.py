from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class StatusHistoryEntry(BaseModel):
    status: str
    at: str
    by_user_id: str | None = None
    note: str | None = None
