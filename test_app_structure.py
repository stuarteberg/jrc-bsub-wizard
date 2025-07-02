#!/usr/bin/env python3
"""
Test that the app structure is correct without running the full TUI
"""

import sys
from pathlib import Path

# Add wizard to path
sys.path.insert(0, str(Path(__file__).parent))

def test_app_structure():
    """Test that the app has all required components"""
    try:
        from wizard.app import BsubWizardApp
        
        print("✓ Importing BsubWizardApp...")
        app = BsubWizardApp()
        print("✓ Creating app instance...")
        
        # Test that all required attributes exist
        assert hasattr(app, 'cluster_config'), "Missing cluster_config"
        assert hasattr(app, 'job_config'), "Missing job_config"
        assert hasattr(app, 'command_builder'), "Missing command_builder"
        assert hasattr(app, 'steps'), "Missing steps"
        print("✓ All required attributes present...")
        
        # Test that we have the right number of steps
        assert len(app.steps) == 8, f"Expected 8 steps, got {len(app.steps)}"
        print(f"✓ Correct number of wizard steps: {len(app.steps)}")
        
        # Test each step screen class can be imported
        for i, (step_name, step_class) in enumerate(app.steps):
            print(f"  Step {i+1}: {step_name} ({step_class.__name__})")
        print("✓ All wizard steps defined...")
        
        # Test action methods exist
        actions = ['action_next', 'action_back', 'action_save_config', 'action_load_config', 'action_help']
        for action in actions:
            assert hasattr(app, action), f"Missing {action}"
        print("✓ All action methods present...")
        
        # Test validation method works
        result = app.validate_current_step()
        assert isinstance(result, bool), "validate_current_step should return bool"
        print("✓ Validation method works...")
        
        # Test that we can access cluster configuration
        assert len(app.cluster_config.queues) > 0, "No queues in cluster config"
        assert len(app.cluster_config.gpus) > 0, "No GPUs in cluster config"
        print(f"✓ Cluster config loaded: {len(app.cluster_config.queues)} queues, {len(app.cluster_config.gpus)} GPU types")
        
        return True
        
    except Exception as e:
        print(f"❌ App structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the app structure test"""
    print("=" * 60)
    print("BSub Wizard Application Structure Test")
    print("=" * 60)
    
    if test_app_structure():
        print("\n" + "=" * 60)
        print("✅ Application structure test PASSED!")
        print("=" * 60)
        print("\nThe BSub Wizard is ready to run!")
        print("\nTo start the wizard:")
        print("  pixi run start")
        print("\nTo run tests:")
        print("  pixi run test")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Application structure test FAILED!")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())