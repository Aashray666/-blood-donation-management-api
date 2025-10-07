"""
Donor management API endpoints
FastAPI router for donor-related operations
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from models.donor import Donor, DonorCreate, DonorUpdate
from services.donor_service import DonorService, DonorServiceError

# Create router for donor endpoints
router = APIRouter(prefix="/api/donors", tags=["donors"])

# Initialize donor service
donor_service = DonorService()


@router.get("/", response_model=List[Donor])
async def get_donors(
    blood_group: Optional[str] = Query(None, description="Filter by blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of results (1-100)"),
    offset: Optional[int] = Query(None, ge=0, description="Number of results to skip")
):
    """
    Get all donors with optional filtering.
    
    - **blood_group**: Filter by blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)
    - **city**: Filter by city name
    - **limit**: Maximum number of results to return (1-100)
    - **offset**: Number of results to skip for pagination
    """
    try:
        donors = await donor_service.get_all_donors(
            blood_group=blood_group,
            city=city,
            limit=limit,
            offset=offset
        )
        return donors
    except DonorServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving donors"
        )


@router.post("/", response_model=Donor, status_code=status.HTTP_201_CREATED)
async def create_donor(donor_data: DonorCreate):
    """
    Create a new donor.
    
    - **name**: Full name of the donor (letters and spaces only)
    - **blood_group**: Blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)
    - **city**: City where donor is located
    - **contact_number**: Contact phone number (10-15 digits)
    - **email**: Email address (optional)
    """
    try:
        donor = await donor_service.create_donor(donor_data)
        return donor
    except DonorServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while creating donor"
        )


@router.get("/{donor_id}", response_model=Donor)
async def get_donor(donor_id: int):
    """
    Get a specific donor by ID.
    
    - **donor_id**: ID of the donor to retrieve
    """
    try:
        donor = await donor_service.get_donor_by_id(donor_id)
        if not donor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Donor with ID {donor_id} not found"
            )
        return donor
    except DonorServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while retrieving donor"
        )


@router.put("/{donor_id}", response_model=Donor)
async def update_donor(donor_id: int, donor_update: DonorUpdate):
    """
    Update an existing donor.
    
    - **donor_id**: ID of the donor to update
    - **name**: Full name of the donor (optional)
    - **blood_group**: Blood group (optional)
    - **city**: City where donor is located (optional)
    - **contact_number**: Contact phone number (optional)
    - **email**: Email address (optional)
    """
    try:
        updated_donor = await donor_service.update_donor(donor_id, donor_update)
        if not updated_donor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Donor with ID {donor_id} not found"
            )
        return updated_donor
    except DonorServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while updating donor"
        )


@router.delete("/{donor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_donor(donor_id: int):
    """
    Delete a donor.
    
    - **donor_id**: ID of the donor to delete
    """
    try:
        success = await donor_service.delete_donor(donor_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Donor with ID {donor_id} not found"
            )
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
    except DonorServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while deleting donor"
        )


@router.get("/search/by-blood-group", response_model=List[Donor])
async def search_donors_by_blood_group(
    blood_group: str = Query(..., description="Blood group to search for (A+, A-, B+, B-, AB+, AB-, O+, O-)")
):
    """
    Search donors by blood group.
    
    - **blood_group**: Blood group to search for (A+, A-, B+, B-, AB+, AB-, O+, O-)
    """
    try:
        donors = await donor_service.search_donors_by_blood_group(blood_group)
        return donors
    except DonorServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while searching donors"
        )


@router.get("/search/by-city", response_model=List[Donor])
async def search_donors_by_city(
    city: str = Query(..., description="City to search in")
):
    """
    Search donors by city.
    
    - **city**: City to search in
    """
    try:
        donors = await donor_service.search_donors_by_city(city)
        return donors
    except DonorServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while searching donors"
        )


@router.get("/statistics", response_model=dict)
async def get_donor_statistics():
    """
    Get donor statistics including counts by blood group and city.
    """
    try:
        statistics = await donor_service.get_donor_statistics()
        return statistics
    except DonorServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while generating statistics"
        )