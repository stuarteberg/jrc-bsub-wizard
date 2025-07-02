#!/usr/bin/env python3
"""
Quick test to check if the wizard can start without the navigation error
"""

import sys
from pathlib import Path

# Add wizard to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Quick test of the wizard startup"""
    try:
        from wizard.app import BsubWizardApp
        
        print("✓ Importing app...")
        app = BsubWizardApp()
        print("✓ Created app instance...")
        
        # Test that the method name conflict is resolved
        print("✓ Testing method name resolution...")
        result = app.validate_current_wizard_step()
        print(f"✓ validate_current_wizard_step() works: {result}")
        
        print("\n🎉 The TypeError should be fixed!")
        print("\nTo test the full wizard:")
        print("  pixi run start")
        print("\nThen try pressing Enter to navigate to the next step.")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)