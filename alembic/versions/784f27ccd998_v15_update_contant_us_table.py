"""v15_update_contant_us_table

Revision ID: 784f27ccd998
Revises: b51861b17770
Create Date: 2024-10-23 15:19:12.276113

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '784f27ccd998'
down_revision: Union[str, None] = 'b51861b17770'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contacts', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('contacts', sa.Column('last_name', sa.String(), nullable=True))
    op.drop_index('ix_contacts_user_id', table_name='contacts')
    op.drop_constraint('contacts_user_id_fkey', 'contacts', type_='foreignkey')
    op.drop_column('contacts', 'user_id')
    op.drop_column('contacts', 'name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('contacts', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('contacts', sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_foreign_key('contacts_user_id_fkey', 'contacts', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_contacts_user_id', 'contacts', ['user_id'], unique=False)
    op.drop_column('contacts', 'last_name')
    op.drop_column('contacts', 'first_name')
    # ### end Alembic commands ###
