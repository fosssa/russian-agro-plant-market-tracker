"""API route handlers for data sources and visualizations."""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Any
from datetime import datetime, timedelta

from models.data_source import DataSource, DataSourcesResponse, TriggerDataCollectionResponse
from models.visualization import FilterOption, FilterOptionsResponse, ChartData
from repositories.organization_repository import OrganizationRepository
from repositories.product_repository import ProductRepository
from repositories.record_repository import RecordRepository
from db import get_db
from celery.tasks import collect_data_for_source

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/data-sources", response_model=DataSourcesResponse)
async def get_data_sources_endpoint(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Get all data sources.
    
    Returns:
        DataSourcesResponse containing list of data sources and total count
        
    Raises:
        HTTPException: If there's an error retrieving data sources
    """
    try:
        # Initialize repository with database session
        org_repo = OrganizationRepository(db)
        
        # Get all organizations from database
        organizations = org_repo.get_all()
        
        # Transform organizations to DataSource format
        current_date = datetime.now().strftime("%d.%m.%Y")
        data_sources = []
        for org in organizations:
            data_sources.append({
                "id": org["id"],
                "name": org["name"],
                "location": org["location"] or "",
                "lastRunStatus": True,  # Placeholder until execution tracking is implemented
                "lastRunDate": current_date  # Placeholder until execution tracking is implemented
            })
        
        # Validate each source against the Pydantic model
        validated_sources = [DataSource(**source) for source in data_sources]
        
        return {
            "data": validated_sources,
            "total": len(validated_sources)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data sources: {str(e)}")


@router.post("/data-sources/{source_id}/collect", response_model=TriggerDataCollectionResponse)
async def trigger_data_collection_endpoint(source_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Trigger data collection for a specific data source.
    
    This endpoint initiates an asynchronous data collection task via Celery.
    The task will collect data from the specified source and update the
    last run date and status upon completion.
    
    Args:
        source_id: ID of the data source to collect data from
    
    Returns:
        TriggerDataCollectionResponse with task info
        
    Raises:
        HTTPException: If the source doesn't exist or task fails to start
    """
    try:
        # Verify the source exists
        org_repo = OrganizationRepository(db)
        organization = org_repo.get_by_id(source_id)
        
        if not organization:
            raise HTTPException(status_code=404, detail=f"Data source with id {source_id} not found")
        
        # Trigger the Celery task
        task = collect_data_for_source.delay(source_id)
        
        return {
            "success": True,
            "message": f"Data collection task triggered for source '{organization['name']}'",
            "task_id": task.id,
            "source_id": source_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering data collection: {str(e)}")


@router.get("/filters/{filter_type}", response_model=FilterOptionsResponse)
async def get_filter_options_endpoint(filter_type: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Get filter options for visualization.
    
    Args:
        filter_type: Type of filter ('source' or 'product')
    
    Returns:
        FilterOptionsResponse containing list of filter options and total count
        
    Raises:
        HTTPException: If there's an error retrieving filter options
    """
    try:
        if filter_type not in ["source", "product"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid filter type: {filter_type}. Must be 'source' or 'product'"
            )
        
        # Initialize appropriate repository based on filter type
        if filter_type == "source":
            org_repo = OrganizationRepository(db)
            entities = org_repo.get_all()
        else:  # product
            product_repo = ProductRepository(db)
            entities = product_repo.get_all()
        
        # Transform entities to FilterOption format
        filter_options = [
            {"value": entity["id"], "label": entity["name"]}
            for entity in entities
        ]
        
        # Validate each option against the Pydantic model
        validated_options = [FilterOption(**option) for option in filter_options]
        
        return {
            "data": validated_options,
            "total": len(validated_options)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving filter options: {str(e)}")


@router.get("/chart-data", response_model=ChartData)
async def get_chart_data_endpoint(
    source: int = Query(..., description="Source ID for filtering"),
    product: int = Query(..., description="Product ID for filtering"),
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """Get chart data based on source and product filters.
    
    Args:
        source: Source (organization) ID for filtering
        product: Product ID for filtering
    
    Returns:
        ChartData containing xAxisData, seriesData, and seriesName
        
    Raises:
        HTTPException: If there's an error retrieving chart data
    """
    try:
        # Initialize repositories
        product_repo = ProductRepository(db)
        record_repo = RecordRepository(db)
        
        # Get product to validate it exists and get its details
        product_data = product_repo.get_by_id(product)
        
        # If product not found or doesn't belong to the specified organization, return empty data
        if not product_data or product_data["organization_id"] != source:
            return {
                "xAxisData": [],
                "seriesData": [],
                "seriesName": ""
            }
        
        # Calculate date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Get records for the product within the date range
        records = record_repo.get_by_product(
            product_id=product,
            start_date=start_date,
            end_date=end_date
        )
        
        # Transform records to chart data format
        x_axis_data = []
        series_data = []
        
        for record in records:
            # Parse timestamp and format as DD.MM
            if isinstance(record["timestamp"], str):
                timestamp = datetime.fromisoformat(record["timestamp"])
            else:
                timestamp = record["timestamp"]
            
            x_axis_data.append(timestamp.strftime("%d.%m"))
            series_data.append(round(record["value"]))
        
        # Use product type as series name
        series_name = product_data.get("type", "")
        
        # Validate chart data against the Pydantic model
        validated_data = ChartData(
            xAxisData=x_axis_data,
            seriesData=series_data,
            seriesName=series_name
        )
        
        return validated_data.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chart data: {str(e)}")
