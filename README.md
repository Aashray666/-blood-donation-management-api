# Blood Donation Management API

A comprehensive FastAPI-based web service for managing blood donors and blood requests. This system enables efficient matching between blood donors and those in need, featuring a REST API backend with a responsive web dashboard interface.

## 🚀 Features

- **Donor Management**: Register, update, and search blood donors
- **Blood Request Management**: Create and manage blood requests with urgency levels
- **Smart Matching**: Automatic donor-request matching based on blood compatibility and location
- **Web Dashboard**: User-friendly interface for managing donors and requests
- **REST API**: Complete RESTful API with automatic documentation
- **Real-time Search**: Filter donors and requests by multiple criteria
- **Blood Compatibility**: Implements proper blood donation compatibility rules

## 📋 Requirements

- Python 3.8+
- SQLite (included with Python)
- Modern web browser for dashboard access

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd blood-donation-api
```

### 2. Create Virtual Environment
```bash
# Using venv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Using pip
pip install -r requirements.txt

# Or using uv (recommended)
uv pip install -r requirements.txt
```

### 4. Quick Start
```bash
# Simple startup (recommended)
python start.py
```

This will automatically:
- Initialize the database if needed
- Start the server on http://localhost:8000
- Show you all access points

### 5. Manual Setup (Alternative)
```bash
# Initialize database
python init_db.py

# Start server
python main.py
```

### 6. Access the Application
- **Web Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Testing

### Run Integration Tests
```bash
python simple_test.py
```

This will:
- Start a test server
- Test all major functionality
- Clean up automatically
- Show detailed results

## 🏗️ Project Structure

```
blood-donation-api/
├── api/                    # FastAPI endpoints and routes
│   ├── donors.py          # Donor management endpoints
│   ├── blood_requests.py  # Blood request endpoints
│   └── matching.py        # Donor matching endpoints
├── models/                 # Pydantic models and data structures
│   ├── donor.py           # Donor data model
│   └── blood_request.py   # Blood request data model
├── repositories/           # Data access layer
│   ├── donor_repository.py
│   └── blood_request_repository.py
├── services/              # Business logic layer
│   ├── donor_service.py
│   ├── blood_request_service.py
│   └── matching_service.py
├── database/              # Database configuration and schema
│   ├── connection.py      # Database connection management
│   └── schema.py          # Database schema definitions
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base template
│   ├── dashboard.html     # Main dashboard
│   ├── donors.html        # Donor management page
│   └── requests.html      # Request management page
├── static/                # Static files (CSS, JS)
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── js/
│       ├── main.js        # Common utilities and API client
│       ├── dashboard.js   # Dashboard functionality
│       ├── donors.js      # Donor management
│       └── requests.js    # Request management
├── main.py                # FastAPI application entry point
├── config.py              # Configuration settings
├── init_db.py             # Database initialization script
├── test_integration.py    # Integration tests
├── health_check.py        # Health check endpoints
├── middleware.py          # Custom middleware
├── error_handlers.py      # Error handling
├── logging_config.py      # Logging configuration
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

The application uses environment variables for configuration. Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=sqlite:///blood_donation.db

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/blood_donation_api.log
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Authentication
Currently, the API does not require authentication. This can be added as needed.

### Endpoints Overview

#### Donor Management
- `GET /api/donors` - List all donors with optional filtering
- `POST /api/donors` - Create a new donor
- `GET /api/donors/{id}` - Get specific donor details
- `PUT /api/donors/{id}` - Update donor information
- `DELETE /api/donors/{id}` - Delete a donor

#### Blood Request Management
- `GET /api/requests` - List all blood requests with optional filtering
- `POST /api/requests` - Create a new blood request
- `GET /api/requests/{id}` - Get specific request details
- `PUT /api/requests/{id}` - Update request information
- `DELETE /api/requests/{id}` - Delete a request
- `POST /api/requests/{id}/fulfill` - Mark request as fulfilled

#### Matching & Search
- `GET /api/requests/{id}/matches` - Find suitable donors for a request
- `GET /api/donors/search` - Search donors by criteria

### Example API Usage

#### Create a Donor
```bash
curl -X POST "http://localhost:8000/api/donors" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "blood_group": "O+",
    "city": "New York",
    "contact_number": "+1234567890",
    "email": "john.doe@example.com"
  }'
```

#### Create a Blood Request
```bash
curl -X POST "http://localhost:8000/api/requests" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Jane Smith",
    "blood_group": "O+",
    "city": "New York",
    "urgency": "High",
    "hospital_name": "City Hospital",
    "contact_number": "+0987654321"
  }'
```

#### Find Matching Donors
```bash
curl -X GET "http://localhost:8000/api/requests/1/matches"
```

#### Search Donors
```bash
curl -X GET "http://localhost:8000/api/donors/search?blood_group=O%2B&city=New%20York"
```

### Response Format

All API responses follow a consistent JSON format:

**Success Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "blood_group": "O+",
  "city": "New York",
  "contact_number": "+1234567890",
  "email": "john.doe@example.com",
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Error Response:**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid blood group",
  "details": {
    "field": "blood_group",
    "value": "Invalid"
  }
}
```

### HTTP Status Codes
- `200 OK` - Successful GET, PUT operations
- `201 Created` - Successful POST operations
- `204 No Content` - Successful DELETE operations
- `400 Bad Request` - Invalid input data
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation errors
- `500 Internal Server Error` - Server errors

## 🩸 Blood Compatibility Rules

The system implements proper blood donation compatibility:

| Recipient | Can Receive From |
|-----------|------------------|
| A+ | A+, A-, O+, O- |
| A- | A-, O- |
| B+ | B+, B-, O+, O- |
| B- | B-, O- |
| AB+ | All blood types (Universal recipient) |
| AB- | AB-, A-, B-, O- |
| O+ | O+, O- |
| O- | O- only |

**Universal Donors:**
- O- can donate to all blood types
- O+ can donate to all positive blood types

## 🧪 Testing

### Run Integration Tests
```bash
# Make sure the server is running first
python main.py &

# Run integration tests
python test_integration.py
```

### Manual Testing
1. Start the application: `python main.py`
2. Open http://localhost:8000 in your browser
3. Test the web interface:
   - Add donors through the dashboard
   - Create blood requests
   - Search for matching donors
   - Test filtering and search functionality

## 🚀 Deployment

### Production Setup
1. Set environment variables for production
2. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```
3. Set up reverse proxy (nginx recommended)
4. Configure SSL/TLS certificates
5. Set up monitoring and logging

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python init_db.py

EXPOSE 8000
CMD ["python", "main.py"]
```

## 🔍 Monitoring & Health Checks

The application includes built-in health check endpoints:

- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed system status including database connectivity

## 📝 Logging

Logs are written to:
- Console (development)
- `logs/blood_donation_api.log` (application logs)
- `logs/blood_donation_api_errors.log` (error logs)

Log levels can be configured via environment variables.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the integration tests for usage examples
- Open an issue in the repository

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Kill existing Python processes (Windows)
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force

# Or use a different port
uvicorn main:app --port 8001
```

### Database Issues
```bash
# Reset database
del blood_donation.db  # Windows
rm blood_donation.db   # Linux/Mac
python init_db.py
```

### Testing Issues
If tests fail, try:
```bash
python simple_test.py
```

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
  - Donor and blood request management
  - Web dashboard interface
  - REST API with automatic documentation
  - Blood compatibility matching system