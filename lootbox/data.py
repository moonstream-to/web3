from typing import Any, List, Optional

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

    dropper_contract_id: str
    blockchain: str
    title: str
    description: str
    claim_block_deadline: int
    terminus_address: str
    terminus_pool_id: int
    claim_id: Optional[int] = None


class DropResponse(BaseModel):
    claimant: str
    claim_id: int
    block_deadline: int
    signature: str


class DropListResponse(BaseModel):
    drops: List[Any] = Field(default_factory=list)
