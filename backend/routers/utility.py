"""Utility API endpoints for database management operations."""

from fastapi import APIRouter, HTTPException, Body
from typing import Any
from pydantic import BaseModel, Field

from db_operations import init_db, seed_sample_data, drop_all_tables


class ConfirmationRequest(BaseModel):
    """Request model for destructive operations requiring confirmation."""
    confirm: bool = Field(..., description="Must be true to confirm the destructive operation")

router = APIRouter(prefix="/utility", tags=["utilities"])


@router.post("/init")
async def init_endpoint() -> dict[str, Any]:
    """Initialize database schema by creating all tables.
    
    Returns:
        Success response with status and message
        
    Raises:
        HTTPException: If database initialization fails
    """
    try:
        init_db()
        return {
            "status": "success",
            "message": "Database tables created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing database: {str(e)}"
        )


@router.post("/seed")
async def seed_endpoint() -> dict[str, Any]:
    """Initialize database schema and populate with sample data.
    
    Returns:
        Success response with status and message
        
    Raises:
        HTTPException: If database seeding fails
    """
    try:
        init_db()
        seed_sample_data()
        return {
            "status": "success",
            "message": "Database initialized and seeded successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error seeding database: {str(e)}"
        )


@router.delete("/drop")
async def drop_endpoint(
    confirmation: ConfirmationRequest = Body(...)
) -> dict[str, Any]:
    """Remove all database tables and data.
    
    Warning: This is a destructive operation that deletes all data.
    Requires explicit confirmation by setting confirm=true in request body.
    
    Args:
        confirmation: Request body with confirm field that must be true
    
    Returns:
        Success response with status and message
        
    Raises:
        HTTPException: If confirmation is not provided or table drop fails
    """
    if not confirmation.confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required. Set 'confirm' to true to proceed with dropping all tables."
        )
    
    try:
        drop_all_tables()
        return {
            "status": "success",
            "message": "All database tables dropped successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error dropping tables: {str(e)}"
        )


@router.post("/reset")
async def reset_endpoint(
    confirmation: ConfirmationRequest = Body(...)
) -> dict[str, Any]:
    """Completely reset database by dropping, recreating, and seeding.
    
    This operation:
    1. Drops all existing tables
    2. Creates fresh tables
    3. Seeds with sample data
    
    Warning: This is a destructive operation that deletes all existing data.
    Requires explicit confirmation by setting confirm=true in request body.
    
    Args:
        confirmation: Request body with confirm field that must be true
    
    Returns:
        Success response with status and message
        
    Raises:
        HTTPException: If confirmation is not provided or any step of the reset fails
    """
    if not confirmation.confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required. Set 'confirm' to true to proceed with database reset."
        )
    
    try:
        drop_all_tables()
        init_db()
        seed_sample_data()
        return {
            "status": "success",
            "message": "Database reset completed successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during database reset: {str(e)}"
        )
