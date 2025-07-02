#!/usr/bin/env python3
"""
Test the wizard startup by running it briefly
"""

import sys
import asyncio
from pathlib import Path

# Add wizard to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_wizard_startup():
    """Test that the wizard can start and initialize properly"""
    try:
        from wizard.app import BsubWizardApp
        
        print("Creating BSub Wizard app...")
        app = BsubWizardApp()
        
        print("Starting app briefly...")
        # Run the app for a very short time to test initialization
        await app._startup()
        print("✓ App startup completed successfully")
        
        # Test that we can access the initial screen
        print("✓ App initialized without errors")
        
        await app._shutdown()
        print("✓ App shutdown completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Wizard startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the startup test"""
    print("=" * 50)
    print("BSub Wizard Startup Test")
    print("=" * 50)
    
    try:
        result = asyncio.run(test_wizard_startup())
        if result:
            print("\n✅ Wizard startup test passed!")
            print("\nTo run the full wizard:")
            print("  pixi run start")
        else:
            print("\n❌ Wizard startup test failed!")
            return 1
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())