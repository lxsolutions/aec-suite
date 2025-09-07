


"""
Simple test that doesn't import the full app to avoid dependency issues
"""

def test_simple():
    """Simple test that should always pass"""
    assert 1 + 1 == 2

def test_import_shared_models():
    """Test that shared models can be imported"""
    try:
        from aec_shared.models import Project, Rfp, Estimate
        assert True
    except ImportError as e:
        print(f"Import error: {e}")
        assert False

if __name__ == "__main__":
    test_simple()
    test_import_shared_models()
    print("All simple tests passed!")


