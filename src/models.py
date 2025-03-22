from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import date
from enum import Enum

class TransactionType(str, Enum):
    PAYMENT = "PAYMENT"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    REFUND = "REFUND"

class TransactionStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class CustomerModel(BaseModel):
    customer_id: str
    name: str
    email: str  # Using str instead of EmailStr to avoid additional dependencies

class MetadataModel(BaseModel):
    ip_address: Optional[str] = None
    device: Optional[str] = None
    location: Optional[str] = None

class TransactionBase(BaseModel):
    transaction_id: str
    amount: float = Field(..., gt=0)
    currency: str
    transaction_type: TransactionType
    status: TransactionStatus
    date: str  # Keeping as string for simplicity
    
    @validator('date')
    def validate_date_format(cls, v):
        try:
            year, month, day = map(int, v.split('-'))
            date(year, month, day)
            return v
        except (ValueError, TypeError):
            raise ValueError('Invalid date format. Expected YYYY-MM-DD')

class TransactionNested(TransactionBase):
    """Model for nested JSON data with customer and metadata as nested objects"""
    customer: CustomerModel
    metadata: MetadataModel

class TransactionFlat(TransactionBase):
    """Model for flattened data (as would be found in CSV)"""
    customer_id: str
    customer_name: str
    customer_email: str
    ip_address: Optional[str] = None
    device: Optional[str] = None
    location: Optional[str] = None

class TransactionResponse(TransactionBase):
    """Model for API responses with all fields flattened"""
    customer_id: str
    customer_name: str
    customer_email: str
    ip_address: Optional[str] = None
    device: Optional[str] = None
    location: Optional[str] = None

    @validator('transaction_type', 'status', pre=True)
    def validate_enums(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

    class Config:
        from_attributes = True

class PaginatedTransactionResponse(BaseModel):
    """Model for paginated API responses"""
    data: List[TransactionResponse]
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    total: int