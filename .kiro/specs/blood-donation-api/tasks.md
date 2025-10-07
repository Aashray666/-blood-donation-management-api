# Implementation Plan

- [x] 1. Set up project structure and dependencies





  - Create FastAPI project directory structure with models, repositories, services, and API folders
  - Set up requirements.txt with FastAPI, SQLite, Jinja2, and other dependencies
  - Create main.py entry point and basic FastAPI app configuration
  - _Requirements: 3.1, 3.2, 4.1_

- [x] 2. Implement core data models and validation





  - [x] 2.1 Create Pydantic models for Donor and BloodRequest


    - Define Donor model with validation for blood group, contact number, and email formats
    - Define BloodRequest model with urgency levels and status validation
    - Add datetime handling and optional field configurations
    - _Requirements: 1.1, 2.1, 4.1_
  
  - [x] 2.2 Create database schema and connection utilities



    - Write SQLite database initialization script with CREATE TABLE statements
    - Implement database connection management and session handling
    - Create database utility functions for connection lifecycle
    - _Requirements: 4.1, 4.3_

- [x] 3. Build repository layer for data access




  - [x] 3.1 Implement DonorRepository class


    - Write CRUD operations (create, get_by_id, get_all, update, delete) for donors
    - Implement search methods for blood group and city filtering
    - Add database error handling and transaction management
    - _Requirements: 1.1, 1.2, 1.3, 1.6, 5.1, 5.2, 5.3_
  
  - [x] 3.2 Implement BloodRequestRepository class


    - Write CRUD operations for blood requests with status management
    - Implement filtering methods for active requests and urgency levels
    - Add methods for request fulfillment and status updates
    - _Requirements: 2.1, 2.2, 2.4, 5.4_
  
  - [ ]* 3.3 Write unit tests for repository operations
    - Create test cases for all CRUD operations using in-memory SQLite
    - Test error handling scenarios and edge cases
    - Verify data integrity and constraint validation
    - _Requirements: 1.1, 2.1, 4.3_

- [x] 4. Develop service layer with business logic





  - [x] 4.1 Create DonorService class


    - Implement donor management operations with validation
    - Add business logic for donor data processing and filtering
    - Integrate with DonorRepository for data operations
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_
  
  - [x] 4.2 Create BloodRequestService class


    - Implement blood request management with status handling
    - Add business logic for request processing and validation
    - Integrate with BloodRequestRepository for data operations
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 4.3 Implement MatchingService for donor-request matching


    - Write blood group compatibility logic (O-, AB+, Rh factor rules)
    - Implement geographic matching based on city proximity
    - Create algorithm to find suitable donors for specific requests
    - _Requirements: 2.3, 5.1, 5.2, 5.3_
  
  - [ ]* 4.4 Write unit tests for service layer
    - Test business logic with mocked repository dependencies
    - Verify matching algorithm accuracy and edge cases
    - Test service error handling and validation
    - _Requirements: 2.3, 5.1, 5.2, 5.3_

- [x] 5. Build FastAPI REST endpoints




  - [x] 5.1 Create donor management API endpoints


    - Implement GET /api/donors with filtering support (blood group, city)
    - Implement POST /api/donors with input validation
    - Implement GET /api/donors/{id}, PUT /api/donors/{id}, DELETE /api/donors/{id}
    - Add proper HTTP status codes and error responses
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 5.2 Create blood request management API endpoints


    - Implement GET /api/requests with filtering (urgency, status, city)
    - Implement POST /api/requests with validation
    - Implement GET /api/requests/{id}, PUT /api/requests/{id}, DELETE /api/requests/{id}
    - Add POST /api/requests/{id}/fulfill endpoint for status updates
    - _Requirements: 2.1, 2.2, 2.4, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 5.3 Create matching and search API endpoints


    - Implement GET /api/requests/{id}/matches for donor matching
    - Implement GET /api/donors/search with blood group and city parameters
    - Add comprehensive filtering and sorting capabilities
    - _Requirements: 2.3, 5.1, 5.2, 5.3, 5.5_
  
  - [ ]* 5.4 Write API endpoint tests
    - Test all endpoints with various input scenarios using httpx
    - Verify HTTP status codes, response formats, and error handling
    - Test filtering, pagination, and search functionality
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 6. Create web dashboard interface





  - [x] 6.1 Set up Jinja2 templates and static file serving


    - Configure FastAPI to serve HTML templates and static files
    - Create base template with navigation and common styling
    - Set up CSS framework (Bootstrap or similar) for responsive design
    - _Requirements: 6.1, 6.5_
  
  - [x] 6.2 Build donor management web pages


    - Create donors list page displaying all donors with search/filter options
    - Build add donor form with client-side validation
    - Implement donor detail and edit pages
    - Add JavaScript for dynamic interactions and API calls
    - _Requirements: 6.2, 6.3, 6.5_
  
  - [x] 6.3 Build blood request management web pages


    - Create requests list page with filtering by status and urgency
    - Build add request form with validation
    - Implement request detail page with donor matching display
    - Add functionality to mark requests as fulfilled
    - _Requirements: 6.2, 6.4, 6.5_
  
  - [x] 6.4 Create main dashboard with overview statistics


    - Build homepage showing summary statistics (total donors, active requests)
    - Add quick action buttons for common operations
    - Implement responsive navigation between different sections
    - _Requirements: 6.1, 6.2_

- [x] 7. Add error handling and logging





  - [x] 7.1 Implement comprehensive error handling


    - Create custom exception classes for business logic errors
    - Add global exception handlers for FastAPI
    - Implement proper error response formatting with detailed messages
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 4.3_
  
  - [x] 7.2 Set up logging and monitoring



    - Configure structured logging for API requests and database operations
    - Add request/response logging middleware
    - Implement health check endpoint for system monitoring
    - _Requirements: 4.3_

- [x] 8. Final integration and testing





  - [x] 8.1 Integrate all components and test end-to-end functionality



    - Connect web dashboard to API endpoints
    - Test complete user workflows (add donor, create request, find matches)
    - Verify data consistency between API and web interface
    - _Requirements: 6.5_
  
  - [ ]* 8.2 Create integration tests
    - Write tests for complete user scenarios using test database
    - Test API and web interface integration
    - Verify error handling across all layers
    - _Requirements: 3.1, 6.5_
  
  - [x] 8.3 Add API documentation and setup instructions


    - Configure FastAPI automatic documentation (Swagger/OpenAPI)
    - Create README with setup and usage instructions
    - Document API endpoints and example requests/responses
    - _Requirements: 3.1_