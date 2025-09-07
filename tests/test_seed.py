


"""
Test for database seed script functionality.
"""

import pytest
import sys
from pathlib import Path

# Add the tools directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

def test_seed_script_import():
    """Test that the seed script can be imported without errors."""
    try:
        # Import the seed script to check for syntax errors
        import seed
        assert hasattr(seed, 'main')
        assert callable(seed.main)
        print("✓ Seed script imports successfully")
    except ImportError as e:
        pytest.fail(f"Seed script import failed: {e}")
    except SyntaxError as e:
        pytest.fail(f"Seed script has syntax errors: {e}")

def test_seed_functions_exist():
    """Test that the seed script has the expected functions."""
    try:
        import seed
        # Check that the main seeding function exists
        assert hasattr(seed, 'seed_database')
        assert callable(seed.seed_database)
        
        # Check that database creation function exists
        assert hasattr(seed, 'create_database_if_not_exists')
        assert callable(seed.create_database_if_not_exists)
        
        # Check that main function exists
        assert hasattr(seed, 'main')
        assert callable(seed.main)
        
        print("✓ All seed functions exist")
    except ImportError:
        pytest.skip("Seed script not available for testing")

def test_seed_data_validation():
    """Test that seed script has proper structure."""
    try:
        import seed
        
        # Check that database URLs are defined
        assert hasattr(seed, 'DATABASE_URL')
        assert hasattr(seed, 'SYNC_DATABASE_URL')
        
        # Check that imports are working
        assert 'asyncio' in dir(seed)
        assert 'uuid' in dir(seed)
        assert 'datetime' in dir(seed)
        
        print("✓ Seed script structure validation passed")
    except ImportError:
        pytest.skip("Seed script not available for testing")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


