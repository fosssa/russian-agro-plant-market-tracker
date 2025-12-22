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
