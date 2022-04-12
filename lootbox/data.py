from typing import Any, List

from pydantic import BaseModel, Field


class PingResponse(BaseModel):
    """
    Schema for ping response
    """

    status: str


class SleepResponse(BaseModel):
    instances: List[str] = Field(default_factory=list)


class WakeupResponse(BaseModel):
    instances: List[str] = Field(default_factory=list)


class DropRegisterRequest(BaseModel):
    drop_name: str
    dropper_address: str
    claim_id: str
    addresses: List[str]


class DropResponse(BaseModel):
    signed_transaction: str


class DropListResponse(BaseModel):
    drops: List[Any] = Field(default_factory=list)

