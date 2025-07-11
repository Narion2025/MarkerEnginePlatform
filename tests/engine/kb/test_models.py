"""
Tests for the MarkerSet models.
"""
import pytest
from pydantic import ValidationError

from engine.kb.models import MarkerSet


class TestMarkerSetModel:
    """Tests for the MarkerSet Pydantic model."""
    
    def test_minimal_valid_marker(self):
        """Test creating a marker with minimal required fields."""
        marker = MarkerSet(
            name="Minimal Marker",
            keywords=["test"],
            version="1.0.0"
        )
        assert marker.name == "Minimal Marker"
        assert marker.keywords == ["test"]
        assert marker.version == "1.0.0"
        assert marker.semantic_hints == []
        assert marker.prompt_inserts == {}
    
    def test_full_marker(self):
        """Test creating a marker with all fields."""
        marker = MarkerSet(
            name="Full Marker",
            keywords=["test", "example"],
            semantic_hints=["hint1", "hint2"],
            prompt_inserts={"de": "Deutsch", "en": "English"},
            version="2.1.3"
        )
        assert marker.name == "Full Marker"
        assert len(marker.keywords) == 2
        assert len(marker.semantic_hints) == 2
        assert marker.prompt_inserts["de"] == "Deutsch"
        assert marker.version == "2.1.3"
    
    def test_name_validation(self):
        """Test name field validation."""
        # Empty name should fail
        with pytest.raises(ValidationError) as exc_info:
            MarkerSet(name="", keywords=["test"], version="1.0.0")
        assert "at least 1 character" in str(exc_info.value)
    
    def test_version_format(self):
        """Test version format validation."""
        # Valid versions
        valid_versions = ["0.0.0", "1.2.3", "10.20.30", "999.999.999"]
        for version in valid_versions:
            marker = MarkerSet(name="Test", keywords=["test"], version=version)
            assert marker.version == version
        
        # Invalid versions
        invalid_versions = ["1", "1.2", "1.2.3.4", "v1.2.3", "1.2.a"]
        for version in invalid_versions:
            with pytest.raises(ValidationError):
                MarkerSet(name="Test", keywords=["test"], version=version)
    
    def test_keyword_edge_cases(self):
        """Test edge cases for keyword handling."""
        # Keywords with only whitespace should be filtered out
        marker = MarkerSet(
            name="Test",
            keywords=["valid", "  ", "\t", "\n", "also valid"],
            version="1.0.0"
        )
        assert marker.keywords == ["valid", "also valid"]
        
        # Empty strings should be filtered
        marker = MarkerSet(
            name="Test",
            keywords=["valid", "", "also valid"],
            version="1.0.0"
        )
        assert marker.keywords == ["valid", "also valid"]
    
    def test_json_serialization(self):
        """Test JSON serialization/deserialization."""
        marker = MarkerSet(
            name="Test Marker",
            keywords=["test", "serialize"],
            semantic_hints=["hint"],
            prompt_inserts={"de": "Test"},
            version="1.0.0"
        )
        
        # Serialize to JSON
        json_data = marker.model_dump_json()
        assert isinstance(json_data, str)
        
        # Deserialize back
        marker2 = MarkerSet.model_validate_json(json_data)
        assert marker2 == marker
    
    def test_dict_export(self):
        """Test exporting to dictionary."""
        marker = MarkerSet(
            name="Test",
            keywords=["test"],
            version="1.0.0"
        )
        
        data = marker.model_dump()
        assert data["name"] == "Test"
        assert data["keywords"] == ["test"]
        assert data["version"] == "1.0.0"
        assert data["semantic_hints"] == []
        assert data["prompt_inserts"] == {} 