"""Organization repository implementation."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models.db_models import Organization


class OrganizationRepository:
    """Repository for Organization database operations.
    
    Provides an abstraction layer between the application and SQLAlchemy ORM,
    ensuring ORM models never escape the repository boundary.
    """

    def __init__(self, db: Session):
        """Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_all(self) -> list[dict]:
        """Retrieve all organizations.
        
        Returns:
            List of organization dictionaries
        """
        try:
            organizations = self.db.query(Organization).all()
            return [org.to_dict() for org in organizations]
        except SQLAlchemyError as e:
            raise Exception(f"Database error retrieving organizations: {str(e)}")

    def get_by_id(self, org_id: int) -> Optional[dict]:
        """Retrieve a single organization by ID.
        
        Args:
            org_id: Organization ID
            
        Returns:
            Organization dictionary if found, None otherwise
        """
        try:
            organization = self.db.query(Organization).filter(Organization.id == org_id).first()
            return organization.to_dict() if organization else None
        except SQLAlchemyError as e:
            raise Exception(f"Database error retrieving organization {org_id}: {str(e)}")

    def create(self, org_data: dict) -> dict:
        """Insert a new organization.
        
        Args:
            org_data: Dictionary containing organization data
            
        Returns:
            Created organization dictionary
            
        Raises:
            Exception: If database operation fails
        """
        try:
            organization = Organization(**org_data)
            self.db.add(organization)
            self.db.commit()
            self.db.refresh(organization)
            return organization.to_dict()
        except IntegrityError as e:
            self.db.rollback()
            raise Exception(f"Integrity error creating organization: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error creating organization: {str(e)}")

    def update(self, org_id: int, org_data: dict) -> Optional[dict]:
        """Modify an existing organization.
        
        Args:
            org_id: Organization ID
            org_data: Dictionary containing updated organization data
            
        Returns:
            Updated organization dictionary if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            organization = self.db.query(Organization).filter(Organization.id == org_id).first()
            if not organization:
                return None
            
            # Update only provided fields
            for key, value in org_data.items():
                if value is not None and hasattr(organization, key):
                    setattr(organization, key, value)
            
            self.db.commit()
            self.db.refresh(organization)
            return organization.to_dict()
        except IntegrityError as e:
            self.db.rollback()
            raise Exception(f"Integrity error updating organization {org_id}: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error updating organization {org_id}: {str(e)}")

    def delete(self, org_id: int) -> bool:
        """Remove an organization.
        
        Args:
            org_id: Organization ID
            
        Returns:
            True if organization was deleted, False if not found
            
        Raises:
            Exception: If database operation fails
        """
        try:
            organization = self.db.query(Organization).filter(Organization.id == org_id).first()
            if not organization:
                return False
            
            self.db.delete(organization)
            self.db.commit()
            return True
        except IntegrityError as e:
            self.db.rollback()
            raise Exception(f"Integrity error deleting organization {org_id}: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error deleting organization {org_id}: {str(e)}")
