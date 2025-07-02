#!/usr/bin/env python3
"""
Diagnostic script for the BSub Wizard
"""

import sys
import os
from pathlib import Path

# Add wizard to path
sys.path.insert(0, str(Path(__file__).parent))

def check_terminal_compatibility():
    """Check if terminal supports the wizard"""
    print("🔍 Terminal Compatibility Check")
    print("-" * 40)
    
    # Check terminal size
    try:
        size = os.get_terminal_size()
        print(f"✓ Terminal size: {size.columns}x{size.lines}")
        if size.columns < 80 or size.lines < 24:
            print("⚠️  Warning: Terminal is small, recommended: 80x24 or larger")
    except:
        print("❌ Could not detect terminal size")
    
    # Check environment variables
    term = os.environ.get('TERM', 'unknown')
    print(f"✓ TERM: {term}")
    
    colorterm = os.environ.get('COLORTERM', 'none')
    print(f"✓ COLORTERM: {colorterm}")
    
    # Check if running in a proper terminal
    if not sys.stdout.isatty():
        print("⚠️  Warning: Not running in a TTY")
    else:
        print("✓ Running in TTY")

def test_wizard_components():
    """Test wizard components without UI"""
    print("\n🧪 Component Tests")
    print("-" * 40)
    
    try:
        from wizard.models.job_config import JobConfiguration, JobType
        print("✓ Job configuration imports")
        
        from wizard.models.cluster_info import ClusterConfiguration
        print("✓ Cluster configuration imports")
        
        from wizard.utils.command_builder import BsubCommandBuilder
        print("✓ Command builder imports")
        
        from wizard.app import BsubWizardApp
        print("✓ Main app imports")
        
        # Test app creation
        app = BsubWizardApp()
        print("✓ App instance created")
        
        # Test the fixed method
        result = app.validate_current_wizard_step()
        print(f"✓ Validation method works: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def create_sample_command():
    """Create a sample bsub command to show functionality"""
    print("\n🚀 Sample Command Generation")
    print("-" * 40)
    
    try:
        from wizard.models.job_config import JobConfiguration, JobType, GPUConfiguration
        from wizard.models.cluster_info import ClusterConfiguration
        from wizard.utils.command_builder import BsubCommandBuilder
        
        cluster = ClusterConfiguration()
        builder = BsubCommandBuilder(cluster.general_config)
        
        # Create sample CPU job
        cpu_job = JobConfiguration(
            job_type=JobType.CPU,
            job_name="sample_analysis",
            command="python analyze_data.py",
            slots=8,
            queue="local",
            runtime_limit="4:00",
            output_file="/groups/mylab/output.log"
        )
        
        cpu_command = builder.build_command(cpu_job)
        print("📝 Sample CPU Job Command:")
        print(f"   {cpu_command}")
        
        # Create sample GPU job
        gpu_job = JobConfiguration(
            job_type=JobType.GPU,
            job_name="ml_training",
            command="python train_model.py",
            slots=12,
            queue="gpu_a100",
            runtime_limit="8:00",
            gpu_config=GPUConfiguration(
                gpu_type="NVIDIAA100_SXM4_80GB",
                num_gpus=1
            ),
            output_file="/groups/mylab/training.log"
        )
        
        gpu_command = builder.build_command(gpu_job)
        print("\n🎮 Sample GPU Job Command:")
        print(f"   {gpu_command}")
        
        # Cost estimation
        cost = builder.estimate_cost(gpu_job)
        print(f"\n💰 Estimated Cost: ${cost:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample command generation failed: {e}")
        return False

def main():
    """Run full diagnostic"""
    print("=" * 60)
    print("🔧 BSub Wizard Diagnostic Tool")
    print("=" * 60)
    
    # Run checks
    check_terminal_compatibility()
    
    components_ok = test_wizard_components()
    
    if components_ok:
        create_sample_command()
    
    print("\n" + "=" * 60)
    
    if components_ok:
        print("✅ DIAGNOSIS: Wizard components are working correctly!")
        print("\n🎯 The TypeError issue has been resolved.")
        print("\n📋 Recommendations:")
        print("1. Clear your terminal: type 'clear' and press Enter")
        print("2. Try the wizard again: pixi run start")
        print("3. If you see control characters, try a different terminal")
        print("4. Use keyboard navigation: Enter (next), Esc (back), Q (quit)")
        
        print("\n🔗 Alternative Usage:")
        print("If the interactive wizard has issues, you can:")
        print("- Use the generated commands above as templates")
        print("- Modify the job configuration in Python scripts")
        print("- Generate commands programmatically")
        
    else:
        print("❌ DIAGNOSIS: Issues found with wizard components")
        print("Please check the error messages above.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()