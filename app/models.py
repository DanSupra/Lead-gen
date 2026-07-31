from sqlalchemy import (
    Column, String, Integer, DateTime, JSON, Enum, Float, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

def gen_uuid():
    return str(uuid.uuid4())

class Lead(Base):
    __tablename__ = "leads"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    leadgen_id = Column(String, index=True)
    page_id = Column(String, index=True)
    form_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    raw_payload = Column(JSONB)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    email = Column(String)
    property_address = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    source = Column(String)
    status = Column(String, default="new")
    score = Column(Integer, default=0)

class Signal(Base):
    __tablename__ = "signals"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    source = Column(String, index=True)
    event_type = Column(String)
    event_time = Column(DateTime)
    geometry = Column(JSONB)
    properties = Column(JSONB)
