"""document metadata

Revision ID: 281bc05cd12
Revises: 
Create Date: 2015-08-07 07:31:22.775957

"""

# revision identifiers, used by Alembic.
revision = '281bc05cd12'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('documents',
                    sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('metadata', postgresql.JSON()),
                    sa.Column('image_paths', postgresql.JSON()))


def downgrade():
    op.drop_table('documents')
