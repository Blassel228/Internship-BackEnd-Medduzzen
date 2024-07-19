"""empty message

Revision ID: c8bc5585225e
Revises: 7e115f504d5f
Create Date: 2024-07-19 20:54:56.042466

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c8bc5585225e"
down_revision: Union[str, None] = "7e115f504d5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "company",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("visible", sa.Boolean(), nullable=True),
        sa.Column("registration_date", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["user.id"], onupdate="CASCADE", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("company")
    # ### end Alembic commands ###
