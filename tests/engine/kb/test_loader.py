"""
Tests for the Knowledge Base Loader.
"""
import json
import tempfile
from pathlib import Path
from typing import Dict, List

import pytest

from engine.kb import MarkerLoadError, MarkerSet, clear_cache, load_marker_sets


@pytest.fixture
def valid_marker_data() -> Dict:
    """Return valid marker data."""
    return {
        "name": "Test-Marker",
        "keywords": ["test", "example", "sample"],
        "semanticHints": ["testing", "validation"],
        "promptInserts": {
            "de": "Test auf Deutsch",
            "en": "Test in English"
        },
        "version": "1.0.0"
    }


@pytest.fixture
def temp_marker_dir(valid_marker_data):
    """Create a temporary directory with test marker files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create a valid marker file
        marker_file = tmpdir_path / "test_marker.json"
        with open(marker_file, 'w', encoding='utf-8') as f:
            json.dump(valid_marker_data, f, indent=2)
        
        yield tmpdir_path


@pytest.fixture(autouse=True)
def clear_loader_cache():
    """Clear the loader cache before and after each test."""
    clear_cache()
    yield
    clear_cache()


class TestMarkerSet:
    """Tests for the MarkerSet model."""
    
    def test_valid_marker_creation(self, valid_marker_data):
        """Test creating a valid MarkerSet."""
        marker = MarkerSet(**valid_marker_data)
        assert marker.name == "Test-Marker"
        assert len(marker.keywords) == 3
        assert marker.version == "1.0.0"
    
    def test_keyword_validation(self):
        """Test keyword validation."""
        # Empty keywords should fail
        with pytest.raises(ValueError, match="at least 1 item"):
            MarkerSet(
                name="Test",
                keywords=[],
                version="1.0.0"
            )
    
    def test_keyword_deduplication(self):
        """Test that duplicate keywords are removed."""
        marker = MarkerSet(
            name="Test",
            keywords=["test", "test", "example", "test"],
            version="1.0.0"
        )
        assert marker.keywords == ["test", "example"]
    
    def test_keyword_stripping(self):
        """Test that keywords are stripped of whitespace."""
        marker = MarkerSet(
            name="Test",
            keywords=["  test  ", "\nexample\t", "  sample"],
            version="1.0.0"
        )
        assert marker.keywords == ["test", "example", "sample"]
    
    def test_version_validation(self):
        """Test version format validation."""
        # Invalid version format should fail
        with pytest.raises(ValueError, match="pattern"):
            MarkerSet(
                name="Test",
                keywords=["test"],
                version="1.0"  # Missing patch version
            )
    
    def test_default_values(self):
        """Test default values for optional fields."""
        marker = MarkerSet(
            name="Test",
            keywords=["test"],
            version="1.0.0"
        )
        assert marker.semantic_hints == []
        assert marker.prompt_inserts == {}


class TestLoader:
    """Tests for the load_marker_sets function."""
    
    def test_load_valid_markers(self, temp_marker_dir):
        """Test loading valid marker files."""
        markers = load_marker_sets(str(temp_marker_dir))
        assert len(markers) == 1
        assert markers[0].name == "Test-Marker"
    
    def test_load_from_path_object(self, temp_marker_dir):
        """Test loading with Path object instead of string."""
        markers = load_marker_sets(temp_marker_dir)
        assert len(markers) == 1
    
    def test_nonexistent_directory(self):
        """Test loading from non-existent directory."""
        with pytest.raises(MarkerLoadError, match="Directory not found"):
            load_marker_sets("/nonexistent/path")
    
    def test_file_instead_of_directory(self, temp_marker_dir):
        """Test loading from a file instead of directory."""
        file_path = temp_marker_dir / "test_marker.json"
        with pytest.raises(MarkerLoadError, match="Not a directory"):
            load_marker_sets(str(file_path))
    
    def test_invalid_json_file(self, temp_marker_dir):
        """Test handling of invalid JSON files."""
        invalid_file = temp_marker_dir / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("{ invalid json")
        
        # Should still load valid files
        markers = load_marker_sets(str(temp_marker_dir))
        assert len(markers) == 1  # Only the valid file
    
    def test_schema_validation_failure(self, temp_marker_dir):
        """Test handling of files that fail schema validation."""
        invalid_marker = temp_marker_dir / "invalid_schema.json"
        with open(invalid_marker, 'w') as f:
            json.dump({"name": "Missing required fields"}, f)
        
        # Should still load valid files
        markers = load_marker_sets(str(temp_marker_dir))
        assert len(markers) == 1  # Only the valid file
    
    def test_skip_hidden_files(self, temp_marker_dir, valid_marker_data):
        """Test that hidden files are skipped."""
        hidden_file = temp_marker_dir / ".hidden.json"
        with open(hidden_file, 'w') as f:
            json.dump(valid_marker_data, f)
        
        markers = load_marker_sets(str(temp_marker_dir))
        assert len(markers) == 1  # Only the non-hidden file
    
    def test_skip_non_json_files(self, temp_marker_dir, valid_marker_data):
        """Test that non-JSON files are skipped."""
        txt_file = temp_marker_dir / "readme.txt"
        with open(txt_file, 'w') as f:
            f.write("This is not a JSON file")
        
        markers = load_marker_sets(str(temp_marker_dir))
        assert len(markers) == 1  # Only the JSON file
    
    def test_cache_functionality(self, temp_marker_dir):
        """Test that results are cached."""
        # First load
        markers1 = load_marker_sets(str(temp_marker_dir))
        
        # Add another file (should be ignored due to cache)
        new_file = temp_marker_dir / "new_marker.json"
        with open(new_file, 'w') as f:
            json.dump({
                "name": "New Marker",
                "keywords": ["new"],
                "version": "1.0.0"
            }, f)
        
        # Second load should return cached result
        markers2 = load_marker_sets(str(temp_marker_dir))
        assert len(markers2) == 1  # Still only the original file
        assert markers1 is markers2  # Same object reference
        
        # Clear cache and load again
        clear_cache()
        markers3 = load_marker_sets(str(temp_marker_dir))
        assert len(markers3) == 2  # Now both files are loaded
    
    def test_empty_directory(self):
        """Test loading from empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(MarkerLoadError, match="Failed to load any markers"):
                load_marker_sets(tmpdir)
    
    def test_partial_failure_logging(self, temp_marker_dir, caplog):
        """Test that partial failures are logged as warnings."""
        # Add an invalid file
        invalid_file = temp_marker_dir / "bad.json"
        with open(invalid_file, 'w') as f:
            f.write("{}")
        
        markers = load_marker_sets(str(temp_marker_dir))
        assert len(markers) == 1
        
        # Check for warning in logs
        assert any("with 1 failures" in record.message for record in caplog.records)


class TestIntegration:
    """Integration tests with actual marker files."""
    
    def test_load_actual_markers(self):
        """Test loading the actual seed markers from kb/sets."""
        # This assumes we're running from the project root
        kb_path = Path("kb/sets")
        if not kb_path.exists():
            pytest.skip("kb/sets directory not found")
        
        markers = load_marker_sets(str(kb_path))
        assert len(markers) >= 2  # At least ambivalenz and schuld
        
        # Check specific markers
        marker_names = {m.name for m in markers}
        assert "Ambivalenz-Marker" in marker_names
        assert "Schuld-Marker" in marker_names
        
        # Verify structure
        for marker in markers:
            assert marker.name
            assert marker.keywords
            assert marker.version
            assert marker.prompt_inserts  # Should have at least 'de' and 'en' 