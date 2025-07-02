#!/usr/bin/env python3
"""
Test application startup without running the full TUI
"""

import sys
from pathlib import Path

# Add wizard to path
sys.path.insert(0, str(Path(__file__).parent))

def test_startup():
    """Test that we can create and initialize the app"""
    try:
        from wizard.app import BsubWizardApp
        print("✓ App class imported successfully")
        
        # Create an instance
        app = BsubWizardApp()
        print("✓ App instance created successfully")
        
        # Test the validate_current_step method
        result = app.validate_current_step()
        print(f"✓ validate_current_step() returns: {result}")
        
        # Test compose method (this sets up the UI structure)
        print("✓ Testing UI composition...")
        compose_result = list(app.compose())
        print(f"✓ compose() returned {len(compose_result)} widgets")
        
        # Test action methods
        print("✓ Testing action methods...")
        try:
            # These shouldn't crash even if they don't do much without a running app
            app.action_next()
            print("✓ action_next() works")
        except Exception as e:
            print(f"⚠️ action_next() error (expected): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_startup():
        print("\n✅ Application startup test passed!")
    else:
        print("\n❌ Application startup test failed!")
        sys.exit(1)