"""
Game Master bots for the Garden of Forking Paths on-chain game mechanic.
"""

from dataclasses import asdict, dataclass, Field
from enum import Enum
from typing import Any, Optional

from .. import GOFPFacet

from moonworm.watch import watch_contract


GOFP_ABI = GOFPFacet.get_abi_json("GOFPFacet")

GOFP_EVENTS_ABI = [item for item in GOFP_ABI if item["type"] == "event"]


class GOFPEvents(Enum):
    PathChosen = "PathChosen"
    PathRegistered = "PathRegistered"
    SessionActivated = "SessionActivated"
    SessionChoosingActivated = "SessionChoosingActivated"
    SessionCreated = "SessionCreated"
    SessionUriChanged = "SessionUriChanged"


@dataclass
class GOFPGameMasterState:
    gofp_address: str
    deployment_block: str
    session_id: int
    session_start_block: int

    current_stage: Optional[int] = None
    current_stage_start_block: Optional[int] = None
    current_stage_is_active: Optional[bool] = None

    correct_paths: list[int] = Field(default_factory=list)


class GOFPGameMaster:
    def __init__(self, state: GOFPGameMasterState) -> None:
        pass
