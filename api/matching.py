"""
Matching and search API endpoints
FastAPI router for donor-request matching and search operations
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from models.donor import Donor
from services.matching_service import MatchingService, MatchingServiceError
from services.donor_service import DonorService, DonorServiceError

# Create router for matching endpoints
router = APIRouter(prefix="/api", tags=["matching"])

# Initialize services
matching_service = MatchingService()
donor_service = DonorService()


@router.get("/requests/{request_id}/matches", response_model=List[dict])
async def get_matching_donors_for_request(
    request_id: int,
    city_exact_match: bool = Query(True, description="Require exact city match"),
    limit: Optional[int] = Query(None, ge=1, le=50, description="Maximum number of matches (1-50)")
):
    """
    Find suitable donors for a specific blood request.
    
    - **request_id**: ID of the blood request to find matches for
    - **city_exact_match**: Whether to require exact city match (default: True)
    - **limit**: Maximum number of matching donors to return (1-50)
    
    Returns a list of matching donors with match scores and compatibility details.
    """
    try:
        matches = await matching_service.find_matching_donors_by_request_id(
            request_id=request_id,
            city_exact_match=city_exact_match,
            limit=limit
        )
        return matches
    except MatchingServiceError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while finding matching donors"
        )


@router.get("/donors/{donor_id}/matches", response_model=List[dict])
async def get_matching_requests_for_donor(
    donor_id: int,
    city_exact_match: bool = Query(True, description="Require exact city match"),
    active_only: bool = Query(True, description="Only include active requests"),
    limit: Optional[int] = Query(None, ge=1, le=50, description="Maximum number of matches (1-50)")
):
    """
    Find blood requests that a specific donor can fulfill.
    
    - **donor_id**: ID of the donor to find matches for
    - **city_exact_match**: Whether to require exact city match (default: True)
    - **active_only**: Whether to only include active requests (default: True)
    - **limit**: Maximum number of matching requests to return (1-50)
    
    Returns a list of matching blood requests with match scores and compatibility details.
    """
    try:
        matches = await matching_service.find_requests_for_donor_by_id(
            donor_id=donor_id,
            city_exact_match=city_exact_match,
            active_only=active_only,
            limit=limit
        )
        return matches
    except MatchingServiceError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while finding matching requests"
        )


@router.get("/donors/search", response_model=List[Donor])
async def search_donors(
    blood_group: Optional[str] = Query(None, description="Filter by blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of results (1-100)"),
    offset: Optional[int] = Query(None, ge=0, description="Number of results to skip")
):
    """
    Search donors with comprehensive filtering and sorting capabilities.
    
    - **blood_group**: Filter by blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)
    - **city**: Filter by city name
    - **limit**: Maximum number of results to return (1-100)
    - **offset**: Number of results to skip for pagination
    
    This endpoint provides the same functionality as GET /api/donors but with a different path
    for consistency with the matching API design.
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
            detail="Internal server error occurred while searching donors"
        )


@router.get("/donors/search/by-blood-group", response_model=List[Donor])
async def search_donors_by_blood_group(
    blood_group: str = Query(..., description="Blood group to search for (A+, A-, B+, B-, AB+, AB-, O+, O-)")
):
    """
    Search donors by blood group only.
    
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
            detail="Internal server error occurred while searching donors by blood group"
        )


@router.get("/donors/search/by-city", response_model=List[Donor])
async def search_donors_by_city(
    city: str = Query(..., description="City to search in")
):
    """
    Search donors by city only.
    
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
            detail="Internal server error occurred while searching donors by city"
        )


@router.get("/donors/search/compatible", response_model=List[Donor])
async def search_compatible_donors(
    blood_group: str = Query(..., description="Recipient blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of results (1-100)")
):
    """
    Search for donors compatible with a specific blood group.
    
    - **blood_group**: Recipient blood group to find compatible donors for
    - **city**: Filter by city (optional)
    - **limit**: Maximum number of results to return (1-100)
    
    This endpoint finds all donors whose blood is compatible with the specified recipient blood group,
    following standard blood donation compatibility rules.
    """
    try:
        # Get compatible blood groups
        compatible_groups = matching_service.get_compatible_blood_groups(blood_group)
        
        # Search for donors with compatible blood groups
        all_compatible_donors = []
        
        for compatible_blood_group in compatible_groups:
            if city:
                donors = await donor_service.search_donors_by_blood_group_and_city(
                    compatible_blood_group, city
                )
            else:
                donors = await donor_service.search_donors_by_blood_group(compatible_blood_group)
            
            all_compatible_donors.extend(donors)
        
        # Remove duplicates (shouldn't happen but just in case)
        seen_ids = set()
        unique_donors = []
        for donor in all_compatible_donors:
            if donor.id not in seen_ids:
                seen_ids.add(donor.id)
                unique_donors.append(donor)
        
        # Apply limit if specified
        if limit:
            unique_donors = unique_donors[:limit]
        
        return unique_donors
        
    except (MatchingServiceError, DonorServiceError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while searching compatible donors"
        )


@router.get("/matching/statistics", response_model=dict)
async def get_matching_statistics():
    """
    Get comprehensive matching statistics for the system.
    
    Returns statistics about:
    - Total active requests and available donors
    - Requests with potential matches
    - Match rates by blood group
    - Match rates by urgency level
    """
    try:
        statistics = await matching_service.get_matching_statistics()
        return statistics
    except MatchingServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while generating matching statistics"
        )


@router.get("/matching/compatibility", response_model=dict)
async def get_blood_compatibility_info(
    blood_group: str = Query(..., description="Blood group to get compatibility info for (A+, A-, B+, B-, AB+, AB-, O+, O-)")
):
    """
    Get blood compatibility information for a specific blood group.
    
    - **blood_group**: Blood group to get compatibility info for
    
    Returns information about which blood groups can donate to and receive from the specified blood group.
    """
    try:
        # Get compatible donor blood groups (who can donate to this blood group)
        compatible_donors = matching_service.get_compatible_blood_groups(blood_group)
        
        # Get recipient blood groups (who this blood group can donate to)
        compatible_recipients = set()
        for recipient_bg in matching_service._compatibility_map.keys():
            if blood_group in matching_service._compatibility_map[recipient_bg]:
                compatible_recipients.add(recipient_bg)
        
        compatibility_info = {
            'blood_group': blood_group,
            'can_receive_from': sorted(list(compatible_donors)),
            'can_donate_to': sorted(list(compatible_recipients)),
            'is_universal_donor': blood_group == 'O-',
            'is_universal_recipient': blood_group == 'AB+',
            'compatibility_details': {
                'total_compatible_donors': len(compatible_donors),
                'total_compatible_recipients': len(compatible_recipients)
            }
        }
        
        return compatibility_info
        
    except MatchingServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while getting compatibility information"
        )