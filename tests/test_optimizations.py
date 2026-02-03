"""
Unit tests for optimizations made to the real estate engine.
"""
import pytest
from utils.amenities import detect_amenities
from utils.text import extract_bedrooms
from utils.nlp import extract_entities_from_text
from engine.features import build_dataframe


def test_amenity_detection():
    """Test centralized amenity detection utility."""
    # Test with French text
    result = detect_amenities("Appartement avec clim, piscine et garage")
    assert result["has_air_conditioning"] == True
    assert result["has_pool"] == True
    assert result["has_garage"] == True
    assert result["has_elevator"] == False
    
    # Test with empty text
    result = detect_amenities("")
    assert all(v == False for v in result.values())
    
    # Test with Arabic text
    result = detect_amenities("شقة مع مسبح")
    assert result["has_pool"] == True


def test_bedroom_extraction_with_precompiled_patterns():
    """Test bedroom extraction uses pre-compiled patterns efficiently."""
    # Test S+1 format
    assert extract_bedrooms("Appartement S+1") == 1
    assert extract_bedrooms("S 2") == 2
    
    # Test Arabic numbers
    assert extract_bedrooms("شقة غرفتين") == 2
    
    # Test French format
    assert extract_bedrooms("4 pièces") == 3  # 4 pieces = 3 bedrooms
    assert extract_bedrooms("F3") == 2  # F3 = 2 bedrooms
    
    # Test studio
    assert extract_bedrooms("studio") == 0


def test_nlp_geo_extraction_optimized():
    """Test optimized geo-mapping with pre-sorted dictionary."""
    # Test with specific location
    result = extract_entities_from_text("Appartement à La Marsa 120 m²")
    assert result["city"] == "Tunis"
    assert result["locality"] == "La Marsa"
    assert result["surface_area"] == 120
    
    # Test with multi-word location (should match longest first)
    result = extract_entities_from_text("Villa à Sidi Bou Said")
    assert result["city"] == "Tunis"
    assert result["locality"] == "Sidi Bou Said"


def test_build_dataframe_optimized():
    """Test optimized DataFrame building with single-pass merge."""
    data = {
        "surface_area": 100,
        "bedrooms_filled": 3,
        "has_air_conditioning": True,
        "city": "Tunis",
        "locality": "La Marsa"
    }
    
    df = build_dataframe(data)
    
    # Check all expected columns are present
    assert len(df) == 1
    assert df["surface_area"].iloc[0] == 100
    assert df["bedrooms_filled"].iloc[0] == 3
    assert df["has_air_conditioning"].iloc[0] == True
    assert df["city"].iloc[0] == "Tunis"
    
    # Check defaults are applied for missing columns
    assert df["has_pool"].iloc[0] == False
    assert df["photo_count"].iloc[0] == 0


def test_build_dataframe_bedroom_cap():
    """Test bedroom capping works correctly."""
    data = {"bedrooms_filled": 15}
    df = build_dataframe(data)
    assert df["bedrooms_filled"].iloc[0] == 10  # Should be capped at 10


def test_amenity_detection_consistency():
    """Test that amenity detection is consistent across different text formats."""
    texts = [
        "avec climatisation",
        "climatisé",
        "clim split",
        "air conditionné"
    ]
    
    for text in texts:
        result = detect_amenities(text)
        assert result["has_air_conditioning"] == True, f"Failed for: {text}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
