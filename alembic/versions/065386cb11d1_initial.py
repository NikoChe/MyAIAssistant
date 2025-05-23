"""initial

Revision ID: 065386cb11d1
Revises: 
Create Date: 2025-04-23 01:20:57.591827

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '065386cb11d1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('clients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('source', sa.String(length=64), nullable=True),
    sa.Column('initial_request', sa.Text(), nullable=True),
    sa.Column('telegram_id', sa.BigInteger(), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('telegram_id')
    )
    op.create_table('question_versions',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('version_name', sa.String(length=64), nullable=True),
    sa.Column('uploaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('owner_id', sa.BigInteger(), nullable=True),
    sa.Column('label', sa.String(length=128), nullable=True),
    sa.Column('public_access', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('version_id', sa.String(length=32), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('type', sa.String(length=32), nullable=True),
    sa.Column('required', sa.Boolean(), nullable=True),
    sa.Column('options', sa.JSON(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['questions.id'], ),
    sa.ForeignKeyConstraint(['version_id'], ['question_versions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.Integer(), nullable=True),
    sa.Column('session_type', sa.String(length=32), nullable=True),
    sa.Column('answers_json', sa.JSON(), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=True),
    sa.Column('scheduled_at', sa.DateTime(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sessions')
    op.drop_table('questions')
    op.drop_table('question_versions')
    op.drop_table('clients')
    # ### end Alembic commands ###
