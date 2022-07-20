"""
Lootbox API.
"""
from atexit import register
import logging
from uuid import UUID

from web3 import Web3


from fastapi import  FastAPI, Request, Depends
from sqlalchemy.orm import Session

from .. import actions
from .. import data
from .. import db
from ..settings import DOCS_TARGET_PATH_OPENAPI, DOCS_TARGET_PATH

logger = logging.getLogger(__name__)


tags_metadata = [{"name": "leaderboard", "description": "Moonstream Engine leaderboard API"}]


app = FastAPI(
    title=f"Moonstream Engine leaderboard API",
    description="Moonstream Engine leaderboard API endpoints.",
    version="v0.0.1",
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url=None,
    redoc_url=f"/{DOCS_TARGET_PATH_OPENAPI['leaderboard']}",
)


@app.get("/count/addresses")
async def count_addresses(
    request: Request,
    leaderboard_id: UUID,
    db_session: Session = Depends(db.yield_db_session),
):

    """
    Returns the number of addresses in the leaderboard.
    """

    count = actions.get_leaderboard_total_count(db_session, leaderboard_id)

    return data.CountAddressesResponse(count=count)


@app.get("/quartiles")
async def quartiles(
    request: Request,
    leaderboard_id: UUID,
    db_session: Session = Depends(db.yield_db_session),
):

    """

    Returns the quartiles of the leaderboard.

    """

    q1, q2, q3 = actions.get_qurtiles(db_session, leaderboard_id)

    return data.QuartilesResponse(
        percentile_25={"address": q1[0], "score": q1[1], "rank": q1[2]},
        percentile_50={"address": q2[0], "score": q2[1], "rank": q2[2]},
        percentile_75={"address": q3[0], "score": q3[1], "rank": q3[2]},
    )


@app.get("/position")
async def position(
    request: Request,
    leaderboard_id: UUID,
    address: str,
    window_size: int = 1,
    limit: int = 10,
    offset: int = 0,
    db_session: Session = Depends(db.yield_db_session),
):

    """
    Returns the leaderboard posotion for the given address.
    With given window size.
    """

    address = Web3.toChecksumAddress(address)

    positions = actions.get_position(
        db_session, leaderboard_id, address, window_size, limit, offset
    )

    return positions


@app.get("/")
async def leaderboard(
    request: Request,
    leaderboard_id: UUID,
    limit: int = 10,
    offset: int = 0,
    db_session: Session = Depends(db.yield_db_session),
):

    """
    Returns the leaderboard.
    """

    leaderboard = actions.get_leaderboard_positions(
        db_session, leaderboard_id, limit, offset
    )

    return leaderboard
