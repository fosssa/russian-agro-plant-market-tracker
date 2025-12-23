"""Pydantic models for data sources."""

from pydantic import BaseModel, Field


class DataSource(BaseModel):
    """Model representing a single data source.
    
    Matches frontend interface:
    - id: number
    - name: string
    - location: string
    - lastRunStatus: boolean
    - lastRunDate: string
    """
    
    id: int = Field(..., description="Unique identifier for the data source")
    name: str = Field(..., description="Display name of the data source")
    location: str = Field(..., description="Location of the data source")
    lastRunStatus: bool = Field(..., description="Status of the last run (true=success, false=failure)")
    lastRunDate: str = Field(..., description="Date of the last run (DD.MM.YYYY format)")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Биржа",
                "location": "Россия",
                "lastRunStatus": True,
                "lastRunDate": "30.12.2025"
            }
        }


class DataSourcesResponse(BaseModel):
    """Response model for list of data sources."""
    
    data: list[DataSource] = Field(..., description="List of data sources")
    total: int = Field(..., description="Total number of data sources")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id": 1,
                        "name": "MySQL Database",
                        "type": "database",
                        "status": "active"
                    }
                ],
                "total": 1
            }
        }


class TriggerDataCollectionResponse(BaseModel):
    """Response model for triggering data collection task."""
    
    success: bool = Field(..., description="Whether the task was successfully triggered")
    message: str = Field(..., description="Status message")
    task_id: str = Field(..., description="Celery task ID for tracking")
    source_id: int = Field(..., description="ID of the data source")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Data collection task triggered successfully",
                "task_id": "abc123-def456",
                "source_id": 1
            }
        }
