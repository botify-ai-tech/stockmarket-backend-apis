"""v14_update__news_table

Revision ID: b51861b17770
Revises: 85112910f172
Create Date: 2024-10-22 11:56:58.223785

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b51861b17770'
down_revision: Union[str, None] = '85112910f172'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('news_items', sa.Column('image', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('news_items', 'image')
    # ### end Alembic commands ###