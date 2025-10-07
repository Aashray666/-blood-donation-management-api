from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import aiosqlite

from models.blood_request import BloodRequest, BloodRequestCreate, BloodRequestUpdate
from database.connection import get_db_session

logger = logging.getLogger(__name__)


class BloodRequestRepositoryError(Exception):
    """Custom exception for blood request repository operations."""
    pass


class BloodRequestRepository:
    """Repository class for blood request data access operations."""
    
    def __init__(self, database_path: str = "blood_donation.db"):
        """
        Initialize the blood request repository.
        
        Args:
            database_path: Path to the SQLite database file
        """
        self.database_path = database_path
    
    async def create(self, blood_request: BloodRequestCreate) -> BloodRequest:
        """
        Create a new blood request record.
        
        Args:
            blood_request: BloodRequestCreate object with request information
            
        Returns:
            BloodRequest: Created blood request with assigned ID and timestamp
            
        Raises:
            BloodRequestRepositoryError: If creation fails
        """
        try:
            async with get_db_session(self.database_path) as connection:
                # Insert blood request record
                query = """
                INSERT INTO blood_requests (patient_name, blood_group, city, urgency, 
                                          hospital_name, contact_number, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                created_at = datetime.now()
                params = (
                    blood_request.patient_name,
                    blood_request.blood_group,
                    blood_request.city,
                    blood_request.urgency,
                    blood_request.hospital_name,
                    blood_request.contact_number,
                    "Active",  # Default status
                    created_at
                )
                
                cursor = await connection.execute(query, params)
                await connection.commit()
                
                request_id = cursor.lastrowid
                
                # Return the created blood request with ID
                return BloodRequest(
                    id=request_id,
                    patient_name=blood_request.patient_name,
                    blood_group=blood_request.blood_group,
                    city=blood_request.city,
                    urgency=blood_request.urgency,
                    hospital_name=blood_request.hospital_name,
                    contact_number=blood_request.contact_number,
                    status="Active",
                    created_at=created_at
                )
                
        except Exception as e:
            logger.error(f"Error creating blood request: {e}")
            raise BloodRequestRepositoryError(f"Failed to create blood request: {str(e)}")
    
    async def get_by_id(self, request_id: int) -> Optional[BloodRequest]:
        """
        Retrieve a blood request by ID.
        
        Args:
            request_id: ID of the blood request to retrieve
            
        Returns:
            BloodRequest object if found, None otherwise
            
        Raises:
            BloodRequestRepositoryError: If retrieval fails
        """
        try:
            async with get_db_session(self.database_path) as connection:
                query = """
                SELECT id, patient_name, blood_group, city, urgency, hospital_name, 
                       contact_number, status, created_at
                FROM blood_requests
                WHERE id = ?
                """
                
                cursor = await connection.execute(query, (request_id,))
                row = await cursor.fetchone()
                
                if row:
                    return self._row_to_blood_request(row)
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving blood request {request_id}: {e}")
            raise BloodRequestRepositoryError(f"Failed to retrieve blood request: {str(e)}")
    
    async def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[BloodRequest]:
        """
        Retrieve all blood requests with optional filtering.
        
        Args:
            filters: Optional dictionary with filter criteria
                    - blood_group: Filter by blood group
                    - city: Filter by city
                    - urgency: Filter by urgency level
                    - status: Filter by status
                    - limit: Maximum number of results
                    - offset: Number of results to skip
            
        Returns:
            List of BloodRequest objects
            
        Raises:
            BloodRequestRepositoryError: If retrieval fails
        """
        try:
            async with get_db_session(self.database_path) as connection:
                query = """
                SELECT id, patient_name, blood_group, city, urgency, hospital_name, 
                       contact_number, status, created_at
                FROM blood_requests
                """
                params = []
                where_conditions = []
                
                if filters:
                    if 'blood_group' in filters and filters['blood_group']:
                        where_conditions.append("blood_group = ?")
                        params.append(filters['blood_group'])
                    
                    if 'city' in filters and filters['city']:
                        where_conditions.append("LOWER(city) = LOWER(?)")
                        params.append(filters['city'])
                    
                    if 'urgency' in filters and filters['urgency']:
                        where_conditions.append("urgency = ?")
                        params.append(filters['urgency'])
                    
                    if 'status' in filters and filters['status']:
                        where_conditions.append("status = ?")
                        params.append(filters['status'])
                
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
                
                query += " ORDER BY created_at DESC"
                
                # Add pagination if specified
                if filters and 'limit' in filters:
                    query += " LIMIT ?"
                    params.append(filters['limit'])
                    
                    if 'offset' in filters:
                        query += " OFFSET ?"
                        params.append(filters['offset'])
                
                cursor = await connection.execute(query, params)
                rows = await cursor.fetchall()
                
                return [self._row_to_blood_request(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error retrieving blood requests: {e}")
            raise BloodRequestRepositoryError(f"Failed to retrieve blood requests: {str(e)}")
    
    async def update(self, request_id: int, request_update: BloodRequestUpdate) -> Optional[BloodRequest]:
        """
        Update an existing blood request record.
        
        Args:
            request_id: ID of the blood request to update
            request_update: BloodRequestUpdate object with fields to update
            
        Returns:
            Updated BloodRequest object if successful, None if request not found
            
        Raises:
            BloodRequestRepositoryError: If update fails
        """
        try:
            async with get_db_session(self.database_path) as connection:
                # First check if blood request exists
                existing_request = await self.get_by_id(request_id)
                if not existing_request:
                    return None
                
                # Build update query dynamically based on provided fields
                update_fields = []
                params = []
                
                update_data = request_update.dict(exclude_unset=True)
                
                for field, value in update_data.items():
                    if value is not None:
                        update_fields.append(f"{field} = ?")
                        params.append(value)
                
                if not update_fields:
                    # No fields to update, return existing request
                    return existing_request
                
                query = f"""
                UPDATE blood_requests
                SET {', '.join(update_fields)}
                WHERE id = ?
                """
                params.append(request_id)
                
                cursor = await connection.execute(query, params)
                await connection.commit()
                
                if cursor.rowcount > 0:
                    # Return updated blood request
                    return await self.get_by_id(request_id)
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error updating blood request {request_id}: {e}")
            raise BloodRequestRepositoryError(f"Failed to update blood request: {str(e)}")
    
    async def delete(self, request_id: int) -> bool:
        """
        Delete a blood request record.
        
        Args:
            request_id: ID of the blood request to delete
            
        Returns:
            True if deletion was successful, False if request not found
            
        Raises:
            BloodRequestRepositoryError: If deletion fails
        """
        try:
            async with get_db_session(self.database_path) as connection:
                query = "DELETE FROM blood_requests WHERE id = ?"
                
                cursor = await connection.execute(query, (request_id,))
                await connection.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting blood request {request_id}: {e}")
            raise BloodRequestRepositoryError(f"Failed to delete blood request: {str(e)}")
    
    async def get_active_requests(self) -> List[BloodRequest]:
        """
        Retrieve all active blood requests.
        
        Returns:
            List of active BloodRequest objects
            
        Raises:
            BloodRequestRepositoryError: If retrieval fails
        """
        try:
            filters = {'status': 'Active'}
            return await self.get_all(filters)
            
        except Exception as e:
            logger.error(f"Error retrieving active blood requests: {e}")
            raise BloodRequestRepositoryError(f"Failed to retrieve active blood requests: {str(e)}")
    
    async def get_requests_by_urgency(self, urgency: str) -> List[BloodRequest]:
        """
        Retrieve blood requests by urgency level.
        
        Args:
            urgency: Urgency level to filter by
            
        Returns:
            List of BloodRequest objects with specified urgency
            
        Raises:
            BloodRequestRepositoryError: If retrieval fails
        """
        try:
            filters = {'urgency': urgency}
            return await self.get_all(filters)
            
        except Exception as e:
            logger.error(f"Error retrieving blood requests by urgency {urgency}: {e}")
            raise BloodRequestRepositoryError(f"Failed to retrieve blood requests by urgency: {str(e)}")
    
    async def get_requests_by_blood_group_and_city(self, blood_group: str, city: str) -> List[BloodRequest]:
        """
        Retrieve blood requests by blood group and city.
        
        Args:
            blood_group: Blood group to filter by
            city: City to filter by
            
        Returns:
            List of matching BloodRequest objects
            
        Raises:
            BloodRequestRepositoryError: If retrieval fails
        """
        try:
            filters = {
                'blood_group': blood_group,
                'city': city
            }
            return await self.get_all(filters)
            
        except Exception as e:
            logger.error(f"Error retrieving blood requests by blood group {blood_group} and city {city}: {e}")
            raise BloodRequestRepositoryError(f"Failed to retrieve blood requests: {str(e)}")
    
    async def fulfill_request(self, request_id: int) -> Optional[BloodRequest]:
        """
        Mark a blood request as fulfilled.
        
        Args:
            request_id: ID of the blood request to fulfill
            
        Returns:
            Updated BloodRequest object if successful, None if request not found
            
        Raises:
            BloodRequestRepositoryError: If fulfillment fails
        """
        try:
            update_data = BloodRequestUpdate(status="Fulfilled")
            return await self.update(request_id, update_data)
            
        except Exception as e:
            logger.error(f"Error fulfilling blood request {request_id}: {e}")
            raise BloodRequestRepositoryError(f"Failed to fulfill blood request: {str(e)}")
    
    async def count_requests(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count total number of blood requests with optional filtering.
        
        Args:
            filters: Optional dictionary with filter criteria
            
        Returns:
            Total count of blood requests matching the criteria
            
        Raises:
            BloodRequestRepositoryError: If count fails
        """
        try:
            async with get_db_session(self.database_path) as connection:
                query = "SELECT COUNT(*) FROM blood_requests"
                params = []
                where_conditions = []
                
                if filters:
                    if 'blood_group' in filters and filters['blood_group']:
                        where_conditions.append("blood_group = ?")
                        params.append(filters['blood_group'])
                    
                    if 'city' in filters and filters['city']:
                        where_conditions.append("LOWER(city) = LOWER(?)")
                        params.append(filters['city'])
                    
                    if 'urgency' in filters and filters['urgency']:
                        where_conditions.append("urgency = ?")
                        params.append(filters['urgency'])
                    
                    if 'status' in filters and filters['status']:
                        where_conditions.append("status = ?")
                        params.append(filters['status'])
                
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
                
                cursor = await connection.execute(query, params)
                result = await cursor.fetchone()
                
                return result[0] if result else 0
                
        except Exception as e:
            logger.error(f"Error counting blood requests: {e}")
            raise BloodRequestRepositoryError(f"Failed to count blood requests: {str(e)}")
    
    def _row_to_blood_request(self, row: tuple) -> BloodRequest:
        """
        Convert database row to BloodRequest object.
        
        Args:
            row: Database row tuple
            
        Returns:
            BloodRequest object
        """
        return BloodRequest(
            id=row[0],
            patient_name=row[1],
            blood_group=row[2],
            city=row[3],
            urgency=row[4],
            hospital_name=row[5],
            contact_number=row[6],
            status=row[7],
            created_at=datetime.fromisoformat(row[8]) if row[8] else None
        )