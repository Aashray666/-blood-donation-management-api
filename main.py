"""
Blood Donation Management API
FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import API routers
from api.donors import router as donors_router
from api.blood_requests import router as blood_requests_router
from api.matching import router as matching_router

# Import health check router
from health_check import router as health_router

# Import error handling and middleware
from error_handlers import register_exception_handlers
from middleware import register_middleware

# Import logging configuration
from logging_config import setup_logging, get_logger

# Set up logging
setup_logging()
logger = get_logger("main")

# Create FastAPI application instance
app = FastAPI(
    title="Blood Donation Management API",
    description="""
    A comprehensive FastAPI-based web service for managing blood donors and blood requests.
    
    ## Features
    
    * **Donor Management**: Register, update, and search blood donors
    * **Blood Request Management**: Create and manage blood requests with urgency levels
    * **Smart Matching**: Automatic donor-request matching based on blood compatibility and location
    * **Web Dashboard**: User-friendly interface for managing donors and requests
    
    ## Blood Compatibility
    
    The system implements proper blood donation compatibility rules:
    - O- (Universal donor) can donate to all blood types
    - AB+ (Universal recipient) can receive from all blood groups
    - Same blood group compatibility with Rh factor considerations
    
    ## Usage
    
    1. **Add Donors**: Register blood donors with their information
    2. **Create Requests**: Submit blood requests for patients in need
    3. **Find Matches**: Use the matching system to find compatible donors
    4. **Manage Data**: Update, search, and filter donors and requests
    
    For detailed examples and testing, visit the interactive documentation below.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Blood Donation Management System",
        "email": "support@blooddonation.example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
)

# Register middleware (order matters - registered in reverse execution order)
register_middleware(app)

# Register exception handlers
register_exception_handlers(app)

logger.info("Blood Donation Management API starting up")

# Include API routers
app.include_router(donors_router)
app.include_router(blood_requests_router)
app.include_router(matching_router)
app.include_router(health_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Note: Health check endpoints are now handled by the health_router

# Dashboard routes
from fastapi import Request
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/donors", response_class=HTMLResponse)
async def donors_page(request: Request):
    """Donors management page"""
    return templates.TemplateResponse("donors.html", {"request": request})

@app.get("/requests", response_class=HTMLResponse)
async def requests_page(request: Request):
    """Blood requests management page"""
    return templates.TemplateResponse("requests.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Blood Donation Management API server")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_config=None  # Use our custom logging configuration
    )