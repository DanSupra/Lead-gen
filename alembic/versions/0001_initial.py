"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-07-31 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
deep = None

def upgrade():
    # enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')

    op.create_table(
        'leads',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column('leadgen_id', sa.String(length=255), nullable=True),
        sa.Column('page_id', sa.String(length=255), nullable=True),
        sa.Column('form_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('raw_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=320), nullable=True),
        sa.Column('property_address', sa.String(length=512), nullable=True),
        sa.Column('lat', sa.Float(), nullable=True),
        sa.Column('lon', sa.Float(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='new'),
        sa.Column('score', sa.Integer(), nullable=True, server_default='0'),
        sa.UniqueConstraint('leadgen_id', name='uq_leads_leadgen_id')
    )

    op.create_table(
        'signals',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('event_type', sa.String(length=255), nullable=True),
        sa.Column('event_time', sa.DateTime(), nullable=True),
        sa.Column('geometry', Geometry(geometry_type='GEOMETRY', srid=4326), nullable=True),
        sa.Column('properties', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.create_table(
        'signal_sources',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )

    op.create_table(
        'lead_signal_links',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column('lead_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('signal_id', postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column('reason', sa.String(length=512), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True)
    )

    op.create_table(
        'audits',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column('kind', sa.String(length=255), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )

    op.create_table(
        'suppressions',
        sa.Column('id', postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column('contact', sa.String(length=320), nullable=False),
        sa.Column('reason', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )

def downgrade():
    op.drop_table('suppressions')
    op.drop_table('audits')
    op.drop_table('lead_signal_links')
    op.drop_table('signal_sources')
    op.drop_table('signals')
    op.drop_table('leads')
