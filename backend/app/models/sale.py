from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="pending")
    total = Column(Numeric(12, 2), default=0)
    discount = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    cashier_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sale", cascade="all, delete-orphan")
    fiscal_documents = relationship("FiscalDocument", back_populates="sale")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Numeric(12, 3), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    document = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)

    sales = relationship("Sale", backref="customer")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    method = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_code = Column(String, nullable=True)
    paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sale = relationship("Sale", back_populates="payments")
