"""remove user tokens

Revision ID: 0dfd5bb59cb7
Revises: 749bb4c79f6b
Create Date: 2021-01-11 04:26:24.671863

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0dfd5bb59cb7'
down_revision = '749bb4c79f6b'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index(op.f('ix_user_token'), table_name='user')
    op.drop_column('user', 'token_expiration')
    op.drop_column('user', 'token')


def downgrade():
    op.add_column('user', sa.Column('token', sa.String(length=32), nullable=True))
    op.add_column('user', sa.Column('token_expiration', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_user_token'), 'user', ['token'], unique=True)