from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class FiscalDocument(Base):
    __tablename__ = "fiscal_documents"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    model = Column(String, nullable=False)  # NFC-e, SAT, MFE
    status = Column(String, default="pending")
    protocol = Column(String, nullable=True)
    access_key = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    events = relationship("FiscalEvent", back_populates="document", cascade="all, delete-orphan")
    sale = relationship("Sale", back_populates="fiscal_documents")


class FiscalEvent(Base):
    __tablename__ = "fiscal_events"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("fiscal_documents.id"), nullable=False)
    type = Column(String, nullable=False)  # emission, cancel, correction
    status = Column(String, nullable=False)
    message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("FiscalDocument", back_populates="events")
