"""empty message

Revision ID: 4ee15791d048
Revises: 940b3ef1cccb
Create Date: 2024-07-28 07:16:38.102980

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bdec4ba673a9"
down_revision: Union[str, None] = "4ee15791d048"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    pass


def downgrade():
    pass
