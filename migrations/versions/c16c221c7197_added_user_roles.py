"""Added user roles

Revision ID: c16c221c7197
Revises: 25264fcb7944
Create Date: 2020-03-16 23:00:35.850094

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'c16c221c7197'
down_revision = '25264fcb7944'
branch_labels = None
depends_on = None


def upgrade():
    userroles = postgresql.ENUM('USER', 'EXPERT', 'ADMIN', name='userroles')
    userroles.create(op.get_bind())

    op.add_column('user', sa.Column('user_role', sa.Enum('USER', 'EXPERT', 'ADMIN', name='userroles'), nullable=False))


def downgrade():
    op.drop_column('user', 'user_role')

    userroles = postgresql.ENUM('USER', 'EXPERT', 'ADMIN', name='userroles')
    userroles.drop(op.get_bind())
