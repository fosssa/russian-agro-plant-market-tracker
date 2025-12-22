# Agro Backend API

Backend API service for data sources and visualizations.

## Features

- RESTful API endpoints for data sources and visualizations
- Type-safe with Pydantic models
- CORS enabled for frontend integration
- FastAPI with automatic OpenAPI documentation

## Installation

This project uses `uv` for dependency management:

```bash
# Install dependencies
uv sync
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation and serialization
- **basedpyright**: Static type checker

## Running the Server

```bash
# Run the server
python main.py
```

The server will start on `http://localhost:7000`

## API Endpoints

### Health Check
- **GET** `/healthcheck`
- Returns: `{"status": "ok"}`

### Utility Endpoints

Database management endpoints for initializing, seeding, dropping, and resetting the database.

#### Initialize Database
- **POST** `/utility/init`
- Creates all database tables
- Response:
  ```json
  {
    "status": "success",
    "message": "Database tables created successfully"
  }
  ```

#### Seed Database
- **POST** `/utility/seed`
- Creates tables and populates with sample data
- Response:
  ```json
  {
    "status": "success",
    "message": "Database initialized and seeded successfully"
  }
  ```

#### Drop All Tables
- **DELETE** `/utility/drop`
- **⚠️ Warning**: Destructive operation that deletes all data
- Requires confirmation in request body:
  ```json
  {
    "confirm": true
  }
  ```
- Response:
  ```json
  {
    "status": "success",
    "message": "All database tables dropped successfully"
  }
  ```

#### Reset Database
- **POST** `/utility/reset`
- **⚠️ Warning**: Destructive operation - drops all tables, recreates them, and seeds with sample data
- Requires confirmation in request body:
  ```json
  {
    "confirm": true
  }
  ```
- Response:
  ```json
  {
    "status": "success",
    "message": "Database reset completed successfully"
  }
  ```

### Data Sources
- **GET** `/api/data-sources`
- Returns: List of all data sources
- Response format:
  ```json
  {
    "data": [
      {
        "id": 1,
        "name": "Биржа",
        "location": "Россия",
        "lastRunStatus": true,
        "lastRunDate": "30.12.2025"
      }
    ],
    "total": 3
  }
  ```

### Filter Options
- **GET** `/api/filters/{filter_type}`
- Path parameter: `filter_type` - Either "source" or "product"
- Returns: List of filter options for the specified type
- Response format:
  ```json
  {
    "data": [
      {
        "value": "source1",
        "label": "Биржа"
      },
      {
        "value": "source2",
        "label": "ООО \"Рога и копыта\""
      }
    ],
    "total": 2
  }
  ```

### Chart Data
- **GET** `/api/chart-data?source={sourceId}&product={productId}`
- Query parameters:
  - `source` - Source ID (e.g., "source1")
  - `product` - Product ID (e.g., "product1")
- Returns: Chart data with 30 days of generated price data
- Response format:
  ```json
  {
    "xAxisData": ["08.11", "09.11", "10.11", ...],
    "seriesData": [99, 103, 104, ...],
    "seriesName": "Цена"
  }
  ```

## Interactive Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:7000/docs`
- ReDoc: `http://localhost:7000/redoc`

## Type Checking

Run type checking with basedpyright:

```bash
uv run basedpyright .
```

## Project Structure

```
backend/
├── main.py                # FastAPI application entry point
├── db_operations.py       # Database initialization and seeding functions
├── db.py                  # Database configuration and session management
├── models/                # Pydantic models and ORM models
│   ├── data_source.py     # Data source models
│   ├── visualization.py   # Visualization models
│   ├── db_models.py       # SQLAlchemy ORM models
│   └── schemas.py         # Additional schema definitions
├── repositories/          # Database repository layer
│   ├── organization_repository.py
│   ├── product_repository.py
│   └── record_repository.py
├── routers/               # API route handlers
│   ├── api.py             # Main API endpoints
│   └── utility.py         # Database utility endpoints
├── pyproject.toml         # Project dependencies
└── README.md              # This file
```

## CORS Configuration

The API is configured to allow all origins for development. In production, update the CORS settings in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Development

The server uses auto-reload during development. Any changes to the code will automatically restart the server.

## Database Management

### Command Line Interface

You can manage the database using the CLI script:

```bash
# Initialize database tables
python db_operations.py init

# Initialize and seed with sample data
python db_operations.py seed

# Drop all tables (with confirmation prompt)
python db_operations.py drop

# Reset database (drop, recreate, and seed)
python db_operations.py reset
```

### API Endpoints

Alternatively, use the utility API endpoints for database management:

```bash
# Initialize database
curl -X POST http://localhost:7000/utility/init

# Seed database
curl -X POST http://localhost:7000/utility/seed

# Drop all tables (requires confirmation)
curl -X DELETE http://localhost:7000/utility/drop \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'

# Reset database (requires confirmation)
curl -X POST http://localhost:7000/utility/reset \
  -H "Content-Type: application/json" \
  -d '{"confirm": true}'
```
