from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import aiosqlite

from models.donor import Donor, DonorCreate, DonorUpdate
from database.connection import get_db_session

logger = logging.getLogger(__name__)


class DonorRepositoryError(Exception):
    """Custom exception for donor repository operations."""
    pass


class DonorRepository:
    """Repository class for donor data access operations."""
    
    def __init__(self, database_path: str = "blood_donation.db"):
        """
        Initialize the donor repository.
        
        Args:
            database_path: Path to the SQLite database file
        """
        self.database_path = database_path
    
    async def create(self, donor: DonorCreate) -> Donor:
        """
        Create a new donor record.
        
        Args:
            donor: DonorCreate object with donor information
            
        Returns:
            Donor: Created donor with assigned ID and timestamp
            
        Raises:
            DonorRepositoryError: If creation fails
        """
        try:
            async with get_db_session(self.database_path) as connection:
                # Insert donor record
                query = """
                INSERT INTO donors (name, blood_group, city, contact_number, email, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                created_at = datetime.now()
                params = (
                    donor.name,
                    donor.blood_group,
                    donor.city,
                    donor.contact_number,
                    donor.email,
                    created_at
                )
                
                cursor = await connection.execute(query, params)
                await connection.commit()
                
                donor_id = cursor.lastrowid
                
                # Return the created donor with ID
                return Donor(
                    id=donor_id,
                    name=donor.name,
                    blood_group=donor.blood_group,
                    city=donor.city,
                    contact_number=donor.contact_number,
                    email=donor.email,
                    created_at=created_at
                )
                
        except Exception as e:
            logger.error(f"Error creating donor: {e}")
            raise DonorRepositoryError(f"Failed to create donor: {str(e)}")
    
    async def get_by_id(self, donor_id: int) -> Optional[Donor]:
        """
        Retrieve a donor by ID.
        
        Args:
            donor_id: ID of the donor to retrieve
            
        Returns:
            Donor object if found, None otherwise
            
        Raises:
            DonorRepositoryError: If retrieval fails
        """
        try:
            async with get_db_session(self.database_path) as connection:
                query = """
                SELECT id, name, blood_group, city, contact_number, email, created_at
                FROM donors
                WHERE id = ?
                """
                
                cursor = await connection.execute(query, (donor_id,))
                row = await cursor.fetchone()
                
                if row:
                    return self._row_to_donor(row)
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving donor {donor_id}: {e}")
            raise DonorRepositoryError(f"Failed to retrieve donor: {str(e)}")
    
    async def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Donor]:
        """
        Retrieve all donors with optional filtering.
        
        Args:
            filters: Optional dictionary with filter criteria
                    - blood_group: Filter by blood group
                    - city: Filter by city
                    - limit: Maximum number of results
                    - offset: Number of results to skip
            
        Returns:
            List of Donor objects
            
        Raises:
            DonorRepositoryError: If retrieval fails
        """
        try:
            async with get_db_session(self.database_path) as connection:
                query = """
                SELECT id, name, blood_group, city, contact_number, email, created_at
                FROM donors
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
                
                return [self._row_to_donor(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error retrieving donors: {e}")
            raise DonorRepositoryError(f"Failed to retrieve donors: {str(e)}")
    
    async def update(self, donor_id: int, donor_update: DonorUpdate) -> Optional[Donor]:
        """
        Update an existing donor record.
        
        Args:
            donor_id: ID of the donor to update
            donor_update: DonorUpdate object with fields to update
            
        Returns:
            Updated Donor object if successful, None if donor not found
            
        Raises:
            DonorRepositoryError: If update fails
        """
        try:
            async with get_db_session(self.database_path) as connection:
                # First check if donor exists
                existing_donor = await self.get_by_id(donor_id)
                if not existing_donor:
                    return None
                
                # Build update query dynamically based on provided fields
                update_fields = []
                params = []
                
                update_data = donor_update.dict(exclude_unset=True)
                
                for field, value in update_data.items():
                    if value is not None:
                        update_fields.append(f"{field} = ?")
                        params.append(value)
                
                if not update_fields:
                    # No fields to update, return existing donor
                    return existing_donor
                
                query = f"""
                UPDATE donors
                SET {', '.join(update_fields)}
                WHERE id = ?
                """
                params.append(donor_id)
                
                cursor = await connection.execute(query, params)
                await connection.commit()
                
                if cursor.rowcount > 0:
                    # Return updated donor
                    return await self.get_by_id(donor_id)
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error updating donor {donor_id}: {e}")
            raise DonorRepositoryError(f"Failed to update donor: {str(e)}")
    
    async def delete(self, donor_id: int) -> bool:
        """
        Delete a donor record.
        
        Args:
            donor_id: ID of the donor to delete
            
        Returns:
            True if deletion was successful, False if donor not found
            
        Raises:
            DonorRepositoryError: If deletion fails
        """
        try:
            async with get_db_session(self.database_path) as connection:
                query = "DELETE FROM donors WHERE id = ?"
                
                cursor = await connection.execute(query, (donor_id,))
                await connection.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting donor {donor_id}: {e}")
            raise DonorRepositoryError(f"Failed to delete donor: {str(e)}")
    
    async def search_by_blood_group_and_city(self, blood_group: str, city: str) -> List[Donor]:
        """
        Search donors by blood group and city.
        
        Args:
            blood_group: Blood group to search for
            city: City to search in
            
        Returns:
            List of matching Donor objects
            
        Raises:
            DonorRepositoryError: If search fails
        """
        try:
            filters = {
                'blood_group': blood_group,
                'city': city
            }
            return await self.get_all(filters)
            
        except Exception as e:
            logger.error(f"Error searching donors by blood group {blood_group} and city {city}: {e}")
            raise DonorRepositoryError(f"Failed to search donors: {str(e)}")
    
    async def search_by_blood_group(self, blood_group: str) -> List[Donor]:
        """
        Search donors by blood group only.
        
        Args:
            blood_group: Blood group to search for
            
        Returns:
            List of matching Donor objects
            
        Raises:
            DonorRepositoryError: If search fails
        """
        try:
            filters = {'blood_group': blood_group}
            return await self.get_all(filters)
            
        except Exception as e:
            logger.error(f"Error searching donors by blood group {blood_group}: {e}")
            raise DonorRepositoryError(f"Failed to search donors: {str(e)}")
    
    async def search_by_city(self, city: str) -> List[Donor]:
        """
        Search donors by city only.
        
        Args:
            city: City to search in
            
        Returns:
            List of matching Donor objects
            
        Raises:
            DonorRepositoryError: If search fails
        """
        try:
            filters = {'city': city}
            return await self.get_all(filters)
            
        except Exception as e:
            logger.error(f"Error searching donors by city {city}: {e}")
            raise DonorRepositoryError(f"Failed to search donors: {str(e)}")
    
    async def count_donors(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count total number of donors with optional filtering.
        
        Args:
            filters: Optional dictionary with filter criteria
            
        Returns:
            Total count of donors matching the criteria
            
        Raises:
            DonorRepositoryError: If count fails
        """
        try:
            async with get_db_session(self.database_path) as connection:
                query = "SELECT COUNT(*) FROM donors"
                params = []
                where_conditions = []
                
                if filters:
                    if 'blood_group' in filters and filters['blood_group']:
                        where_conditions.append("blood_group = ?")
                        params.append(filters['blood_group'])
                    
                    if 'city' in filters and filters['city']:
                        where_conditions.append("LOWER(city) = LOWER(?)")
                        params.append(filters['city'])
                
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
                
                cursor = await connection.execute(query, params)
                result = await cursor.fetchone()
                
                return result[0] if result else 0
                
        except Exception as e:
            logger.error(f"Error counting donors: {e}")
            raise DonorRepositoryError(f"Failed to count donors: {str(e)}")
    
    def _row_to_donor(self, row: tuple) -> Donor:
        """
        Convert database row to Donor object.
        
        Args:
            row: Database row tuple
            
        Returns:
            Donor object
        """
        return Donor(
            id=row[0],
            name=row[1],
            blood_group=row[2],
            city=row[3],
            contact_number=row[4],
            email=row[5],
            created_at=datetime.fromisoformat(row[6]) if row[6] else None
        )