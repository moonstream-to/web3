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


class DropperContractResponse(BaseModel):
    id: UUID
    address: str
    blockchain: str
    title: Optional[str]
    description: Optional[str]
    image_uri: Optional[str]


class DropperTerminusResponse(BaseModel):
    terminus_address: str
    terminus_pool_id: int
    blockchain: str

class DropperBlockchainResponse(BaseModel):
    blockchain: str

class DropRegisterRequest(BaseModel):

    dropper_contract_id: UUID
    title: str
    description: str
    claim_block_deadline: Optional[int] = None
    terminus_address: Optional[str] = None
    terminus_pool_id: Optional[int] = None
    claim_id: Optional[int] = None


class DropCreatedResponse(BaseModel):
    dropper_claim_id: UUID
    dropper_contract_id: UUID
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
    claimants: List[Claimant] = Field(default_factory=list)


class ClaimantsResponse(BaseModel):
    claimants: List[Claimant] = Field(default_factory=list)


class DropRemoveClaimantsRequest(BaseModel):
    dropper_claim_id: UUID
    addresses: List[str] = Field(default_factory=list)


class RemoveClaimantsResponse(BaseModel):
    addresses: List[str] = Field(default_factory=list)


class DropResponse(BaseModel):
    claimant: str
    claim_id: int
    amount: int
    block_deadline: int
    signature: str


class DropListResponse(BaseModel):
    drops: List[Any] = Field(default_factory=list)
