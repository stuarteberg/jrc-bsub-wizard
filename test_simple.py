#!/usr/bin/env python3
"""
Simple test to check the basic app structure
"""

import sys
from pathlib import Path

# Add wizard to path
sys.path.insert(0, str(Path(__file__).parent))

def test_import():
    """Test that we can import the main components"""
    try:
        from wizard.models.job_config import JobConfiguration, JobType
        from wizard.models.cluster_info import ClusterConfiguration
        from wizard.utils.command_builder import BsubCommandBuilder
        print("✓ Core modules import successfully")
        
        # Test creating the app class without running it
        from wizard.app import BsubWizardApp
        print("✓ App class imports successfully")
        
        # Try to create an instance
        app = BsubWizardApp()
        print("✓ App instance created successfully")
        
        # Try to call _validate_current_step manually
        result = app._validate_current_step()
        print(f"✓ _validate_current_step() returns: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import/creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_import():
        print("✅ Basic app structure works")
    else:
        print("❌ Basic app structure has issues")
        sys.exit(1)