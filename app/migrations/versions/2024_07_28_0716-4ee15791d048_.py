"""empty message

Revision ID: 4ee15791d048
Revises: 940b3ef1cccb
Create Date: 2024-07-28 07:16:38.102980

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4ee15791d048"
down_revision: Union[str, None] = "940b3ef1cccb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add the USING clause to properly cast the column type
    op.alter_column(
        "user",
        "registration_date",
        type_=sa.TIMESTAMP(timezone=False),
        postgresql_using="registration_date::timestamp without time zone",
    )

    op.alter_column(
        "company",
        "registration_date",
        type_=sa.TIMESTAMP(timezone=False),
        postgresql_using="registration_date::timestamp without time zone",
    )

    op.alter_column(
        "invitation",
        "registration_date",
        type_=sa.TIMESTAMP(timezone=False),
        postgresql_using="registration_date::timestamp without time zone",
    )

    op.alter_column(
        "member",
        "registration_date",
        type_=sa.TIMESTAMP(timezone=False),
        postgresql_using="registration_date::timestamp without time zone",
    )

    op.alter_column(
        "request",
        "registration_date",
        type_=sa.TIMESTAMP(timezone=False),
        postgresql_using="registration_date::timestamp without time zone",
    )

    op.alter_column(
        "quiz",
        "registration_date",
        type_=sa.TIMESTAMP(timezone=False),
        postgresql_using="registration_date::timestamp without time zone",
    )

    op.alter_column(
        "quiz_result",
        "registration_date",
        type_=sa.TIMESTAMP(timezone=False),
        postgresql_using="registration_date::timestamp without time zone",
    )


def downgrade():
    # Revert the changes in downgrade
    op.alter_column("user", "registration_date", type_=sa.DateTime())

    op.alter_column("company", "registration_date", type_=sa.DateTime())

    op.alter_column("invitation", "registration_date", type_=sa.DateTime())

    op.alter_column("member", "registration_date", type_=sa.DateTime())

    op.alter_column("request", "registration_date", type_=sa.DateTime())

    op.alter_column("quiz", "registration_date", type_=sa.DateTime())

    op.alter_column("quiz_result", "registration_date", type_=sa.DateTime())
