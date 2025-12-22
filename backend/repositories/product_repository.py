"""Product repository implementation."""

from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models.db_models import Product, Organization


class ProductRepository:
    """Repository for Product database operations.
    
    Provides an abstraction layer between the application and SQLAlchemy ORM,
    ensuring ORM models never escape the repository boundary.
    """

    def __init__(self, db: Session):
        """Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_all(self, organization_id: Optional[int] = None) -> list[dict]:
        """Retrieve all products with optional organization filtering.
        
        Args:
            organization_id: Optional organization ID to filter by
            
        Returns:
            List of product dictionaries
        """
        try:
            query = self.db.query(Product)
            
            if organization_id is not None:
                query = query.filter(Product.organization_id == organization_id)
            
            products = query.all()
            return [product.to_dict() for product in products]
        except SQLAlchemyError as e:
            raise Exception(f"Database error retrieving products: {str(e)}")

    def get_by_id(self, product_id: int) -> Optional[dict]:
        """Retrieve a single product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product dictionary if found, None otherwise
        """
        try:
            product = self.db.query(Product).filter(Product.id == product_id).first()
            return product.to_dict() if product else None
        except SQLAlchemyError as e:
            raise Exception(f"Database error retrieving product {product_id}: {str(e)}")

    def get_by_organization(self, org_id: int) -> list[dict]:
        """Filter products by organization.
        
        Args:
            org_id: Organization ID
            
        Returns:
            List of product dictionaries for the specified organization
        """
        return self.get_all(organization_id=org_id)

    def get_with_organization(self, product_id: int) -> Optional[dict]:
        """Retrieve a product with its organization details.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product dictionary with nested organization data if found, None otherwise
        """
        try:
            product = (
                self.db.query(Product)
                .options(joinedload(Product.organization))
                .filter(Product.id == product_id)
                .first()
            )
            
            if not product:
                return None
            
            product_dict = product.to_dict()
            if product.organization:
                product_dict['organization'] = product.organization.to_dict()
            
            return product_dict
        except SQLAlchemyError as e:
            raise Exception(f"Database error retrieving product {product_id} with organization: {str(e)}")

    def create(self, product_data: dict) -> dict:
        """Insert a new product.
        
        Args:
            product_data: Dictionary containing product data
            
        Returns:
            Created product dictionary
            
        Raises:
            Exception: If database operation fails or foreign key constraint violated
        """
        try:
            # Validate organization exists
            if 'organization_id' in product_data:
                org_exists = (
                    self.db.query(Organization)
                    .filter(Organization.id == product_data['organization_id'])
                    .first()
                )
                if not org_exists:
                    raise Exception(f"Organization with ID {product_data['organization_id']} does not exist")
            
            product = Product(**product_data)
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            return product.to_dict()
        except IntegrityError as e:
            self.db.rollback()
            raise Exception(f"Integrity error creating product: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error creating product: {str(e)}")

    def update(self, product_id: int, product_data: dict) -> Optional[dict]:
        """Modify an existing product.
        
        Args:
            product_id: Product ID
            product_data: Dictionary containing updated product data
            
        Returns:
            Updated product dictionary if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                return None
            
            # Validate organization exists if being updated
            if 'organization_id' in product_data and product_data['organization_id'] is not None:
                org_exists = (
                    self.db.query(Organization)
                    .filter(Organization.id == product_data['organization_id'])
                    .first()
                )
                if not org_exists:
                    raise Exception(f"Organization with ID {product_data['organization_id']} does not exist")
            
            # Update only provided fields
            for key, value in product_data.items():
                if value is not None and hasattr(product, key):
                    setattr(product, key, value)
            
            self.db.commit()
            self.db.refresh(product)
            return product.to_dict()
        except IntegrityError as e:
            self.db.rollback()
            raise Exception(f"Integrity error updating product {product_id}: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error updating product {product_id}: {str(e)}")

    def delete(self, product_id: int) -> bool:
        """Remove a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            True if product was deleted, False if not found
            
        Raises:
            Exception: If database operation fails
        """
        try:
            product = self.db.query(Product).filter(Product.id == product_id).first()
            if not product:
                return False
            
            self.db.delete(product)
            self.db.commit()
            return True
        except IntegrityError as e:
            self.db.rollback()
            raise Exception(f"Integrity error deleting product {product_id}: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error deleting product {product_id}: {str(e)}")
