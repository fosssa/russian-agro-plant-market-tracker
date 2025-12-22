"""Pydantic schemas for database operations."""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from models.db_models import ProductType


# Organization Schemas

class OrganizationBase(BaseModel):
    """Base schema for Organization."""
    name: str = Field(..., min_length=1, description="Organization name")
    link: Optional[str] = Field(None, description="External reference URL")
    location: Optional[str] = Field(None, description="Geographic location")


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = Field(None, min_length=1)
    link: Optional[str] = None
    location: Optional[str] = None


class OrganizationRead(OrganizationBase):
    """Schema for reading an organization."""
    id: int

    model_config = {"from_attributes": True}


# Product Schemas

class ProductBase(BaseModel):
    """Base schema for Product."""
    name: str = Field(..., min_length=1, description="Product name")
    type: ProductType = Field(..., description="Product type/category")
    organization_id: int = Field(..., description="ID of the organization")
    link: Optional[str] = Field(None, description="Product reference URL")


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    
    @field_validator('type', mode='before')
    @classmethod
    def validate_product_type(cls, v):
        """Validate and convert product type to enum."""
        if isinstance(v, str):
            try:
                return ProductType(v)
            except ValueError:
                valid_types = [t.value for t in ProductType]
                raise ValueError(f"Invalid product type. Must be one of: {valid_types}")
        return v


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = Field(None, min_length=1)
    type: Optional[ProductType] = None
    organization_id: Optional[int] = None
    link: Optional[str] = None

    @field_validator('type', mode='before')
    @classmethod
    def validate_product_type(cls, v):
        """Validate and convert product type to enum."""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return ProductType(v)
            except ValueError:
                valid_types = [t.value for t in ProductType]
                raise ValueError(f"Invalid product type. Must be one of: {valid_types}")
        return v


class ProductRead(ProductBase):
    """Schema for reading a product."""
    id: int

    model_config = {"from_attributes": True}


class ProductReadWithOrganization(ProductRead):
    """Schema for reading a product with organization details."""
    organization: OrganizationRead

    model_config = {"from_attributes": True}


# Record Schemas

class RecordBase(BaseModel):
    """Base schema for Record."""
    timestamp: datetime = Field(..., description="Timestamp of the record")
    value: float = Field(..., ge=0, description="Measurement/price value")
    product_id: int = Field(..., description="ID of the product")


class RecordCreate(RecordBase):
    """Schema for creating a record."""
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def validate_timestamp(cls, v):
        """Validate and convert timestamp to datetime."""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                raise ValueError("Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        return v


class RecordUpdate(BaseModel):
    """Schema for updating a record."""
    timestamp: Optional[datetime] = None
    value: Optional[float] = Field(None, ge=0)
    product_id: Optional[int] = None

    @field_validator('timestamp', mode='before')
    @classmethod
    def validate_timestamp(cls, v):
        """Validate and convert timestamp to datetime."""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                raise ValueError("Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        return v


class RecordRead(RecordBase):
    """Schema for reading a record."""
    id: int

    model_config = {"from_attributes": True}


class RecordReadWithProduct(RecordRead):
    """Schema for reading a record with product details."""
    product: ProductRead

    model_config = {"from_attributes": True}


# Utility Operation Schemas

class UtilityOperationResponse(BaseModel):
    """Schema for utility operation responses."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Descriptive message about operation result")
    details: Optional[dict] = Field(None, description="Additional details about the operation")
