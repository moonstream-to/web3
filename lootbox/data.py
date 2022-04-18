from typing import Any, List

from pydantic import BaseModel, Field


class PingResponse(BaseModel):
    """
    Schema for ping response
    """

    status: str


class SignerListResponse(BaseModel):
    instances: List[Any] = Field(default_factory=list)


class SignerSleepResponse(BaseModel):
    instances: List[str] = Field(default_factory=list)


class SignerWakeupResponse(BaseModel):
    instances: List[str] = Field(default_factory=list)


class DropRegisterRequest(BaseModel):
    name: str
    claim_id: str
    addresses: List[str]


class DropResponse(BaseModel):
    claimant: str
    claim_id: int
    block_deadline: int
    signature: str


class DropListResponse(BaseModel):
    drops: List[Any] = Field(default_factory=list)
