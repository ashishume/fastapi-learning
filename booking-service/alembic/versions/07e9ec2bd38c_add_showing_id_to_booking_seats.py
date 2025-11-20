"""add_showing_id_to_booking_seats

Revision ID: 07e9ec2bd38c
Revises: 3094ab09a708
Create Date: 2025-11-21 02:41:02.898778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07e9ec2bd38c'
down_revision: Union[str, None] = '3094ab09a708'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add showing_id column to booking_seats table (nullable initially)
    op.add_column('booking_seats', sa.Column('showing_id', sa.UUID(as_uuid=True), nullable=True))
    
    # Populate showing_id from the related booking
    op.execute("""
        UPDATE booking_seats
        SET showing_id = bookings.showing_id
        FROM bookings
        WHERE booking_seats.booking_id = bookings.id
    """)
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_booking_seats_showing_id',
        'booking_seats',
        'showings',
        ['showing_id'],
        ['id']
    )
    
    # Make the column non-nullable after populating data
    op.alter_column('booking_seats', 'showing_id', nullable=False)


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_booking_seats_showing_id', 'booking_seats', type_='foreignkey')
    
    # Drop the column
    op.drop_column('booking_seats', 'showing_id')
