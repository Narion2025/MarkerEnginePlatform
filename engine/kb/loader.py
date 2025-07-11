"""
Knowledge Base Loader for Marker Sets.

This module provides functionality to load and validate marker definitions
from JSON files against the defined schema.
"""
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Union

import jsonschema
from pydantic import ValidationError

from engine.kb.models import MarkerSet


logger = logging.getLogger(__name__)


class MarkerLoadError(Exception):
    """Raised when a marker file cannot be loaded or validated."""
    pass


@lru_cache(maxsize=None)
def _load_schema() -> dict:
    """
    Load and cache the marker JSON schema.
    
    Returns:
        dict: The loaded JSON schema
        
    Raises:
        MarkerLoadError: If schema file cannot be found or parsed
    """
    schema_path = Path(__file__).parent.parent.parent / "kb" / "schema" / "marker.schema.json"
    
    if not schema_path.exists():
        raise MarkerLoadError(f"Schema file not found: {schema_path}")
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise MarkerLoadError(f"Invalid JSON in schema file: {e}")
    except Exception as e:
        raise MarkerLoadError(f"Failed to load schema: {e}")


def _validate_against_schema(data: dict, file_path: Path) -> None:
    """
    Validate marker data against the JSON schema.
    
    Args:
        data: The marker data to validate
        file_path: Path to the file being validated (for error messages)
        
    Raises:
        MarkerLoadError: If validation fails
    """
    schema = _load_schema()
    
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as e:
        raise MarkerLoadError(
            f"Schema validation failed for {file_path.name}: {e.message}"
        )
    except jsonschema.SchemaError as e:
        raise MarkerLoadError(f"Invalid schema: {e.message}")


def _load_single_marker(file_path: Path) -> Optional[MarkerSet]:
    """
    Load a single marker file.
    
    Args:
        file_path: Path to the marker JSON file
        
    Returns:
        MarkerSet if successfully loaded, None if file should be skipped
        
    Raises:
        MarkerLoadError: If file cannot be loaded or validated
    """
    if not file_path.suffix == '.json':
        return None
    
    if file_path.name.startswith('.'):
        # Skip hidden files
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise MarkerLoadError(f"Invalid JSON in {file_path.name}: {e}")
    except Exception as e:
        raise MarkerLoadError(f"Failed to read {file_path.name}: {e}")
    
    # Validate against schema first
    _validate_against_schema(data, file_path)
    
    # Then validate with Pydantic
    try:
        marker = MarkerSet(**data)
        logger.debug(f"Loaded marker: {marker.name} from {file_path.name}")
        return marker
    except ValidationError as e:
        raise MarkerLoadError(f"Validation failed for {file_path.name}: {e}")


@lru_cache(maxsize=None)
def load_marker_sets(root: Union[str, Path]) -> List[MarkerSet]:
    """
    Load all marker sets from the specified directory.
    
    This function lazily loads all JSON files from the given directory,
    validates them against the schema, and returns typed MarkerSet objects.
    Results are cached for subsequent calls with the same path.
    
    Args:
        root: Path to the directory containing marker JSON files
        
    Returns:
        List of validated MarkerSet objects
        
    Raises:
        MarkerLoadError: If the directory doesn't exist or markers cannot be loaded
        
    Example:
        >>> markers = load_marker_sets("kb/sets")
        >>> print(f"Loaded {len(markers)} markers")
        >>> for marker in markers:
        ...     print(f"- {marker.name}: {len(marker.keywords)} keywords")
    """
    root_path = Path(root).resolve()
    
    if not root_path.exists():
        raise MarkerLoadError(f"Directory not found: {root_path}")
    
    if not root_path.is_dir():
        raise MarkerLoadError(f"Not a directory: {root_path}")
    
    markers: List[MarkerSet] = []
    errors: List[str] = []
    
    # Iterate through all files in the directory
    for file_path in sorted(root_path.glob("*.json")):
        try:
            marker = _load_single_marker(file_path)
            if marker:
                markers.append(marker)
        except MarkerLoadError as e:
            errors.append(str(e))
            logger.error(f"Failed to load {file_path.name}: {e}")
    
    # If we have errors and no successful loads, raise an exception
    if errors and not markers:
        raise MarkerLoadError(
            f"Failed to load any markers from {root_path}. Errors: {'; '.join(errors)}"
        )
    
    # Log warnings for partial failures
    if errors:
        logger.warning(
            f"Loaded {len(markers)} markers with {len(errors)} failures from {root_path}"
        )
    else:
        logger.info(f"Successfully loaded {len(markers)} markers from {root_path}")
    
    return markers


def clear_cache() -> None:
    """Clear the loader cache. Useful for testing or reloading markers."""
    load_marker_sets.cache_clear()
    _load_schema.cache_clear()
    logger.debug("Loader cache cleared") 