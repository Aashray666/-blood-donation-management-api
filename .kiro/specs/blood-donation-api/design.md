# Design Document

## Overview

The Blood Donation Management API is a FastAPI-based web service that manages donor information and blood requests. The system follows a layered architecture with clear separation between API endpoints, business logic, data access, and presentation layers. The application uses SQLite for data persistence and includes a simple web dashboard for user interaction.

## Architecture

The system follows a clean architecture pattern with the following layers:

```
┌─────────────────────────────────────┐
│           Web Dashboard             │
│        (HTML Templates)             │
├─────────────────────────────────────┤
│            FastAPI                  │
│         (REST Endpoints)            │
├─────────────────────────────────────┤
│          Service Layer              │
│       (Business Logic)              │
├─────────────────────────────────────┤
│         Repository Layer            │
│        (Data Access)                │
├─────────────────────────────────────┤
│           SQLite                    │
│         (Database)                  │
└─────────────────────────────────────┘
```

### Key Architectural Decisions

1. **FastAPI Framework**: Chosen for automatic API documentation, type hints, and high performance
2. **SQLite Database**: Lightweight, file-based database suitable for college projects and development
3. **Repository Pattern**: Abstracts data access logic for better testability and maintainability
4. **Service Layer**: Contains business logic and coordinates between API and data layers
5. **Jinja2 Templates**: For serving simple HTML dashboard pages

## Components and Interfaces

### 1. Data Models

#### Donor Model
```python
class Donor(BaseModel):
    id: Optional[int] = None
    name: str
    blood_group: str  # A+, A-, B+, B-, AB+, AB-, O+, O-
    city: str
    contact_number: str
    email: Optional[str] = None
    created_at: Optional[datetime] = None
```

#### Blood Request Model
```python
class BloodRequest(BaseModel):
    id: Optional[int] = None
    patient_name: str
    blood_group: str
    city: str
    urgency: str  # Low, Medium, High, Critical
    hospital_name: Optional[str] = None
    contact_number: str
    status: str = "Active"  # Active, Fulfilled
    created_at: Optional[datetime] = None
```

### 2. API Endpoints

#### Donor Management Endpoints
- `GET /api/donors` - List all donors with optional filtering
- `POST /api/donors` - Create a new donor
- `GET /api/donors/{donor_id}` - Get specific donor details
- `PUT /api/donors/{donor_id}` - Update donor information
- `DELETE /api/donors/{donor_id}` - Delete a donor

#### Blood Request Management Endpoints
- `GET /api/requests` - List all blood requests with optional filtering
- `POST /api/requests` - Create a new blood request
- `GET /api/requests/{request_id}` - Get specific request details
- `PUT /api/requests/{request_id}` - Update request information
- `DELETE /api/requests/{request_id}` - Delete a request
- `POST /api/requests/{request_id}/fulfill` - Mark request as fulfilled

#### Matching Endpoints
- `GET /api/requests/{request_id}/matches` - Find suitable donors for a request
- `GET /api/donors/search` - Search donors by blood group and/or city

#### Dashboard Endpoints
- `GET /` - Main dashboard page
- `GET /donors` - Donors management page
- `GET /requests` - Blood requests management page

### 3. Repository Layer

#### DonorRepository
```python
class DonorRepository:
    def create(self, donor: Donor) -> Donor
    def get_by_id(self, donor_id: int) -> Optional[Donor]
    def get_all(self, filters: Optional[Dict] = None) -> List[Donor]
    def update(self, donor_id: int, donor: Donor) -> Optional[Donor]
    def delete(self, donor_id: int) -> bool
    def search_by_blood_group_and_city(self, blood_group: str, city: str) -> List[Donor]
```

#### BloodRequestRepository
```python
class BloodRequestRepository:
    def create(self, request: BloodRequest) -> BloodRequest
    def get_by_id(self, request_id: int) -> Optional[BloodRequest]
    def get_all(self, filters: Optional[Dict] = None) -> List[BloodRequest]
    def update(self, request_id: int, request: BloodRequest) -> Optional[BloodRequest]
    def delete(self, request_id: int) -> bool
    def get_active_requests(self) -> List[BloodRequest]
```

### 4. Service Layer

#### DonorService
- Handles donor business logic
- Validates donor data
- Coordinates with repository layer
- Implements search and filtering logic

#### BloodRequestService
- Manages blood request operations
- Implements donor matching algorithm
- Handles request fulfillment logic
- Manages request status transitions

#### MatchingService
- Implements blood compatibility logic
- Finds suitable donors for requests
- Considers blood group compatibility and geographic proximity

## Data Models

### Database Schema

#### Donors Table
```sql
CREATE TABLE donors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    blood_group VARCHAR(3) NOT NULL,
    city VARCHAR(100) NOT NULL,
    contact_number VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Blood Requests Table
```sql
CREATE TABLE blood_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name VARCHAR(100) NOT NULL,
    blood_group VARCHAR(3) NOT NULL,
    city VARCHAR(100) NOT NULL,
    urgency VARCHAR(10) NOT NULL,
    hospital_name VARCHAR(100),
    contact_number VARCHAR(15) NOT NULL,
    status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Blood Group Compatibility

The system implements blood donation compatibility rules:
- O- (Universal donor) can donate to all blood groups
- AB+ (Universal recipient) can receive from all blood groups
- Same blood group compatibility (A+ to A+, B- to B-, etc.)
- Rh factor compatibility (+ can receive from +/-, - can only receive from -)

## Error Handling

### HTTP Status Codes
- `200 OK` - Successful GET, PUT operations
- `201 Created` - Successful POST operations
- `204 No Content` - Successful DELETE operations
- `400 Bad Request` - Invalid input data
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation errors
- `500 Internal Server Error` - Server errors

### Error Response Format
```json
{
    "error": "Error type",
    "message": "Detailed error message",
    "details": {
        "field": "Specific field error"
    }
}
```

### Exception Handling Strategy
1. **Validation Errors**: Handled by FastAPI's built-in validation
2. **Database Errors**: Caught and converted to appropriate HTTP responses
3. **Business Logic Errors**: Custom exceptions with meaningful messages
4. **Logging**: All errors logged with appropriate severity levels

## Testing Strategy

### Unit Testing
- **Models**: Test data validation and serialization
- **Repositories**: Test database operations with in-memory SQLite
- **Services**: Test business logic with mocked repositories
- **API Endpoints**: Test HTTP responses and status codes

### Integration Testing
- **Database Integration**: Test with actual SQLite database
- **API Integration**: Test complete request/response cycles
- **Matching Algorithm**: Test donor-request matching scenarios

### Test Data Management
- Use fixtures for consistent test data
- Implement database cleanup between tests
- Create test-specific database instances

### Testing Tools
- **pytest**: Main testing framework
- **httpx**: For testing FastAPI endpoints
- **pytest-asyncio**: For testing async operations
- **Factory Boy**: For generating test data

## Performance Considerations

### Database Optimization
- Index on frequently queried fields (blood_group, city)
- Efficient query patterns for donor matching
- Connection pooling for concurrent requests

### API Performance
- Pagination for large result sets
- Caching for frequently accessed data
- Async/await for I/O operations

### Scalability Considerations
- Stateless API design for horizontal scaling
- Database connection management
- Efficient filtering and search algorithms