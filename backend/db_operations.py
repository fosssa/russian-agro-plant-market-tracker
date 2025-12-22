"""Database initialization and migration script.

This script creates all database tables and optionally seeds initial data.
Run this script to set up the database schema.
"""

from db import Base, engine
from models.db_models import Organization, Product, Record, ProductType
from datetime import datetime, timedelta


def init_db():
    """Create all database tables.
    
    Raises:
        Exception: If table creation fails
    """
    Base.metadata.create_all(bind=engine)


def seed_sample_data():
    """Seed the database with sample data for testing.
    
    This creates sample organizations, products, and records
    to demonstrate the database structure.
    
    Raises:
        Exception: If data seeding fails
    """
    from db import SessionLocal
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_orgs = db.query(Organization).count()
        if existing_orgs > 0:
            return
        
        # Create sample organizations
        org1 = Organization(
            name="Биржа",
            location="Россия",
            link="https://example.com/exchange"
        )
        org2 = Organization(
            name='ООО "Рога и копыта"',
            location="Астрахань",
            link="https://example.com/roga"
        )
        org3 = Organization(
            name='ИП "Грузинские оливки"',
            location="Краснодар",
            link="https://example.com/olives"
        )
        
        db.add_all([org1, org2, org3])
        db.commit()
        
        # Create sample products
        product1 = Product(
            name="Пшеница",
            type=ProductType.PRICE,
            organization_id=org1.id,
            link="https://example.com/wheat"
        )
        product2 = Product(
            name="Кукуруза",
            type=ProductType.PRICE,
            organization_id=org2.id,
            link="https://example.com/corn"
        )
        product3 = Product(
            name="Ячмень",
            type=ProductType.AVERAGE_PRICE,
            organization_id=org3.id,
            link="https://example.com/barley"
        )
        product4 = Product(
            name="Подсолнечник",
            type=ProductType.FUTURES,
            organization_id=org1.id,
            link="https://example.com/sunflower"
        )
        
        db.add_all([product1, product2, product3, product4])
        db.commit()
        
        # Create sample records (30 days of data for each product)
        records = []
        base_date = datetime.now() - timedelta(days=30)
        
        for product in [product1, product2, product3, product4]:
            base_price = 100.0 if product.id == 1 else (120.0 if product.id == 2 else 90.0)
            
            for i in range(30):
                timestamp = base_date + timedelta(days=i, hours=product.id)
                # Add some variation to the price
                import random
                variation = random.uniform(-10, 10)
                value = base_price + variation
                
                record = Record(
                    timestamp=timestamp,
                    value=value,
                    product_id=product.id
                )
                records.append(record)
        
        db.bulk_save_objects(records)
        db.commit()
        
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def drop_all_tables():
    """Drop all database tables. Use with caution!
    
    Raises:
        Exception: If table drop fails
    """
    Base.metadata.drop_all(bind=engine)


def _drop_all_tables_with_confirmation():
    """Drop all database tables with user confirmation. CLI-only function."""
    print("WARNING: Dropping all database tables...")
    response = input("Are you sure? This will delete all data. (yes/no): ")
    if response.lower() == "yes":
        drop_all_tables()
        print("All tables dropped successfully!")
    else:
        print("Operation cancelled.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            print("Creating database tables...")
            init_db()
            print("Database tables created successfully!")
        elif command == "seed":
            print("Creating database tables...")
            init_db()
            print("Database tables created successfully!")
            print("Seeding sample data...")
            seed_sample_data()
            print("Sample data seeded successfully!")
        elif command == "drop":
            _drop_all_tables_with_confirmation()
        elif command == "reset":
            _drop_all_tables_with_confirmation()
            if input("Continue with reset? (yes/no): ").lower() == "yes":
                print("Creating database tables...")
                init_db()
                print("Database tables created successfully!")
                print("Seeding sample data...")
                seed_sample_data()
                print("Sample data seeded successfully!")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: init, seed, drop, reset")
    else:
        print("Database initialization script")
        print("Usage:")
        print("  python init_db.py init   - Create database tables")
        print("  python init_db.py seed   - Create tables and add sample data")
        print("  python init_db.py drop   - Drop all tables (with confirmation)")
        print("  python init_db.py reset  - Drop all tables and recreate with sample data")
