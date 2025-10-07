from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from models.donor import Donor, DonorCreate, DonorUpdate
from repositories.donor_repository import DonorRepository, DonorRepositoryError

logger = logging.getLogger(__name__)


class DonorServiceError(Exception):
    """Custom exception for donor service operations."""
    pass


class DonorService:
    """Service class for donor business logic and operations."""
    
    def __init__(self, donor_repository: Optional[DonorRepository] = None):
        """
        Initialize the donor service.
        
        Args:
            donor_repository: DonorRepository instance (creates default if None)
        """
        self.donor_repository = donor_repository or DonorRepository()
    
    async def create_donor(self, donor_data: DonorCreate) -> Donor:
        """
        Create a new donor with business logic validation.
        
        Args:
            donor_data: DonorCreate object with donor information
            
        Returns:
            Created Donor object
            
        Raises:
            DonorServiceError: If creation fails or validation errors occur
        """
        try:
            # Additional business logic validation
            await self._validate_donor_creation(donor_data)
            
            # Check for duplicate donors (same contact number)
            existing_donors = await self.donor_repository.get_all({
                'contact_number': donor_data.contact_number
            })
            
            if existing_donors:
                raise DonorServiceError(
                    f"Donor with contact number {donor_data.contact_number} already exists"
                )
            
            # Create the donor
            donor = await self.donor_repository.create(donor_data)
            
            logger.info(f"Successfully created donor with ID: {donor.id}")
            return donor
            
        except DonorRepositoryError as e:
            logger.error(f"Repository error creating donor: {e}")
            raise DonorServiceError(f"Failed to create donor: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating donor: {e}")
            raise DonorServiceError(f"Unexpected error: {str(e)}")
    
    async def get_donor_by_id(self, donor_id: int) -> Optional[Donor]:
        """
        Retrieve a donor by ID with business logic.
        
        Args:
            donor_id: ID of the donor to retrieve
            
        Returns:
            Donor object if found, None otherwise
            
        Raises:
            DonorServiceError: If retrieval fails
        """
        try:
            if donor_id <= 0:
                raise DonorServiceError("Donor ID must be a positive integer")
            
            donor = await self.donor_repository.get_by_id(donor_id)
            
            if donor:
                logger.debug(f"Retrieved donor with ID: {donor_id}")
            else:
                logger.debug(f"Donor with ID {donor_id} not found")
            
            return donor
            
        except DonorRepositoryError as e:
            logger.error(f"Repository error retrieving donor {donor_id}: {e}")
            raise DonorServiceError(f"Failed to retrieve donor: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving donor {donor_id}: {e}")
            raise DonorServiceError(f"Unexpected error: {str(e)}")
    
    async def get_all_donors(
        self, 
        blood_group: Optional[str] = None,
        city: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Donor]:
        """
        Retrieve all donors with filtering and pagination.
        
        Args:
            blood_group: Filter by blood group
            city: Filter by city
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of Donor objects
            
        Raises:
            DonorServiceError: If retrieval fails
        """
        try:
            # Build filters
            filters = {}
            
            if blood_group:
                # Validate blood group format
                valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
                if blood_group not in valid_blood_groups:
                    raise DonorServiceError(
                        f"Invalid blood group. Must be one of: {', '.join(valid_blood_groups)}"
                    )
                filters['blood_group'] = blood_group
            
            if city:
                filters['city'] = city.strip()
            
            if limit is not None:
                if limit <= 0:
                    raise DonorServiceError("Limit must be a positive integer")
                filters['limit'] = limit
            
            if offset is not None:
                if offset < 0:
                    raise DonorServiceError("Offset must be non-negative")
                filters['offset'] = offset
            
            donors = await self.donor_repository.get_all(filters)
            
            logger.debug(f"Retrieved {len(donors)} donors with filters: {filters}")
            return donors
            
        except DonorRepositoryError as e:
            logger.error(f"Repository error retrieving donors: {e}")
            raise DonorServiceError(f"Failed to retrieve donors: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving donors: {e}")
            raise DonorServiceError(f"Unexpected error: {str(e)}")
    
    async def update_donor(self, donor_id: int, donor_update: DonorUpdate) -> Optional[Donor]:
        """
        Update an existing donor with business logic validation.
        
        Args:
            donor_id: ID of the donor to update
            donor_update: DonorUpdate object with fields to update
            
        Returns:
            Updated Donor object if successful, None if donor not found
            
        Raises:
            DonorServiceError: If update fails or validation errors occur
        """
        try:
            if donor_id <= 0:
                raise DonorServiceError("Donor ID must be a positive integer")
            
            # Check if donor exists
            existing_donor = await self.donor_repository.get_by_id(donor_id)
            if not existing_donor:
                return None
            
            # Additional business logic validation
            await self._validate_donor_update(donor_update, existing_donor)
            
            # Check for duplicate contact number if being updated
            if donor_update.contact_number:
                existing_donors = await self.donor_repository.get_all()
                for donor in existing_donors:
                    if (donor.contact_number == donor_update.contact_number and 
                        donor.id != donor_id):
                        raise DonorServiceError(
                            f"Another donor with contact number {donor_update.contact_number} already exists"
                        )
            
            # Update the donor
            updated_donor = await self.donor_repository.update(donor_id, donor_update)
            
            if updated_donor:
                logger.info(f"Successfully updated donor with ID: {donor_id}")
            
            return updated_donor
            
        except DonorRepositoryError as e:
            logger.error(f"Repository error updating donor {donor_id}: {e}")
            raise DonorServiceError(f"Failed to update donor: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating donor {donor_id}: {e}")
            raise DonorServiceError(f"Unexpected error: {str(e)}")
    
    async def delete_donor(self, donor_id: int) -> bool:
        """
        Delete a donor with business logic checks.
        
        Args:
            donor_id: ID of the donor to delete
            
        Returns:
            True if deletion was successful, False if donor not found
            
        Raises:
            DonorServiceError: If deletion fails
        """
        try:
            if donor_id <= 0:
                raise DonorServiceError("Donor ID must be a positive integer")
            
            # Check if donor exists before deletion
            existing_donor = await self.donor_repository.get_by_id(donor_id)
            if not existing_donor:
                return False
            
            # Additional business logic checks could go here
            # (e.g., check if donor has pending donations, etc.)
            
            success = await self.donor_repository.delete(donor_id)
            
            if success:
                logger.info(f"Successfully deleted donor with ID: {donor_id}")
            
            return success
            
        except DonorRepositoryError as e:
            logger.error(f"Repository error deleting donor {donor_id}: {e}")
            raise DonorServiceError(f"Failed to delete donor: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting donor {donor_id}: {e}")
            raise DonorServiceError(f"Unexpected error: {str(e)}")
    
    async def search_donors_by_blood_group(self, blood_group: str) -> List[Donor]:
        """
        Search donors by blood group with validation.
        
        Args:
            blood_group: Blood group to search for
            
        Returns:
            List of matching Donor objects
            
        Raises:
            DonorServiceError: If search fails or validation errors occur
        """
        try:
            # Validate blood group format
            valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
            if blood_group not in valid_blood_groups:
                raise DonorServiceError(
                    f"Invalid blood group. Must be one of: {', '.join(valid_blood_groups)}"
                )
            
            donors = await self.donor_repository.search_by_blood_group(blood_group)
            
            logger.debug(f"Found {len(donors)} donors with blood group: {blood_group}")
            return donors
            
        except DonorRepositoryError as e:
            logger.error(f"Repository error searching donors by blood group {blood_group}: {e}")
            raise DonorServiceError(f"Failed to search donors: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error searching donors by blood group {blood_group}: {e}")
            raise DonorServiceError(f"Unexpected error: {str(e)}")
    
    async def search_donors_by_city(self, city: str) -> List[Donor]:
        """
        Search donors by city with validation.
        
        Args:
            city: City to search in
            
        Returns:
            List of matching Donor objects
            
        Raises:
            DonorServiceError: If search fails or validation errors occur
        """
        try:
            if not city or not city.strip():
                raise DonorServiceError("City cannot be empty")
            
            donors = await self.donor_repository.search_by_city(city.strip())
            
            logger.debug(f"Found {len(donors)} donors in city: {city}")
            return donors
            
        except DonorRepositoryError as e:
            logger.error(f"Repository error searching donors by city {city}: {e}")
            raise DonorServiceError(f"Failed to search donors: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error searching donors by city {city}: {e}")
            raise DonorServiceError(f"Unexpected error: {str(e)}")
    
    async def search_donors_by_blood_group_and_city(
        self, 
        blood_group: str, 
        city: str
    ) -> List[Donor]:
        """
        Search donors by both blood group and city with validation.
        
        Args:
            blood_group: Blood group to search for
            city: City to search in
            
        Returns:
            List of matching Donor objects
            
        Raises:
            DonorServiceError: If search fails or validation errors occur
        """
        try:
            # Validate blood group format
            valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
            if blood_group not in valid_blood_groups:
                raise DonorServiceError(
                    f"Invalid blood group. Must be one of: {', '.join(valid_blood_groups)}"
                )
            
            if not city or not city.strip():
                raise DonorServiceError("City cannot be empty")
            
            donors = await self.donor_repository.search_by_blood_group_and_city(
                blood_group, city.strip()
            )
            
            logger.debug(
                f"Found {len(donors)} donors with blood group {blood_group} in city: {city}"
            )
            return donors
            
        except DonorRepositoryError as e:
            logger.error(
                f"Repository error searching donors by blood group {blood_group} and city {city}: {e}"
            )
            raise DonorServiceError(f"Failed to search donors: {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error searching donors by blood group {blood_group} and city {city}: {e}"
            )
            raise DonorServiceError(f"Unexpected error: {str(e)}")
    
    async def get_donor_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about donors in the system.
        
        Returns:
            Dictionary with donor statistics
            
        Raises:
            DonorServiceError: If statistics retrieval fails
        """
        try:
            # Get total count
            total_donors = await self.donor_repository.count_donors()
            
            # Get count by blood group
            blood_group_stats = {}
            valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
            
            for blood_group in valid_blood_groups:
                count = await self.donor_repository.count_donors({'blood_group': blood_group})
                blood_group_stats[blood_group] = count
            
            # Get all donors to calculate city statistics
            all_donors = await self.donor_repository.get_all()
            city_stats = {}
            
            for donor in all_donors:
                city = donor.city
                city_stats[city] = city_stats.get(city, 0) + 1
            
            statistics = {
                'total_donors': total_donors,
                'blood_group_distribution': blood_group_stats,
                'city_distribution': city_stats,
                'last_updated': datetime.now().isoformat()
            }
            
            logger.debug("Generated donor statistics")
            return statistics
            
        except DonorRepositoryError as e:
            logger.error(f"Repository error generating donor statistics: {e}")
            raise DonorServiceError(f"Failed to generate statistics: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error generating donor statistics: {e}")
            raise DonorServiceError(f"Unexpected error: {str(e)}")
    
    async def _validate_donor_creation(self, donor_data: DonorCreate) -> None:
        """
        Additional business logic validation for donor creation.
        
        Args:
            donor_data: DonorCreate object to validate
            
        Raises:
            DonorServiceError: If validation fails
        """
        # Additional business rules can be added here
        # For example: age restrictions, location restrictions, etc.
        
        # Validate city is not empty after stripping
        if not donor_data.city.strip():
            raise DonorServiceError("City cannot be empty")
        
        # Validate name is not empty after stripping
        if not donor_data.name.strip():
            raise DonorServiceError("Name cannot be empty")
    
    async def _validate_donor_update(
        self, 
        donor_update: DonorUpdate, 
        existing_donor: Donor
    ) -> None:
        """
        Additional business logic validation for donor updates.
        
        Args:
            donor_update: DonorUpdate object to validate
            existing_donor: Current donor data
            
        Raises:
            DonorServiceError: If validation fails
        """
        # Additional business rules can be added here
        
        # Validate city is not empty if being updated
        if donor_update.city is not None and not donor_update.city.strip():
            raise DonorServiceError("City cannot be empty")
        
        # Validate name is not empty if being updated
        if donor_update.name is not None and not donor_update.name.strip():
            raise DonorServiceError("Name cannot be empty")