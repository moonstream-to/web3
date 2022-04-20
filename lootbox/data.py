from typing import Any, List, Optional

from pydantic import BaseModel, Field
from uuid import UUID


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

    dropper_contract_address: str
    blockchain: str
    title: str
    description: str
    claim_block_deadline: Optional[int] = None
    terminus_address: Optional[str] = None
    terminus_pool_id: Optional[int] = None
    claim_id: Optional[int] = None


class Claimant(BaseModel):
    address: str
    amount: int


class DropAddClaimantsRequest(BaseModel):
    dropper_claim_id: UUID
    claimants: List[Claimant]


class DropRemoveClaimantsRequest(BaseModel):
    dropper_claim_id: UUID
    addresses: List[str]


class DropResponse(BaseModel):
    claimant: str
    claim_id: int
    block_deadline: int
    signature: str


class DropListResponse(BaseModel):
    drops: List[Any] = Field(default_factory=list)
