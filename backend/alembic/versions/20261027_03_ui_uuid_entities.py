"""create uuid ui entities

Revision ID: 20261027_03
Revises: 20261027_02
Create Date: 2026-10-27 00:25:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = '20261027_03'
down_revision: str | None = '20261027_02'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'ui_users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', sa.String(length=100), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ui_users_client_id', 'ui_users', ['client_id'])
    op.create_index('ix_ui_users_username', 'ui_users', ['username'])

    op.create_table(
        'ui_products',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=120), nullable=True),
        sa.Column('cost', sa.Numeric(12, 2), nullable=False),
        sa.Column('price', sa.Numeric(12, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ui_products_client_id', 'ui_products', ['client_id'])

    op.create_table(
        'ui_sales',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', sa.String(length=100), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('selling_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('sale_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['ui_products.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ui_sales_client_id', 'ui_sales', ['client_id'])
    op.create_index('ix_ui_sales_product_id', 'ui_sales', ['product_id'])


def downgrade() -> None:
    op.drop_index('ix_ui_sales_product_id', table_name='ui_sales')
    op.drop_index('ix_ui_sales_client_id', table_name='ui_sales')
    op.drop_table('ui_sales')
    op.drop_index('ix_ui_products_client_id', table_name='ui_products')
    op.drop_table('ui_products')
    op.drop_index('ix_ui_users_username', table_name='ui_users')
    op.drop_index('ix_ui_users_client_id', table_name='ui_users')
    op.drop_table('ui_users')
