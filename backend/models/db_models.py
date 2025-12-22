"""SQLAlchemy ORM models for database tables."""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from db import Base


class ProductType(str, enum.Enum):
    """Enum for product types.
    
    Constrains product type values to a predefined set of categories.
    """
    GROSS_HARVEST = "Валовой сбор"
    PRICE = "Цена"
    AVERAGE_PRICE = "Средняя цена"
    FUTURES = "Фьючерс"
    TOTAL_REVENUE = "Общая выручка"
    SALES_VOLUME = "Объём реализации"
    LAND_AREA = "Площадь земель"


class Organization(Base):
    """ORM model for organizations table.
    
    Represents data sources/organizations that provide agricultural data.
    """
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    link = Column(String, nullable=True)
    location = Column(String, nullable=True)

    # Relationships
    products = relationship(
        "Product",
        back_populates="organization",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        """Convert ORM model to dictionary.
        
        Returns:
            Dictionary representation of the organization
        """
        return {
            "id": self.id,
            "name": self.name,
            "link": self.link,
            "location": self.location,
        }


class Product(Base):
    """ORM model for products table.
    
    Represents agricultural products tracked by the system.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(SQLEnum(ProductType, native_enum=False), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    link = Column(String, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="products")
    records = relationship(
        "Record",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        """Convert ORM model to dictionary.
        
        Returns:
            Dictionary representation of the product
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value if isinstance(self.type, ProductType) else self.type,
            "organization_id": self.organization_id,
            "link": self.link,
        }


class Record(Base):
    """ORM model for records table.
    
    Represents time-series data points for products.
    """
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, unique=True, index=True)
    value = Column(Float, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Relationships
    product = relationship("Product", back_populates="records")

    def to_dict(self) -> dict:
        """Convert ORM model to dictionary.
        
        Returns:
            Dictionary representation of the record
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "value": self.value,
            "product_id": self.product_id,
        }
