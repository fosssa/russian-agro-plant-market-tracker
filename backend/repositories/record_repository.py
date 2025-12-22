"""Record repository implementation."""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models.db_models import Record, Product


class RecordRepository:
    """Repository for Record database operations.
    
    Provides an abstraction layer between the application and SQLAlchemy ORM,
    ensuring ORM models never escape the repository boundary.
    """

    def __init__(self, db: Session):
        """Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_all(
        self, 
        product_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[dict]:
        """Retrieve all records with optional filtering.
        
        Args:
            product_id: Optional product ID to filter by
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of record dictionaries
        """
        try:
            query = self.db.query(Record)
            
            if product_id is not None:
                query = query.filter(Record.product_id == product_id)
            
            if start_date is not None:
                query = query.filter(Record.timestamp >= start_date)
            
            if end_date is not None:
                query = query.filter(Record.timestamp <= end_date)
            
            # Order by timestamp for consistent results
            query = query.order_by(Record.timestamp)
            
            records = query.all()
            return [record.to_dict() for record in records]
        except SQLAlchemyError as e:
            raise Exception(f"Database error retrieving records: {str(e)}")

    def get_by_id(self, record_id: int) -> Optional[dict]:
        """Retrieve a single record by ID.
        
        Args:
            record_id: Record ID
            
        Returns:
            Record dictionary if found, None otherwise
        """
        try:
            record = self.db.query(Record).filter(Record.id == record_id).first()
            return record.to_dict() if record else None
        except SQLAlchemyError as e:
            raise Exception(f"Database error retrieving record {record_id}: {str(e)}")

    def get_by_product(
        self,
        product_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[dict]:
        """Filter records by product and date range.
        
        Args:
            product_id: Product ID
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of record dictionaries for the specified product and date range
        """
        return self.get_all(product_id=product_id, start_date=start_date, end_date=end_date)

    def get_with_product(self, record_id: int) -> Optional[dict]:
        """Retrieve a record with its product details.
        
        Args:
            record_id: Record ID
            
        Returns:
            Record dictionary with nested product data if found, None otherwise
        """
        try:
            record = (
                self.db.query(Record)
                .options(joinedload(Record.product))
                .filter(Record.id == record_id)
                .first()
            )
            
            if not record:
                return None
            
            record_dict = record.to_dict()
            if record.product:
                record_dict['product'] = record.product.to_dict()
            
            return record_dict
        except SQLAlchemyError as e:
            raise Exception(f"Database error retrieving record {record_id} with product: {str(e)}")

    def create(self, record_data: dict) -> dict:
        """Insert a new record.
        
        Args:
            record_data: Dictionary containing record data
            
        Returns:
            Created record dictionary
            
        Raises:
            Exception: If database operation fails or constraints violated
        """
        try:
            # Validate product exists
            if 'product_id' in record_data:
                product_exists = (
                    self.db.query(Product)
                    .filter(Product.id == record_data['product_id'])
                    .first()
                )
                if not product_exists:
                    raise Exception(f"Product with ID {record_data['product_id']} does not exist")
            
            # Convert timestamp if string
            if 'timestamp' in record_data and isinstance(record_data['timestamp'], str):
                record_data['timestamp'] = datetime.fromisoformat(record_data['timestamp'])
            
            record = Record(**record_data)
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            return record.to_dict()
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e)
            if "UNIQUE constraint" in error_msg and "timestamp" in error_msg:
                raise Exception(f"A record with timestamp {record_data.get('timestamp')} already exists")
            raise Exception(f"Integrity error creating record: {error_msg}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error creating record: {str(e)}")

    def bulk_create(self, records_data: list[dict]) -> list[dict]:
        """Efficient batch insertion for historical data.
        
        Args:
            records_data: List of dictionaries containing record data
            
        Returns:
            List of created record dictionaries
            
        Raises:
            Exception: If database operation fails
        """
        try:
            # Validate all products exist
            product_ids = {r['product_id'] for r in records_data if 'product_id' in r}
            if product_ids:
                existing_products = (
                    self.db.query(Product.id)
                    .filter(Product.id.in_(product_ids))
                    .all()
                )
                existing_ids = {p.id for p in existing_products}
                missing_ids = product_ids - existing_ids
                if missing_ids:
                    raise Exception(f"Products with IDs {missing_ids} do not exist")
            
            # Convert timestamps if strings
            for record_data in records_data:
                if 'timestamp' in record_data and isinstance(record_data['timestamp'], str):
                    record_data['timestamp'] = datetime.fromisoformat(record_data['timestamp'])
            
            records = [Record(**data) for data in records_data]
            self.db.bulk_save_objects(records, return_defaults=True)
            self.db.commit()
            
            # Refresh to get IDs and return dictionaries
            result = []
            for record in records:
                self.db.refresh(record)
                result.append(record.to_dict())
            
            return result
        except IntegrityError as e:
            self.db.rollback()
            raise Exception(f"Integrity error in bulk create: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error in bulk create: {str(e)}")

    def update(self, record_id: int, record_data: dict) -> Optional[dict]:
        """Modify an existing record.
        
        Args:
            record_id: Record ID
            record_data: Dictionary containing updated record data
            
        Returns:
            Updated record dictionary if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        try:
            record = self.db.query(Record).filter(Record.id == record_id).first()
            if not record:
                return None
            
            # Validate product exists if being updated
            if 'product_id' in record_data and record_data['product_id'] is not None:
                product_exists = (
                    self.db.query(Product)
                    .filter(Product.id == record_data['product_id'])
                    .first()
                )
                if not product_exists:
                    raise Exception(f"Product with ID {record_data['product_id']} does not exist")
            
            # Convert timestamp if string
            if 'timestamp' in record_data and isinstance(record_data['timestamp'], str):
                record_data['timestamp'] = datetime.fromisoformat(record_data['timestamp'])
            
            # Update only provided fields
            for key, value in record_data.items():
                if value is not None and hasattr(record, key):
                    setattr(record, key, value)
            
            self.db.commit()
            self.db.refresh(record)
            return record.to_dict()
        except IntegrityError as e:
            self.db.rollback()
            raise Exception(f"Integrity error updating record {record_id}: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error updating record {record_id}: {str(e)}")

    def delete(self, record_id: int) -> bool:
        """Remove a record.
        
        Args:
            record_id: Record ID
            
        Returns:
            True if record was deleted, False if not found
            
        Raises:
            Exception: If database operation fails
        """
        try:
            record = self.db.query(Record).filter(Record.id == record_id).first()
            if not record:
                return False
            
            self.db.delete(record)
            self.db.commit()
            return True
        except IntegrityError as e:
            self.db.rollback()
            raise Exception(f"Integrity error deleting record {record_id}: {str(e)}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Database error deleting record {record_id}: {str(e)}")
