import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from routers.api import router as api_router
from routers.utility import router as utility_router

root_path = os.getenv("UVICORN_ROOT_PATH", "")

app = FastAPI(
    title="Agro Backend API",
    description="Backend API for data sources and visualizations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router)
app.include_router(utility_router)

@app.get("/healthcheck")
def healthcheck() -> dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Status message indicating the service is operational
    """
    return {"status": "ok"}

def main() -> None:
    """Run the FastAPI application."""
    uvicorn.run(app, host="0.0.0.0", port=7000, root_path=root_path)


if __name__ == "__main__":
    main()
