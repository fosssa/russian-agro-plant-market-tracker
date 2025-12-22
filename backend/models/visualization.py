"""Pydantic models for visualization data."""

from pydantic import BaseModel, Field


class FilterOption(BaseModel):
    """Model representing a filter option.
    
    Matches frontend interface:
    - value: string | number
    - label: string
    """
    
    value: str | int = Field(..., description="Value of the filter option")
    label: str = Field(..., description="Display label of the filter option")

    class Config:
        json_schema_extra = {
            "example": {
                "value": "source1",
                "label": "Биржа"
            }
        }


class ChartData(BaseModel):
    """Model representing chart data.
    
    Matches frontend interface:
    - xAxisData: string[]
    - seriesData: number[]
    - seriesName: string
    """
    
    xAxisData: list[str] = Field(..., description="X-axis data points (dates)")
    seriesData: list[int] = Field(..., description="Y-axis data points (values)")
    seriesName: str = Field(..., description="Name of the data series")

    class Config:
        json_schema_extra = {
            "example": {
                "xAxisData": ["01.12", "02.12", "03.12"],
                "seriesData": [100, 120, 115],
                "seriesName": "Цена"
            }
        }


class FilterOptionsResponse(BaseModel):
    """Response model for filter options."""
    
    data: list[FilterOption] = Field(..., description="List of filter options")
    total: int = Field(..., description="Total number of options")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {"value": "source1", "label": "Биржа"},
                    {"value": "source2", "label": "ООО \\'Рога и копыта\\'"}
                ],
                "total": 2
            }
        }
