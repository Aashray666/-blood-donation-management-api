from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
import re


class BloodRequest(BaseModel):
    """Pydantic model for blood request information."""
    
    id: Optional[int] = None
    patient_name: str = Field(..., min_length=1, max_length=100, description="Name of the patient")
    blood_group: str = Field(..., description="Required blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)")
    city: str = Field(..., min_length=1, max_length=100, description="City where blood is needed")
    urgency: str = Field(..., description="Urgency level (Low, Medium, High, Critical)")
    hospital_name: Optional[str] = Field(None, max_length=100, description="Hospital name (optional)")
    contact_number: str = Field(..., description="Contact phone number")
    status: str = Field(default="Active", description="Request status (Active, Fulfilled)")
    created_at: Optional[datetime] = Field(None, description="Timestamp when request was created")
    
    @validator('blood_group')
    def validate_blood_group(cls, v):
        """Validate blood group format."""
        valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
        if v not in valid_blood_groups:
            raise ValueError(f'Invalid blood group. Must be one of: {", ".join(valid_blood_groups)}')
        return v
    
    @validator('urgency')
    def validate_urgency(cls, v):
        """Validate urgency level."""
        valid_urgency_levels = {'Low', 'Medium', 'High', 'Critical'}
        if v not in valid_urgency_levels:
            raise ValueError(f'Invalid urgency level. Must be one of: {", ".join(valid_urgency_levels)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        """Validate request status."""
        valid_statuses = {'Active', 'Fulfilled'}
        if v not in valid_statuses:
            raise ValueError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
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
    
    @validator('patient_name')
    def validate_patient_name(cls, v):
        """Validate patient name contains only letters and spaces."""
        if not re.match(r'^[a-zA-Z\s]+$', v.strip()):
            raise ValueError('Patient name must contain only letters and spaces')
        return v.strip()
    
    @validator('hospital_name')
    def validate_hospital_name(cls, v):
        """Validate hospital name if provided."""
        if v is not None and v.strip():
            # Allow letters, spaces, numbers, and common punctuation for hospital names
            if not re.match(r'^[a-zA-Z0-9\s\.\-&,]+$', v.strip()):
                raise ValueError('Hospital name contains invalid characters')
            return v.strip()
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        json_schema_extra = {
            "example": {
                "patient_name": "Jane Smith",
                "blood_group": "B+",
                "city": "Delhi",
                "urgency": "High",
                "hospital_name": "City General Hospital",
                "contact_number": "9876543210"
            }
        }


class BloodRequestCreate(BaseModel):
    """Model for creating a new blood request (without id, status, and created_at)."""
    
    patient_name: str = Field(..., min_length=1, max_length=100)
    blood_group: str
    city: str = Field(..., min_length=1, max_length=100)
    urgency: str
    hospital_name: Optional[str] = Field(None, max_length=100)
    contact_number: str
    
    @validator('blood_group')
    def validate_blood_group(cls, v):
        valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
        if v not in valid_blood_groups:
            raise ValueError(f'Invalid blood group. Must be one of: {", ".join(valid_blood_groups)}')
        return v
    
    @validator('urgency')
    def validate_urgency(cls, v):
        valid_urgency_levels = {'Low', 'Medium', 'High', 'Critical'}
        if v not in valid_urgency_levels:
            raise ValueError(f'Invalid urgency level. Must be one of: {", ".join(valid_urgency_levels)}')
        return v
    
    @validator('contact_number')
    def validate_contact_number(cls, v):
        cleaned_number = re.sub(r'[\s\-\(\)]', '', v)
        if not re.match(r'^\d{10,15}$', cleaned_number):
            raise ValueError('Contact number must contain 10-15 digits')
        return v
    
    @validator('patient_name')
    def validate_patient_name(cls, v):
        if not re.match(r'^[a-zA-Z\s]+$', v.strip()):
            raise ValueError('Patient name must contain only letters and spaces')
        return v.strip()
    
    @validator('hospital_name')
    def validate_hospital_name(cls, v):
        if v is not None and v.strip():
            if not re.match(r'^[a-zA-Z0-9\s\.\-&,]+$', v.strip()):
                raise ValueError('Hospital name contains invalid characters')
            return v.strip()
        return v


class BloodRequestUpdate(BaseModel):
    """Model for updating blood request information (all fields optional)."""
    
    patient_name: Optional[str] = Field(None, min_length=1, max_length=100)
    blood_group: Optional[str] = None
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    urgency: Optional[str] = None
    hospital_name: Optional[str] = Field(None, max_length=100)
    contact_number: Optional[str] = None
    status: Optional[str] = None
    
    @validator('blood_group')
    def validate_blood_group(cls, v):
        if v is not None:
            valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
            if v not in valid_blood_groups:
                raise ValueError(f'Invalid blood group. Must be one of: {", ".join(valid_blood_groups)}')
        return v
    
    @validator('urgency')
    def validate_urgency(cls, v):
        if v is not None:
            valid_urgency_levels = {'Low', 'Medium', 'High', 'Critical'}
            if v not in valid_urgency_levels:
                raise ValueError(f'Invalid urgency level. Must be one of: {", ".join(valid_urgency_levels)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = {'Active', 'Fulfilled'}
            if v not in valid_statuses:
                raise ValueError(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
        return v
    
    @validator('contact_number')
    def validate_contact_number(cls, v):
        if v is not None:
            cleaned_number = re.sub(r'[\s\-\(\)]', '', v)
            if not re.match(r'^\d{10,15}$', cleaned_number):
                raise ValueError('Contact number must contain 10-15 digits')
        return v
    
    @validator('patient_name')
    def validate_patient_name(cls, v):
        if v is not None:
            if not re.match(r'^[a-zA-Z\s]+$', v.strip()):
                raise ValueError('Patient name must contain only letters and spaces')
            return v.strip()
        return v
    
    @validator('hospital_name')
    def validate_hospital_name(cls, v):
        if v is not None and v.strip():
            if not re.match(r'^[a-zA-Z0-9\s\.\-&,]+$', v.strip()):
                raise ValueError('Hospital name contains invalid characters')
            return v.strip()
        return v