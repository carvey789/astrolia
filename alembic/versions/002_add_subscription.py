"""Add subscription fields

Revision ID: 002_add_subscription
Revises: 001_initial
Create Date: 2025-12-30
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '002_add_subscription'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    # Create subscription_tier enum
    subscription_tier = sa.Enum('free', 'premium', name='subscriptiontier')
    subscription_tier.create(op.get_bind(), checkfirst=True)

    # Add subscription columns
    op.add_column('users', sa.Column(
        'subscription_tier',
        sa.Enum('free', 'premium', name='subscriptiontier'),
        nullable=False,
        server_default='free'
    ))
    op.add_column('users', sa.Column(
        'subscription_expires_at',
        sa.DateTime(),
        nullable=True
    ))
    op.add_column('users', sa.Column(
        'subscription_platform',
        sa.String(20),
        nullable=True
    ))
    op.add_column('users', sa.Column(
        'subscription_product_id',
        sa.String(100),
        nullable=True
    ))
    op.add_column('users', sa.Column(
        'revenuecat_id',
        sa.String(100),
        nullable=True
    ))


def downgrade():
    op.drop_column('users', 'revenuecat_id')
    op.drop_column('users', 'subscription_product_id')
    op.drop_column('users', 'subscription_platform')
    op.drop_column('users', 'subscription_expires_at')
    op.drop_column('users', 'subscription_tier')

    # Drop enum
    subscription_tier = sa.Enum('free', 'premium', name='subscriptiontier')
    subscription_tier.drop(op.get_bind(), checkfirst=True)
