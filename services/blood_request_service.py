from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from models.blood_request import BloodRequest, BloodRequestCreate, BloodRequestUpdate
from repositories.blood_request_repository import BloodRequestRepository, BloodRequestRepositoryError

logger = logging.getLogger(__name__)


class BloodRequestServiceError(Exception):
    """Custom exception for blood request service operations."""
    pass


class BloodRequestService:
    """Service class for blood request business logic and operations."""
    
    def __init__(self, blood_request_repository: Optional[BloodRequestRepository] = None):
        """
        Initialize the blood request service.
        
        Args:
            blood_request_repository: BloodRequestRepository instance (creates default if None)
        """
        self.blood_request_repository = blood_request_repository or BloodRequestRepository()
    
    async def create_blood_request(self, request_data: BloodRequestCreate) -> BloodRequest:
        """
        Create a new blood request with business logic validation.
        
        Args:
            request_data: BloodRequestCreate object with request information
            
        Returns:
            Created BloodRequest object
            
        Raises:
            BloodRequestServiceError: If creation fails or validation errors occur
        """
        try:
            # Additional business logic validation
            await self._validate_blood_request_creation(request_data)
            
            # Create the blood request
            blood_request = await self.blood_request_repository.create(request_data)
            
            logger.info(f"Successfully created blood request with ID: {blood_request.id}")
            return blood_request
            
        except BloodRequestRepositoryError as e:
            logger.error(f"Repository error creating blood request: {e}")
            raise BloodRequestServiceError(f"Failed to create blood request: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating blood request: {e}")
            raise BloodRequestServiceError(f"Unexpected error: {str(e)}")
    
    async def get_blood_request_by_id(self, request_id: int) -> Optional[BloodRequest]:
        """
        Retrieve a blood request by ID with business logic.
        
        Args:
            request_id: ID of the blood request to retrieve
            
        Returns:
            BloodRequest object if found, None otherwise
            
        Raises:
            BloodRequestServiceError: If retrieval fails
        """
        try:
            if request_id <= 0:
                raise BloodRequestServiceError("Blood request ID must be a positive integer")
            
            blood_request = await self.blood_request_repository.get_by_id(request_id)
            
            if blood_request:
                logger.debug(f"Retrieved blood request with ID: {request_id}")
            else:
                logger.debug(f"Blood request with ID {request_id} not found")
            
            return blood_request
            
        except BloodRequestRepositoryError as e:
            logger.error(f"Repository error retrieving blood request {request_id}: {e}")
            raise BloodRequestServiceError(f"Failed to retrieve blood request: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving blood request {request_id}: {e}")
            raise BloodRequestServiceError(f"Unexpected error: {str(e)}")
    
    async def get_all_blood_requests(
        self,
        blood_group: Optional[str] = None,
        city: Optional[str] = None,
        urgency: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[BloodRequest]:
        """
        Retrieve all blood requests with filtering and pagination.
        
        Args:
            blood_group: Filter by blood group
            city: Filter by city
            urgency: Filter by urgency level
            status: Filter by status
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of BloodRequest objects
            
        Raises:
            BloodRequestServiceError: If retrieval fails
        """
        try:
            # Build filters
            filters = {}
            
            if blood_group:
                # Validate blood group format
                valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
                if blood_group not in valid_blood_groups:
                    raise BloodRequestServiceError(
                        f"Invalid blood group. Must be one of: {', '.join(valid_blood_groups)}"
                    )
                filters['blood_group'] = blood_group
            
            if city:
                filters['city'] = city.strip()
            
            if urgency:
                # Validate urgency level
                valid_urgency_levels = {'Low', 'Medium', 'High', 'Critical'}
                if urgency not in valid_urgency_levels:
                    raise BloodRequestServiceError(
                        f"Invalid urgency level. Must be one of: {', '.join(valid_urgency_levels)}"
                    )
                filters['urgency'] = urgency
            
            if status:
                # Validate status
                valid_statuses = {'Active', 'Fulfilled'}
                if status not in valid_statuses:
                    raise BloodRequestServiceError(
                        f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                    )
                filters['status'] = status
            
            if limit is not None:
                if limit <= 0:
                    raise BloodRequestServiceError("Limit must be a positive integer")
                filters['limit'] = limit
            
            if offset is not None:
                if offset < 0:
                    raise BloodRequestServiceError("Offset must be non-negative")
                filters['offset'] = offset
            
            blood_requests = await self.blood_request_repository.get_all(filters)
            
            logger.debug(f"Retrieved {len(blood_requests)} blood requests with filters: {filters}")
            return blood_requests
            
        except BloodRequestRepositoryError as e:
            logger.error(f"Repository error retrieving blood requests: {e}")
            raise BloodRequestServiceError(f"Failed to retrieve blood requests: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving blood requests: {e}")
            raise BloodRequestServiceError(f"Unexpected error: {str(e)}")
    
    async def update_blood_request(
        self, 
        request_id: int, 
        request_update: BloodRequestUpdate
    ) -> Optional[BloodRequest]:
        """
        Update an existing blood request with business logic validation.
        
        Args:
            request_id: ID of the blood request to update
            request_update: BloodRequestUpdate object with fields to update
            
        Returns:
            Updated BloodRequest object if successful, None if request not found
            
        Raises:
            BloodRequestServiceError: If update fails or validation errors occur
        """
        try:
            if request_id <= 0:
                raise BloodRequestServiceError("Blood request ID must be a positive integer")
            
            # Check if blood request exists
            existing_request = await self.blood_request_repository.get_by_id(request_id)
            if not existing_request:
                return None
            
            # Additional business logic validation
            await self._validate_blood_request_update(request_update, existing_request)
            
            # Update the blood request
            updated_request = await self.blood_request_repository.update(request_id, request_update)
            
            if updated_request:
                logger.info(f"Successfully updated blood request with ID: {request_id}")
            
            return updated_request
            
        except BloodRequestRepositoryError as e:
            logger.error(f"Repository error updating blood request {request_id}: {e}")
            raise BloodRequestServiceError(f"Failed to update blood request: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating blood request {request_id}: {e}")
            raise BloodRequestServiceError(f"Unexpected error: {str(e)}")
    
    async def delete_blood_request(self, request_id: int) -> bool:
        """
        Delete a blood request with business logic checks.
        
        Args:
            request_id: ID of the blood request to delete
            
        Returns:
            True if deletion was successful, False if request not found
            
        Raises:
            BloodRequestServiceError: If deletion fails
        """
        try:
            if request_id <= 0:
                raise BloodRequestServiceError("Blood request ID must be a positive integer")
            
            # Check if blood request exists before deletion
            existing_request = await self.blood_request_repository.get_by_id(request_id)
            if not existing_request:
                return False
            
            # Additional business logic checks could go here
            # (e.g., prevent deletion of fulfilled requests, etc.)
            
            success = await self.blood_request_repository.delete(request_id)
            
            if success:
                logger.info(f"Successfully deleted blood request with ID: {request_id}")
            
            return success
            
        except BloodRequestRepositoryError as e:
            logger.error(f"Repository error deleting blood request {request_id}: {e}")
            raise BloodRequestServiceError(f"Failed to delete blood request: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting blood request {request_id}: {e}")
            raise BloodRequestServiceError(f"Unexpected error: {str(e)}")
    
    async def get_active_blood_requests(self) -> List[BloodRequest]:
        """
        Retrieve all active blood requests.
        
        Returns:
            List of active BloodRequest objects
            
        Raises:
            BloodRequestServiceError: If retrieval fails
        """
        try:
            active_requests = await self.blood_request_repository.get_active_requests()
            
            logger.debug(f"Retrieved {len(active_requests)} active blood requests")
            return active_requests
            
        except BloodRequestRepositoryError as e:
            logger.error(f"Repository error retrieving active blood requests: {e}")
            raise BloodRequestServiceError(f"Failed to retrieve active blood requests: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving active blood requests: {e}")
            raise BloodRequestServiceError(f"Unexpected error: {str(e)}")
    
    async def get_blood_requests_by_urgency(self, urgency: str) -> List[BloodRequest]:
        """
        Retrieve blood requests by urgency level with validation.
        
        Args:
            urgency: Urgency level to filter by
            
        Returns:
            List of BloodRequest objects with specified urgency
            
        Raises:
            BloodRequestServiceError: If retrieval fails or validation errors occur
        """
        try:
            # Validate urgency level
            valid_urgency_levels = {'Low', 'Medium', 'High', 'Critical'}
            if urgency not in valid_urgency_levels:
                raise BloodRequestServiceError(
                    f"Invalid urgency level. Must be one of: {', '.join(valid_urgency_levels)}"
                )
            
            requests = await self.blood_request_repository.get_requests_by_urgency(urgency)
            
            logger.debug(f"Retrieved {len(requests)} blood requests with urgency: {urgency}")
            return requests
            
        except BloodRequestRepositoryError as e:
            logger.error(f"Repository error retrieving blood requests by urgency {urgency}: {e}")
            raise BloodRequestServiceError(f"Failed to retrieve blood requests: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving blood requests by urgency {urgency}: {e}")
            raise BloodRequestServiceError(f"Unexpected error: {str(e)}")
    
    async def fulfill_blood_request(self, request_id: int) -> Optional[BloodRequest]:
        """
        Mark a blood request as fulfilled with business logic validation.
        
        Args:
            request_id: ID of the blood request to fulfill
            
        Returns:
            Updated BloodRequest object if successful, None if request not found
            
        Raises:
            BloodRequestServiceError: If fulfillment fails or validation errors occur
        """
        try:
            if request_id <= 0:
                raise BloodRequestServiceError("Blood request ID must be a positive integer")
            
            # Check if blood request exists and is active
            existing_request = await self.blood_request_repository.get_by_id(request_id)
            if not existing_request:
                return None
            
            if existing_request.status == "Fulfilled":
                raise BloodRequestServiceError("Blood request is already fulfilled")
            
            # Fulfill the request
            fulfilled_request = await self.blood_request_repository.fulfill_request(request_id)
            
            if fulfilled_request:
                logger.info(f"Successfully fulfilled blood request with ID: {request_id}")
            
            return fulfilled_request
            
        except BloodRequestRepositoryError as e:
            logger.error(f"Repository error fulfilling blood request {request_id}: {e}")
            raise BloodRequestServiceError(f"Failed to fulfill blood request: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fulfilling blood request {request_id}: {e}")
            raise BloodRequestServiceError(f"Unexpected error: {str(e)}")
    
    async def get_blood_request_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about blood requests in the system.
        
        Returns:
            Dictionary with blood request statistics
            
        Raises:
            BloodRequestServiceError: If statistics retrieval fails
        """
        try:
            # Get total count
            total_requests = await self.blood_request_repository.count_requests()
            
            # Get count by status
            active_count = await self.blood_request_repository.count_requests({'status': 'Active'})
            fulfilled_count = await self.blood_request_repository.count_requests({'status': 'Fulfilled'})
            
            # Get count by urgency
            urgency_stats = {}
            valid_urgency_levels = {'Low', 'Medium', 'High', 'Critical'}
            
            for urgency in valid_urgency_levels:
                count = await self.blood_request_repository.count_requests({'urgency': urgency})
                urgency_stats[urgency] = count
            
            # Get count by blood group
            blood_group_stats = {}
            valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
            
            for blood_group in valid_blood_groups:
                count = await self.blood_request_repository.count_requests({'blood_group': blood_group})
                blood_group_stats[blood_group] = count
            
            # Get all requests to calculate city statistics
            all_requests = await self.blood_request_repository.get_all()
            city_stats = {}
            
            for request in all_requests:
                city = request.city
                city_stats[city] = city_stats.get(city, 0) + 1
            
            statistics = {
                'total_requests': total_requests,
                'status_distribution': {
                    'Active': active_count,
                    'Fulfilled': fulfilled_count
                },
                'urgency_distribution': urgency_stats,
                'blood_group_distribution': blood_group_stats,
                'city_distribution': city_stats,
                'last_updated': datetime.now().isoformat()
            }
            
            logger.debug("Generated blood request statistics")
            return statistics
            
        except BloodRequestRepositoryError as e:
            logger.error(f"Repository error generating blood request statistics: {e}")
            raise BloodRequestServiceError(f"Failed to generate statistics: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error generating blood request statistics: {e}")
            raise BloodRequestServiceError(f"Unexpected error: {str(e)}")
    
    async def get_critical_blood_requests(self) -> List[BloodRequest]:
        """
        Retrieve all critical blood requests (active requests with Critical urgency).
        
        Returns:
            List of critical BloodRequest objects
            
        Raises:
            BloodRequestServiceError: If retrieval fails
        """
        try:
            filters = {
                'urgency': 'Critical',
                'status': 'Active'
            }
            
            critical_requests = await self.blood_request_repository.get_all(filters)
            
            logger.debug(f"Retrieved {len(critical_requests)} critical blood requests")
            return critical_requests
            
        except BloodRequestRepositoryError as e:
            logger.error(f"Repository error retrieving critical blood requests: {e}")
            raise BloodRequestServiceError(f"Failed to retrieve critical blood requests: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving critical blood requests: {e}")
            raise BloodRequestServiceError(f"Unexpected error: {str(e)}")
    
    async def _validate_blood_request_creation(self, request_data: BloodRequestCreate) -> None:
        """
        Additional business logic validation for blood request creation.
        
        Args:
            request_data: BloodRequestCreate object to validate
            
        Raises:
            BloodRequestServiceError: If validation fails
        """
        # Additional business rules can be added here
        
        # Validate city is not empty after stripping
        if not request_data.city.strip():
            raise BloodRequestServiceError("City cannot be empty")
        
        # Validate patient name is not empty after stripping
        if not request_data.patient_name.strip():
            raise BloodRequestServiceError("Patient name cannot be empty")
        
        # Business rule: Critical requests should have hospital name
        if request_data.urgency == "Critical" and not request_data.hospital_name:
            logger.warning(f"Critical blood request created without hospital name for patient: {request_data.patient_name}")
    
    async def _validate_blood_request_update(
        self, 
        request_update: BloodRequestUpdate, 
        existing_request: BloodRequest
    ) -> None:
        """
        Additional business logic validation for blood request updates.
        
        Args:
            request_update: BloodRequestUpdate object to validate
            existing_request: Current blood request data
            
        Raises:
            BloodRequestServiceError: If validation fails
        """
        # Additional business rules can be added here
        
        # Validate city is not empty if being updated
        if request_update.city is not None and not request_update.city.strip():
            raise BloodRequestServiceError("City cannot be empty")
        
        # Validate patient name is not empty if being updated
        if request_update.patient_name is not None and not request_update.patient_name.strip():
            raise BloodRequestServiceError("Patient name cannot be empty")
        
        # Business rule: Cannot change status from Fulfilled back to Active
        if (existing_request.status == "Fulfilled" and 
            request_update.status == "Active"):
            raise BloodRequestServiceError("Cannot reactivate a fulfilled blood request")
        
        # Business rule: Critical requests should have hospital name
        urgency_to_check = request_update.urgency or existing_request.urgency
        hospital_to_check = request_update.hospital_name or existing_request.hospital_name
        
        if urgency_to_check == "Critical" and not hospital_to_check:
            logger.warning(f"Critical blood request updated without hospital name for request ID: {existing_request.id}")