#!/usr/bin/env python3
"""
Test navigation in the wizard to reproduce the Enter key issue
"""

import sys
from pathlib import Path
import asyncio

# Add wizard to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_navigation():
    """Test the wizard navigation by simulating key presses"""
    try:
        from wizard.app import BsubWizardApp
        from textual.events import Key
        
        print("Creating BSub Wizard app...")
        app = BsubWizardApp()
        
        print("Testing action_next method directly...")
        # Test the action_next method directly
        try:
            app.action_next()
            print("✓ action_next() method works when called directly")
        except Exception as e:
            print(f"❌ action_next() failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("Testing validate_current_wizard_step method...")
        try:
            result = app.validate_current_wizard_step()
            print(f"✓ validate_current_wizard_step() returns: {result}")
        except Exception as e:
            print(f"❌ validate_current_wizard_step() failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("Testing button press handling...")
        try:
            # Simulate a button press event
            from textual.widgets import Button
            from textual.message import Message
            
            # Create a mock button pressed event
            class MockButtonPressed:
                def __init__(self, button_id):
                    self.button = type('Button', (), {'id': button_id})()
            
            # Test next button press
            mock_event = MockButtonPressed("next-button")
            app.on_button_pressed(mock_event)
            print("✓ Button press handling works")
            
        except Exception as e:
            print(f"❌ Button press handling failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Navigation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the navigation test"""
    print("=" * 60)
    print("BSub Wizard Navigation Test")
    print("=" * 60)
    
    try:
        result = asyncio.run(test_navigation())
        if result:
            print("\n✅ Navigation test passed!")
            print("\nThe Enter key issue might be related to:")
            print("1. Screen content not loading properly")
            print("2. Welcome screen content being empty or invisible")
            print("3. CSS styling issues hiding the content")
        else:
            print("\n❌ Navigation test failed!")
            return 1
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())