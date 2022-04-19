from turtle import update
import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Boolean,
    Integer,
    ForeignKey,
    MetaData,
    Numeric,
    Text,
    VARCHAR,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles

"""
Naming conventions doc
https://docs.sqlalchemy.org/en/13/core/constraints.html#configuring-constraint-naming-conventions
"""
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention, schema="lootbox")
Base = declarative_base(metadata=metadata)

"""
Creating a utcnow function which runs on the Posgres database server when created_at and updated_at
fields are populated.
Following:
1. https://docs.sqlalchemy.org/en/13/core/compiler.html#utc-timestamp-function
2. https://www.postgresql.org/docs/current/functions-datetime.html#FUNCTIONS-DATETIME-CURRENT
3. https://stackoverflow.com/a/33532154/13659585
"""


class utcnow(expression.FunctionElement):
    type = DateTime


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kwargs):
    return "TIMEZONE('utc', statement_timestamp())"


class Drop(Base):  # type: ignore
    __tablename__ = "drops"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    dropper_address = Column(VARCHAR(length=255), nullable=False)
    claim_id = Column(BigInteger, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False)
    claimant_address = Column(VARCHAR(length=255), nullable=False)
    amount = Column(BigInteger, nullable=False)
    is_claimed = Column(Boolean, nullable=False) 
    recheck = Column(Boolean, nullable=False) # We can add ability to frontend request a re-check of the claim.
    updated_at = Column(
        DateTime(timezone=True), server_default=utcnow(), nullable=False
    )
    created_at = Column(
        DateTime(timezone=True), server_default=utcnow(), nullable=False
    )
