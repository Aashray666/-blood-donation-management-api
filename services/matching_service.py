from typing import List, Optional, Dict, Any, Set
import logging
from datetime import datetime

from models.donor import Donor
from models.blood_request import BloodRequest
from repositories.donor_repository import DonorRepository, DonorRepositoryError
from repositories.blood_request_repository import BloodRequestRepository, BloodRequestRepositoryError

logger = logging.getLogger(__name__)


class MatchingServiceError(Exception):
    """Custom exception for matching service operations."""
    pass


class MatchingService:
    """Service class for donor-request matching logic and operations."""
    
    def __init__(
        self, 
        donor_repository: Optional[DonorRepository] = None,
        blood_request_repository: Optional[BloodRequestRepository] = None
    ):
        """
        Initialize the matching service.
        
        Args:
            donor_repository: DonorRepository instance (creates default if None)
            blood_request_repository: BloodRequestRepository instance (creates default if None)
        """
        self.donor_repository = donor_repository or DonorRepository()
        self.blood_request_repository = blood_request_repository or BloodRequestRepository()
        
        # Blood group compatibility mapping
        self._compatibility_map = self._build_compatibility_map()
    
    def _build_compatibility_map(self) -> Dict[str, Set[str]]:
        """
        Build blood group compatibility mapping.
        
        Returns:
            Dictionary mapping recipient blood groups to compatible donor blood groups
        """
        return {
            'A+': {'A+', 'A-', 'O+', 'O-'},
            'A-': {'A-', 'O-'},
            'B+': {'B+', 'B-', 'O+', 'O-'},
            'B-': {'B-', 'O-'},
            'AB+': {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'},  # Universal recipient
            'AB-': {'A-', 'B-', 'AB-', 'O-'},
            'O+': {'O+', 'O-'},
            'O-': {'O-'}  # Universal donor can only receive from O-
        }
    
    def get_compatible_blood_groups(self, recipient_blood_group: str) -> Set[str]:
        """
        Get compatible donor blood groups for a recipient.
        
        Args:
            recipient_blood_group: Blood group of the recipient
            
        Returns:
            Set of compatible donor blood groups
            
        Raises:
            MatchingServiceError: If blood group is invalid
        """
        try:
            if recipient_blood_group not in self._compatibility_map:
                raise MatchingServiceError(f"Invalid blood group: {recipient_blood_group}")
            
            return self._compatibility_map[recipient_blood_group]
            
        except Exception as e:
            logger.error(f"Error getting compatible blood groups for {recipient_blood_group}: {e}")
            raise MatchingServiceError(f"Failed to get compatible blood groups: {str(e)}")
    
    def is_blood_compatible(self, donor_blood_group: str, recipient_blood_group: str) -> bool:
        """
        Check if donor blood group is compatible with recipient blood group.
        
        Args:
            donor_blood_group: Blood group of the donor
            recipient_blood_group: Blood group of the recipient
            
        Returns:
            True if compatible, False otherwise
            
        Raises:
            MatchingServiceError: If blood groups are invalid
        """
        try:
            compatible_groups = self.get_compatible_blood_groups(recipient_blood_group)
            return donor_blood_group in compatible_groups
            
        except Exception as e:
            logger.error(f"Error checking blood compatibility: {e}")
            raise MatchingServiceError(f"Failed to check blood compatibility: {str(e)}")
    
    async def find_matching_donors(
        self, 
        blood_request: BloodRequest,
        city_exact_match: bool = True,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find suitable donors for a blood request.
        
        Args:
            blood_request: BloodRequest object to find donors for
            city_exact_match: Whether to require exact city match (default: True)
            limit: Maximum number of donors to return
            
        Returns:
            List of dictionaries containing donor information and match details
            
        Raises:
            MatchingServiceError: If matching fails
        """
        try:
            # Get compatible blood groups
            compatible_groups = self.get_compatible_blood_groups(blood_request.blood_group)
            
            # Find donors with compatible blood groups
            matching_donors = []
            
            for blood_group in compatible_groups:
                if city_exact_match:
                    # Exact city match
                    donors = await self.donor_repository.search_by_blood_group_and_city(
                        blood_group, blood_request.city
                    )
                else:
                    # Just blood group match
                    donors = await self.donor_repository.search_by_blood_group(blood_group)
                
                for donor in donors:
                    match_info = self._create_match_info(donor, blood_request, city_exact_match)
                    matching_donors.append(match_info)
            
            # Sort by match score (higher is better)
            matching_donors.sort(key=lambda x: x['match_score'], reverse=True)
            
            # Apply limit if specified
            if limit:
                matching_donors = matching_donors[:limit]
            
            logger.info(
                f"Found {len(matching_donors)} matching donors for blood request {blood_request.id}"
            )
            
            return matching_donors
            
        except (DonorRepositoryError, BloodRequestRepositoryError) as e:
            logger.error(f"Repository error finding matching donors: {e}")
            raise MatchingServiceError(f"Failed to find matching donors: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error finding matching donors: {e}")
            raise MatchingServiceError(f"Unexpected error: {str(e)}")
    
    async def find_matching_donors_by_request_id(
        self, 
        request_id: int,
        city_exact_match: bool = True,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find suitable donors for a blood request by request ID.
        
        Args:
            request_id: ID of the blood request
            city_exact_match: Whether to require exact city match (default: True)
            limit: Maximum number of donors to return
            
        Returns:
            List of dictionaries containing donor information and match details
            
        Raises:
            MatchingServiceError: If matching fails or request not found
        """
        try:
            if request_id <= 0:
                raise MatchingServiceError("Blood request ID must be a positive integer")
            
            # Get the blood request
            blood_request = await self.blood_request_repository.get_by_id(request_id)
            if not blood_request:
                raise MatchingServiceError(f"Blood request with ID {request_id} not found")
            
            # Only match active requests
            if blood_request.status != "Active":
                logger.warning(f"Attempting to match non-active blood request {request_id}")
                return []
            
            return await self.find_matching_donors(blood_request, city_exact_match, limit)
            
        except (DonorRepositoryError, BloodRequestRepositoryError) as e:
            logger.error(f"Repository error finding matching donors for request {request_id}: {e}")
            raise MatchingServiceError(f"Failed to find matching donors: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error finding matching donors for request {request_id}: {e}")
            raise MatchingServiceError(f"Unexpected error: {str(e)}")
    
    async def find_requests_for_donor(
        self, 
        donor: Donor,
        city_exact_match: bool = True,
        active_only: bool = True,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find blood requests that a donor can fulfill.
        
        Args:
            donor: Donor object to find requests for
            city_exact_match: Whether to require exact city match (default: True)
            active_only: Whether to only include active requests (default: True)
            limit: Maximum number of requests to return
            
        Returns:
            List of dictionaries containing request information and match details
            
        Raises:
            MatchingServiceError: If matching fails
        """
        try:
            # Get all blood requests that this donor can fulfill
            matching_requests = []
            
            # Get requests based on city matching preference
            if city_exact_match:
                requests = await self.blood_request_repository.get_requests_by_blood_group_and_city(
                    donor.blood_group, donor.city
                )
            else:
                # Get all requests and filter by compatibility
                all_requests = await self.blood_request_repository.get_all()
                requests = [
                    req for req in all_requests 
                    if self.is_blood_compatible(donor.blood_group, req.blood_group)
                ]
            
            # Filter by status if needed
            if active_only:
                requests = [req for req in requests if req.status == "Active"]
            
            # Create match information for each request
            for request in requests:
                if self.is_blood_compatible(donor.blood_group, request.blood_group):
                    match_info = self._create_request_match_info(request, donor, city_exact_match)
                    matching_requests.append(match_info)
            
            # Sort by urgency and match score
            matching_requests.sort(
                key=lambda x: (x['urgency_priority'], x['match_score']), 
                reverse=True
            )
            
            # Apply limit if specified
            if limit:
                matching_requests = matching_requests[:limit]
            
            logger.info(
                f"Found {len(matching_requests)} matching requests for donor {donor.id}"
            )
            
            return matching_requests
            
        except (DonorRepositoryError, BloodRequestRepositoryError) as e:
            logger.error(f"Repository error finding matching requests for donor {donor.id}: {e}")
            raise MatchingServiceError(f"Failed to find matching requests: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error finding matching requests for donor {donor.id}: {e}")
            raise MatchingServiceError(f"Unexpected error: {str(e)}")
    
    async def find_requests_for_donor_by_id(
        self, 
        donor_id: int,
        city_exact_match: bool = True,
        active_only: bool = True,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find blood requests that a donor can fulfill by donor ID.
        
        Args:
            donor_id: ID of the donor
            city_exact_match: Whether to require exact city match (default: True)
            active_only: Whether to only include active requests (default: True)
            limit: Maximum number of requests to return
            
        Returns:
            List of dictionaries containing request information and match details
            
        Raises:
            MatchingServiceError: If matching fails or donor not found
        """
        try:
            if donor_id <= 0:
                raise MatchingServiceError("Donor ID must be a positive integer")
            
            # Get the donor
            donor = await self.donor_repository.get_by_id(donor_id)
            if not donor:
                raise MatchingServiceError(f"Donor with ID {donor_id} not found")
            
            return await self.find_requests_for_donor(donor, city_exact_match, active_only, limit)
            
        except (DonorRepositoryError, BloodRequestRepositoryError) as e:
            logger.error(f"Repository error finding matching requests for donor {donor_id}: {e}")
            raise MatchingServiceError(f"Failed to find matching requests: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error finding matching requests for donor {donor_id}: {e}")
            raise MatchingServiceError(f"Unexpected error: {str(e)}")
    
    async def get_matching_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about matching potential in the system.
        
        Returns:
            Dictionary with matching statistics
            
        Raises:
            MatchingServiceError: If statistics generation fails
        """
        try:
            # Get all active requests and donors
            active_requests = await self.blood_request_repository.get_active_requests()
            all_donors = await self.donor_repository.get_all()
            
            # Calculate matching statistics
            total_active_requests = len(active_requests)
            total_donors = len(all_donors)
            
            # Count requests with potential matches
            requests_with_matches = 0
            total_potential_matches = 0
            
            for request in active_requests:
                matches = await self.find_matching_donors(request, city_exact_match=False)
                if matches:
                    requests_with_matches += 1
                    total_potential_matches += len(matches)
            
            # Calculate statistics by blood group
            blood_group_stats = {}
            for blood_group in self._compatibility_map.keys():
                request_count = len([r for r in active_requests if r.blood_group == blood_group])
                donor_count = len([d for d in all_donors if d.blood_group == blood_group])
                
                blood_group_stats[blood_group] = {
                    'active_requests': request_count,
                    'available_donors': donor_count
                }
            
            # Calculate urgency statistics
            urgency_stats = {}
            for urgency in ['Critical', 'High', 'Medium', 'Low']:
                urgent_requests = [r for r in active_requests if r.urgency == urgency]
                requests_with_matches_count = 0
                
                for request in urgent_requests:
                    matches = await self.find_matching_donors(request, city_exact_match=False)
                    if matches:
                        requests_with_matches_count += 1
                
                urgency_stats[urgency] = {
                    'total_requests': len(urgent_requests),
                    'requests_with_matches': requests_with_matches_count
                }
            
            statistics = {
                'total_active_requests': total_active_requests,
                'total_donors': total_donors,
                'requests_with_potential_matches': requests_with_matches,
                'total_potential_matches': total_potential_matches,
                'match_rate': (requests_with_matches / total_active_requests * 100) if total_active_requests > 0 else 0,
                'blood_group_breakdown': blood_group_stats,
                'urgency_breakdown': urgency_stats,
                'last_updated': datetime.now().isoformat()
            }
            
            logger.debug("Generated matching statistics")
            return statistics
            
        except (DonorRepositoryError, BloodRequestRepositoryError) as e:
            logger.error(f"Repository error generating matching statistics: {e}")
            raise MatchingServiceError(f"Failed to generate matching statistics: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error generating matching statistics: {e}")
            raise MatchingServiceError(f"Unexpected error: {str(e)}")
    
    def _create_match_info(
        self, 
        donor: Donor, 
        blood_request: BloodRequest, 
        city_exact_match: bool
    ) -> Dict[str, Any]:
        """
        Create match information dictionary for a donor-request pair.
        
        Args:
            donor: Donor object
            blood_request: BloodRequest object
            city_exact_match: Whether city matching was used
            
        Returns:
            Dictionary with match information
        """
        # Calculate match score
        match_score = self._calculate_match_score(donor, blood_request, city_exact_match)
        
        return {
            'donor': {
                'id': donor.id,
                'name': donor.name,
                'blood_group': donor.blood_group,
                'city': donor.city,
                'contact_number': donor.contact_number,
                'email': donor.email
            },
            'match_score': match_score,
            'blood_compatible': self.is_blood_compatible(donor.blood_group, blood_request.blood_group),
            'city_match': donor.city.lower() == blood_request.city.lower(),
            'exact_blood_match': donor.blood_group == blood_request.blood_group,
            'match_details': {
                'donor_blood_group': donor.blood_group,
                'required_blood_group': blood_request.blood_group,
                'donor_city': donor.city,
                'required_city': blood_request.city,
                'request_urgency': blood_request.urgency
            }
        }
    
    def _create_request_match_info(
        self, 
        blood_request: BloodRequest, 
        donor: Donor, 
        city_exact_match: bool
    ) -> Dict[str, Any]:
        """
        Create match information dictionary for a request-donor pair.
        
        Args:
            blood_request: BloodRequest object
            donor: Donor object
            city_exact_match: Whether city matching was used
            
        Returns:
            Dictionary with match information
        """
        # Calculate match score
        match_score = self._calculate_match_score(donor, blood_request, city_exact_match)
        
        # Calculate urgency priority for sorting
        urgency_priority = self._get_urgency_priority(blood_request.urgency)
        
        return {
            'request': {
                'id': blood_request.id,
                'patient_name': blood_request.patient_name,
                'blood_group': blood_request.blood_group,
                'city': blood_request.city,
                'urgency': blood_request.urgency,
                'hospital_name': blood_request.hospital_name,
                'contact_number': blood_request.contact_number,
                'created_at': blood_request.created_at.isoformat() if blood_request.created_at else None
            },
            'match_score': match_score,
            'urgency_priority': urgency_priority,
            'blood_compatible': self.is_blood_compatible(donor.blood_group, blood_request.blood_group),
            'city_match': donor.city.lower() == blood_request.city.lower(),
            'exact_blood_match': donor.blood_group == blood_request.blood_group,
            'match_details': {
                'donor_blood_group': donor.blood_group,
                'required_blood_group': blood_request.blood_group,
                'donor_city': donor.city,
                'required_city': blood_request.city,
                'request_urgency': blood_request.urgency
            }
        }
    
    def _calculate_match_score(
        self, 
        donor: Donor, 
        blood_request: BloodRequest, 
        city_exact_match: bool
    ) -> float:
        """
        Calculate a match score for a donor-request pair.
        
        Args:
            donor: Donor object
            blood_request: BloodRequest object
            city_exact_match: Whether city matching was used
            
        Returns:
            Match score (0-100, higher is better)
        """
        score = 0.0
        
        # Base compatibility score (40 points)
        if self.is_blood_compatible(donor.blood_group, blood_request.blood_group):
            score += 40.0
        
        # Exact blood group match bonus (20 points)
        if donor.blood_group == blood_request.blood_group:
            score += 20.0
        
        # City match score (30 points)
        if donor.city.lower() == blood_request.city.lower():
            score += 30.0
        
        # Urgency bonus (10 points for critical, 7 for high, 4 for medium, 1 for low)
        urgency_bonus = {
            'Critical': 10.0,
            'High': 7.0,
            'Medium': 4.0,
            'Low': 1.0
        }
        score += urgency_bonus.get(blood_request.urgency, 0.0)
        
        return min(score, 100.0)  # Cap at 100
    
    def _get_urgency_priority(self, urgency: str) -> int:
        """
        Get numeric priority for urgency level (higher number = higher priority).
        
        Args:
            urgency: Urgency level string
            
        Returns:
            Numeric priority value
        """
        priority_map = {
            'Critical': 4,
            'High': 3,
            'Medium': 2,
            'Low': 1
        }
        return priority_map.get(urgency, 0)