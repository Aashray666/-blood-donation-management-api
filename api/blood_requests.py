"""
Blood request management API endpoints
FastAPI router for blood request-related operations
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from models.blood_request import BloodRequest, BloodRequestCreate, BloodRequestUpdate
from services.blood_request_service import BloodRequestService, BloodRequestServiceError

# Create router for blood request endpoints
router = APIRouter(prefix="/api/requests", tags=["blood_requests"])

# Initialize blood request service
blood_request_service = BloodRequestService()


@router.get("/", response_model=List[BloodRequest])
async def get_blood_requests(
    blood_group: Optional[str] = Query(None, description="Filter by blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    urgency: Optional[str] = Query(None, description="Filter by urgency (Low, Medium, High, Critical)"),
    status: Optional[str] = Query(None, description="Filter by status (Active, Fulfilled)"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of results (1-100)"),
    offset: Optional[int] = Query(None, ge=0, description="Number of results to skip")
):
    """
    Get all blood requests with optional filtering.
    
    - **blood_group**: Filter by blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)
    - **city**: Filter by city name
    - **urgency**: Filter by urgency level (Low, Medium, High, Critical)
    - **status**: Filter by status (Active, Fulfilled)
    - **limit**: Maximum number of results to return (1-100)
    - **offset**: Number of results to skip for pagination
    """
    try:
        blood_requests = await blood_request_service.get_all_blood_requests(
            blood_group=blood_group,
            city=city,
            urgency=urgency,
            status=status,
            limit=limit,
            offset=offset
        )
        return blood_requests
    except BloodRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving blood requests"
        )


@router.post("/", response_model=BloodRequest, status_code=status.HTTP_201_CREATED)
async def create_blood_request(request_data: BloodRequestCreate):
    """
    Create a new blood request.
    
    - **patient_name**: Name of the patient (letters and spaces only)
    - **blood_group**: Required blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)
    - **city**: City where blood is needed
    - **urgency**: Urgency level (Low, Medium, High, Critical)
    - **hospital_name**: Hospital name (optional)
    - **contact_number**: Contact phone number (10-15 digits)
    """
    try:
        blood_request = await blood_request_service.create_blood_request(request_data)
        return blood_request
    except BloodRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while creating blood request"
        )


@router.get("/{request_id}", response_model=BloodRequest)
async def get_blood_request(request_id: int):
    """
    Get a specific blood request by ID.
    
    - **request_id**: ID of the blood request to retrieve
    """
    try:
        blood_request = await blood_request_service.get_blood_request_by_id(request_id)
        if not blood_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blood request with ID {request_id} not found"
            )
        return blood_request
    except BloodRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving blood request"
        )


@router.put("/{request_id}", response_model=BloodRequest)
async def update_blood_request(request_id: int, request_update: BloodRequestUpdate):
    """
    Update an existing blood request.
    
    - **request_id**: ID of the blood request to update
    - **patient_name**: Name of the patient (optional)
    - **blood_group**: Required blood group (optional)
    - **city**: City where blood is needed (optional)
    - **urgency**: Urgency level (optional)
    - **hospital_name**: Hospital name (optional)
    - **contact_number**: Contact phone number (optional)
    - **status**: Request status (optional)
    """
    try:
        updated_request = await blood_request_service.update_blood_request(request_id, request_update)
        if not updated_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blood request with ID {request_id} not found"
            )
        return updated_request
    except BloodRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while updating blood request"
        )


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blood_request(request_id: int):
    """
    Delete a blood request.
    
    - **request_id**: ID of the blood request to delete
    """
    try:
        success = await blood_request_service.delete_blood_request(request_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blood request with ID {request_id} not found"
            )
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
    except BloodRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while deleting blood request"
        )


@router.post("/{request_id}/fulfill", response_model=BloodRequest)
async def fulfill_blood_request(request_id: int):
    """
    Mark a blood request as fulfilled.
    
    - **request_id**: ID of the blood request to fulfill
    """
    try:
        fulfilled_request = await blood_request_service.fulfill_blood_request(request_id)
        if not fulfilled_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Blood request with ID {request_id} not found"
            )
        return fulfilled_request
    except BloodRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while fulfilling blood request"
        )


@router.get("/filter/active", response_model=List[BloodRequest])
async def get_active_blood_requests():
    """
    Get all active blood requests.
    """
    try:
        active_requests = await blood_request_service.get_active_blood_requests()
        return active_requests
    except BloodRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving active blood requests"
        )


@router.get("/filter/critical", response_model=List[BloodRequest])
async def get_critical_blood_requests():
    """
    Get all critical blood requests (active requests with Critical urgency).
    """
    try:
        critical_requests = await blood_request_service.get_critical_blood_requests()
        return critical_requests
    except BloodRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving critical blood requests"
        )


@router.get("/filter/by-urgency", response_model=List[BloodRequest])
async def get_blood_requests_by_urgency(
    urgency: str = Query(..., description="Urgency level (Low, Medium, High, Critical)")
):
    """
    Get blood requests by urgency level.
    
    - **urgency**: Urgency level to filter by (Low, Medium, High, Critical)
    """
    try:
        requests = await blood_request_service.get_blood_requests_by_urgency(urgency)
        return requests
    except BloodRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving blood requests by urgency"
        )


@router.get("/statistics", response_model=dict)
async def get_blood_request_statistics():
    """
    Get blood request statistics including counts by status, urgency, blood group, and city.
    """
    try:
        statistics = await blood_request_service.get_blood_request_statistics()
        return statistics
    except BloodRequestServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while generating statistics"
        )