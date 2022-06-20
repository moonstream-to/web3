"""Add raw_amount column

Revision ID: 815ae0983ef1
Revises: f0e8022dc814
Create Date: 2022-06-08 12:39:35.846110

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "815ae0983ef1"
down_revision = "f0e8022dc814"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "dropper_claimants", sa.Column("raw_amount", sa.String(), nullable=True)
    )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("dropper_claimants", "raw_amount")
    # ### end Alembic commands ###