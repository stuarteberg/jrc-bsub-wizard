#!/usr/bin/env python3
"""
Basic test to verify the BSub Wizard components work correctly
"""

import sys
from pathlib import Path

# Add wizard to path
sys.path.insert(0, str(Path(__file__).parent))

from wizard.models.job_config import JobConfiguration, JobType, GPUConfiguration
from wizard.models.cluster_info import ClusterConfiguration
from wizard.utils.command_builder import BsubCommandBuilder
from wizard.utils.validators import JobValidator


def test_job_configuration():
    """Test job configuration creation and validation"""
    print("Testing Job Configuration...")
    
    # Test CPU job
    cpu_job = JobConfiguration(
        job_type=JobType.CPU,
        job_name="test_cpu_job",
        command="python script.py",
        slots=4,
        queue="local",
        runtime_limit="2:00"
    )
    
    is_valid, errors = cpu_job.is_valid()
    assert is_valid, f"CPU job validation failed: {errors}"
    print("✓ CPU job configuration valid")
    
    # Test GPU job
    gpu_job = JobConfiguration(
        job_type=JobType.GPU,
        job_name="test_gpu_job",
        command="python train.py",
        slots=12,
        queue="gpu_a100",
        runtime_limit="4:00",
        gpu_config=GPUConfiguration(
            gpu_type="NVIDIAA100_SXM4_80GB",
            num_gpus=1
        )
    )
    
    is_valid, errors = gpu_job.is_valid()
    assert is_valid, f"GPU job validation failed: {errors}"
    print("✓ GPU job configuration valid")


def test_cluster_configuration():
    """Test cluster configuration loading"""
    print("Testing Cluster Configuration...")
    
    cluster = ClusterConfiguration()
    
    # Test queue access
    assert len(cluster.queues) > 0, "No queues configured"
    assert "local" in cluster.queues, "Local queue not found"
    assert "gpu_a100" in cluster.queues, "GPU A100 queue not found"
    print("✓ Cluster queues loaded")
    
    # Test GPU access
    assert len(cluster.gpus) > 0, "No GPUs configured"
    assert "NVIDIAA100_SXM4_80GB" in cluster.gpus, "A100 GPU not found"
    print("✓ GPU configurations loaded")
    
    # Test queue filtering
    cpu_queues = cluster.get_queues_for_job_type("cpu")
    gpu_queues = cluster.get_queues_for_job_type("gpu")
    
    assert len(cpu_queues) > 0, "No CPU queues found"
    assert len(gpu_queues) > 0, "No GPU queues found"
    print("✓ Queue filtering works")


def test_command_builder():
    """Test bsub command generation"""
    print("Testing Command Builder...")
    
    cluster = ClusterConfiguration()
    builder = BsubCommandBuilder(cluster.general_config)
    
    # Test CPU command
    cpu_job = JobConfiguration(
        job_type=JobType.CPU,
        job_name="test_cpu",
        command="echo hello",
        slots=4,
        queue="local",
        runtime_limit="1:00",
        output_file="/dev/null"
    )
    
    cpu_command = builder.build_command(cpu_job)
    expected_parts = ["bsub", "-J", "test_cpu", "-n", "4", "-q", "local", "-W", "1:00", "-o", "/dev/null", "echo hello"]
    
    for part in expected_parts:
        assert part in cpu_command, f"Missing '{part}' in CPU command: {cpu_command}"
    print("✓ CPU command generation works")
    
    # Test GPU command
    gpu_job = JobConfiguration(
        job_type=JobType.GPU,
        job_name="test_gpu",
        command="python train.py",
        slots=12,
        queue="gpu_a100",
        runtime_limit="2:00",
        gpu_config=GPUConfiguration(
            gpu_type="NVIDIAA100_SXM4_80GB",
            num_gpus=1
        ),
        output_file="/dev/null"
    )
    
    gpu_command = builder.build_command(gpu_job)
    expected_gpu_parts = ["bsub", "-J", "test_gpu", "-n", "12", "-q", "gpu_a100", "-gpu", "num=1", "-W", "2:00"]
    
    for part in expected_gpu_parts:
        assert part in gpu_command, f"Missing '{part}' in GPU command: {gpu_command}"
    print("✓ GPU command generation works")
    
    # Test cost estimation
    cost = builder.estimate_cost(gpu_job)
    assert cost > 0, f"Cost estimation failed: {cost}"
    print(f"✓ Cost estimation works: ${cost:.2f}")


def test_validators():
    """Test input validation"""
    print("Testing Validators...")
    
    # Test job name validation
    valid, error = JobValidator.validate_job_name("valid_job_name")
    assert valid, f"Valid job name rejected: {error}"
    
    valid, error = JobValidator.validate_job_name("invalid job name")  # has space
    assert not valid, "Invalid job name (with space) was accepted"
    
    valid, error = JobValidator.validate_job_name("spark_job")  # reserved word
    assert not valid, "Invalid job name (reserved word) was accepted"
    print("✓ Job name validation works")
    
    # Test time format validation
    valid, error = JobValidator.validate_time_format("1:30")
    assert valid, f"Valid time format rejected: {error}"
    
    valid, error = JobValidator.validate_time_format("90")
    assert valid, f"Valid time format (minutes) rejected: {error}"
    
    valid, error = JobValidator.validate_time_format("invalid")
    assert not valid, "Invalid time format was accepted"
    print("✓ Time format validation works")
    
    # Test slots validation
    valid, error = JobValidator.validate_slots(8)
    assert valid, f"Valid slot count rejected: {error}"
    
    valid, error = JobValidator.validate_slots(0)
    assert not valid, "Invalid slot count (0) was accepted"
    
    valid, error = JobValidator.validate_slots(100)
    assert not valid, "Invalid slot count (too high) was accepted"
    print("✓ Slots validation works")


def main():
    """Run all tests"""
    print("=" * 60)
    print("BSub Wizard - Basic Component Tests")
    print("=" * 60)
    
    try:
        test_job_configuration()
        print()
        
        test_cluster_configuration()
        print()
        
        test_command_builder()
        print()
        
        test_validators()
        print()
        
        print("=" * 60)
        print("🎉 All tests passed! BSub Wizard components are working correctly.")
        print("=" * 60)
        print()
        print("To run the full application:")
        print("  python main.py")
        print()
        print("Example commands that would be generated:")
        
        # Show example commands
        cluster = ClusterConfiguration()
        builder = BsubCommandBuilder(cluster.general_config)
        
        cpu_example = JobConfiguration(
            job_type=JobType.CPU,
            job_name="my_analysis",
            command="python analyze_data.py",
            slots=8,
            queue="local",
            runtime_limit="4:00"
        )
        print(f"CPU Job: {builder.build_command(cpu_example)}")
        
        gpu_example = JobConfiguration(
            job_type=JobType.GPU,
            job_name="ml_training",
            command="python train_model.py",
            slots=12,
            queue="gpu_a100",
            runtime_limit="12:00",
            gpu_config=GPUConfiguration(gpu_type="NVIDIAA100_SXM4_80GB", num_gpus=1)
        )
        print(f"GPU Job: {builder.build_command(gpu_example)}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())