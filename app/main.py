"""
Main FastAPI application.

This module initializes the FastAPI application with routers, middleware,
and Swagger documentation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.config import settings
from app.routers import auth, coins, health

# Create FastAPI application instance
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(coins.router)
app.include_router(health.router)


@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint that redirects to API documentation.
    
    Returns:
        Redirect response to Swagger UI
    """
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
