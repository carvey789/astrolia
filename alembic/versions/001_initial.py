"""Initial schema with all models

Revision ID: 001_initial
Revises:
Create Date: 2025-12-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums using raw SQL with exception handling for duplicates
    op.execute("DO $$ BEGIN CREATE TYPE authprovider AS ENUM ('email', 'google'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE manifestationstatus AS ENUM ('pending', 'in_progress', 'manifested', 'released'); EXCEPTION WHEN duplicate_object THEN null; END $$;")

    # Add birth_latitude and birth_longitude columns if they don't exist
    op.execute("""
        DO $$
        BEGIN
            ALTER TABLE users ADD COLUMN IF NOT EXISTS birth_latitude FLOAT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS birth_longitude FLOAT;
        END $$;
    """)


def downgrade() -> None:
    op.execute('ALTER TABLE users DROP COLUMN IF EXISTS birth_latitude')
    op.execute('ALTER TABLE users DROP COLUMN IF EXISTS birth_longitude')
