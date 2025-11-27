from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    stock_items = relationship("StockItem", back_populates="product")
    sale_items = relationship("SaleItem", back_populates="product")


class StockLocation(Base):
    __tablename__ = "stock_locations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)

    items = relationship("StockItem", back_populates="location")


class StockItem(Base):
    __tablename__ = "stock_items"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=False)
    quantity = Column(Numeric(12, 3), default=0)

    product = relationship("Product", back_populates="stock_items")
    location = relationship("StockLocation", back_populates="items")
    movements = relationship("StockMovement", back_populates="stock_item")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True)
    stock_item_id = Column(Integer, ForeignKey("stock_items.id"), nullable=False)
    change = Column(Numeric(12, 3), nullable=False)
    movement_type = Column(String, nullable=False, default="adjustment")
    reason = Column(String, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    sale_item_id = Column(Integer, ForeignKey("sale_items.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    stock_item = relationship("StockItem", back_populates="movements")
    supplier = relationship("Supplier", back_populates="stock_movements")
    sale_item = relationship("SaleItem", back_populates="stock_movements")
    created_by = relationship("User")
