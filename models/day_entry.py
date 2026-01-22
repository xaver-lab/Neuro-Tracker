"""
Data model for a single day entry
"""
from datetime import datetime
from typing import List, Optional, Dict, Any


class DayEntry:
    """Represents a single day's health and food data"""

    def __init__(
        self,
        date: str,
        severity: Optional[int] = None,
        foods: Optional[List[str]] = None,
        notes: str = "",
        skin_notes: str = "",
        food_notes: str = "",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        """
        Initialize a DayEntry

        Args:
            date: Date in ISO format (YYYY-MM-DD)
            severity: Eczema severity rating (1-5)
            foods: List of food items consumed
            notes: Optional notes for the day (legacy, for backward compatibility)
            skin_notes: Notes about skin condition
            food_notes: Notes about food/nutrition
            created_at: Creation timestamp (ISO format)
            updated_at: Last update timestamp (ISO format)
        """
        self.date = date
        self.severity = severity
        self.foods = foods if foods is not None else []
        self.notes = notes
        self.skin_notes = skin_notes
        self.food_notes = food_notes

        now = datetime.now().isoformat()
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary for JSON serialization"""
        return {
            "date": self.date,
            "severity": self.severity,
            "foods": self.foods,
            "notes": self.notes,
            "skin_notes": self.skin_notes,
            "food_notes": self.food_notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DayEntry':
        """Create DayEntry from dictionary"""
        return cls(
            date=data["date"],
            severity=data.get("severity"),
            foods=data.get("foods", []),
            notes=data.get("notes", ""),
            skin_notes=data.get("skin_notes", ""),
            food_notes=data.get("food_notes", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

    def update(self, severity: Optional[int] = None, foods: Optional[List[str]] = None,
               notes: Optional[str] = None, skin_notes: Optional[str] = None,
               food_notes: Optional[str] = None):
        """Update entry data and refresh updated_at timestamp"""
        if severity is not None:
            self.severity = severity
        if foods is not None:
            self.foods = foods
        if notes is not None:
            self.notes = notes
        if skin_notes is not None:
            self.skin_notes = skin_notes
        if food_notes is not None:
            self.food_notes = food_notes

        self.updated_at = datetime.now().isoformat()

    def is_complete(self) -> bool:
        """Check if entry has all required data"""
        return self.severity is not None

    def __str__(self) -> str:
        """String representation"""
        foods_str = ", ".join(self.foods) if self.foods else "Keine"
        return f"DayEntry({self.date}, Severity: {self.severity}, Foods: {foods_str})"

    def __repr__(self) -> str:
        """Developer representation"""
        return f"DayEntry(date='{self.date}', severity={self.severity}, foods={self.foods})"
