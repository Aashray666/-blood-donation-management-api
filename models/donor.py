from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator, EmailStr
import re


class Donor(BaseModel):
    """Pydantic model for blood donor information."""
    
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the donor")
    blood_group: str = Field(..., description="Blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)")
    city: str = Field(..., min_length=1, max_length=100, description="City where donor is located")
    contact_number: str = Field(..., description="Contact phone number")
    email: Optional[EmailStr] = Field(None, description="Email address (optional)")
    created_at: Optional[datetime] = Field(None, description="Timestamp when donor was registered")
    
    @validator('blood_group')
    def validate_blood_group(cls, v):
        """Validate blood group format."""
        valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
        if v not in valid_blood_groups:
            raise ValueError(f'Invalid blood group. Must be one of: {", ".join(valid_blood_groups)}')
        return v
    
    @validator('contact_number')
    def validate_contact_number(cls, v):
        """Validate contact number format."""
        # Remove spaces and dashes for validation
        cleaned_number = re.sub(r'[\s\-\(\)]', '', v)
        
        # Check if it contains only digits and is between 10-15 characters
        if not re.match(r'^\d{10,15}$', cleaned_number):
            raise ValueError('Contact number must contain 10-15 digits')
        
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name contains only letters and spaces."""
        if not re.match(r'^[a-zA-Z\s]+$', v.strip()):
            raise ValueError('Name must contain only letters and spaces')
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "blood_group": "O+",
                "city": "Mumbai",
                "contact_number": "9876543210",
                "email": "john.doe@example.com"
            }
        }


class DonorCreate(BaseModel):
    """Model for creating a new donor (without id and created_at)."""
    
    name: str = Field(..., min_length=1, max_length=100)
    blood_group: str
    city: str = Field(..., min_length=1, max_length=100)
    contact_number: str
    email: Optional[EmailStr] = None
    
    @validator('blood_group')
    def validate_blood_group(cls, v):
        valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
        if v not in valid_blood_groups:
            raise ValueError(f'Invalid blood group. Must be one of: {", ".join(valid_blood_groups)}')
        return v
    
    @validator('contact_number')
    def validate_contact_number(cls, v):
        cleaned_number = re.sub(r'[\s\-\(\)]', '', v)
        if not re.match(r'^\d{10,15}$', cleaned_number):
            raise ValueError('Contact number must contain 10-15 digits')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if not re.match(r'^[a-zA-Z\s]+$', v.strip()):
            raise ValueError('Name must contain only letters and spaces')
        return v.strip()


class DonorUpdate(BaseModel):
    """Model for updating donor information (all fields optional)."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    blood_group: Optional[str] = None
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    contact_number: Optional[str] = None
    email: Optional[EmailStr] = None
    
    @validator('blood_group')
    def validate_blood_group(cls, v):
        if v is not None:
            valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
            if v not in valid_blood_groups:
                raise ValueError(f'Invalid blood group. Must be one of: {", ".join(valid_blood_groups)}')
        return v
    
    @validator('contact_number')
    def validate_contact_number(cls, v):
        if v is not None:
            cleaned_number = re.sub(r'[\s\-\(\)]', '', v)
            if not re.match(r'^\d{10,15}$', cleaned_number):
                raise ValueError('Contact number must contain 10-15 digits')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not re.match(r'^[a-zA-Z\s]+$', v.strip()):
                raise ValueError('Name must contain only letters and spaces')
            return v.strip()
        return v