from typing import List

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
    dropper_address: str
    claim_id: str
    addresses: List[str]
