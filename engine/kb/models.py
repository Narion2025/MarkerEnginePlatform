"""
Pydantic models for marker definitions.

These models mirror the JSON Schema and provide type-safe access to marker data.
"""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class MarkerSet(BaseModel):
    """
    Represents a single marker definition.
    
    Attributes:
        name: Human-readable name of the marker
        keywords: List of keywords for pattern matching
        semantic_hints: Optional semantic hints for enhanced detection
        prompt_inserts: Language-specific prompt inserts
        version: Version of the marker definition (semver format)
    """
    name: str = Field(..., min_length=1, description="Human-readable name of the marker")
    keywords: List[str] = Field(..., min_length=1, description="List of keywords for pattern matching")
    semantic_hints: List[str] = Field(default_factory=list, description="Semantic hints for enhanced detection")
    prompt_inserts: Dict[str, str] = Field(default_factory=dict, description="Language-specific prompt inserts")
    version: str = Field(..., pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$", description="Version (semver format)")
    
    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v: List[str]) -> List[str]:
        """Ensure keywords are unique and non-empty."""
        if not v:
            raise ValueError("Keywords list cannot be empty")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in v:
            if keyword and keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        if not unique_keywords:
            raise ValueError("Keywords list must contain at least one non-empty keyword")
        
        return unique_keywords
    
    @field_validator('keywords', mode='before')
    @classmethod
    def strip_keywords(cls, v: List[str]) -> List[str]:
        """Strip whitespace from keywords."""
        if isinstance(v, list):
            return [k.strip() for k in v if isinstance(k, str) and k.strip()]
        return v
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "name": "Ambivalenz-Marker",
                "keywords": ["einerseits andererseits", "ja aber", "vielleicht doch nicht"],
                "semantic_hints": ["conflicting emotions", "uncertainty"],
                "prompt_inserts": {
                    "de": "Erkenne ambivalente Aussagen",
                    "en": "Detect ambivalent statements"
                },
                "version": "1.0.0"
            }
        } 