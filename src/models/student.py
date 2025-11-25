"""Student data model."""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Student:
    """
    Student data model.
    
    Represents a student record with all relevant information.
    """
    student_id: int
    full_name: str
    dob: date
    gender: str
    major: str
    class_id: str
    email: str
    phone: str
    gpa: Optional[float] = None
    credits: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    province: Optional[str] = None
    enrollment_date: Optional[date] = None
    
    # Calculated fields (will be added during analytics)
    bmi: Optional[float] = None
    age: Optional[float] = None
    z_gpa: Optional[float] = None
    z_credits: Optional[float] = None
    z_bmi: Optional[float] = None
    z_age: Optional[float] = None
    
    def __post_init__(self):
        """Validate data after initialization."""
        if self.gpa is not None and not (0.0 <= self.gpa <= 4.0):
            raise ValueError(f"GPA must be between 0.0 and 4.0, got {self.gpa}")
        
        if self.gender not in ['M', 'F']:
            raise ValueError(f"Gender must be 'M' or 'F', got {self.gender}")
    
    def calculate_bmi(self) -> Optional[float]:
        """
        Calculate BMI if height and weight are available.
        
        Returns:
            BMI value or None if data is missing
        """
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100.0
            return round(self.weight_kg / (height_m ** 2), 2)
        return None
    
    def calculate_age(self, reference_date: date) -> Optional[float]:
        """
        Calculate age in years from date of birth.
        
        Args:
            reference_date: Date to calculate age from
            
        Returns:
            Age in years (with decimals) or None
        """
        if self.dob:
            age_days = (reference_date - self.dob).days
            return round(age_days / 365.25, 2)
        return None
