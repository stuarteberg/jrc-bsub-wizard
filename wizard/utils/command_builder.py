from typing import List, Dict, Any
from ..models.job_config import JobConfiguration, JobType


class BsubCommandBuilder:
    """Builds bsub commands from job configurations"""
    
    def __init__(self, cluster_config: Dict[str, Any]):
        self.cluster_config = cluster_config
    
    def build_command(self, config: JobConfiguration) -> str:
        """Generate the complete bsub command from configuration"""
        parts = ["bsub"]
        
        # Job name
        if config.job_name:
            if config.array_config.enabled:
                array_spec = config.array_config.to_array_string()
                parts.append(f'-J "{config.job_name}{array_spec}"')
            else:
                parts.append(f'-J "{config.job_name}"')
        
        # Number of slots
        parts.append(f"-n {config.slots}")
        
        # Queue specification
        if config.queue:
            parts.append(f"-q {config.queue}")
        
        # GPU configuration
        if config.job_type == JobType.GPU and config.gpu_config:
            gpu_string = config.gpu_config.to_gpu_string()
            parts.append(f'-gpu "{gpu_string}"')
        
        # Runtime limits
        if config.runtime_limit:
            parts.append(f"-W {config.runtime_limit}")
        
        if config.runtime_estimate:
            parts.append(f"-We {config.runtime_estimate}")
        
        # Interactive session
        if config.job_type == JobType.INTERACTIVE:
            parts.append("-Is")
        
        # File handling
        if config.output_file:
            parts.append(f"-o {config.output_file}")
        elif not config.job_type == JobType.INTERACTIVE:
            # Default to /dev/null if no output file specified for non-interactive jobs
            parts.append("-o /dev/null")
        
        if config.error_file:
            parts.append(f"-e {config.error_file}")
        
        # Email notifications
        if config.email_on_start:
            parts.append("-B")
        
        # X11 forwarding
        if config.x11_forwarding:
            parts.append("-XF")
        
        # Working directory
        if config.working_directory:
            parts.append(f'-cwd "{config.working_directory}"')
        
        # Parallel environment (MPI)
        if config.parallel_environment:
            parts.append(f"-app {config.parallel_environment}")
        
        # Architecture requirements
        if config.architecture_requirements:
            for arch in config.architecture_requirements:
                parts.append(f'-R"select[{arch}]"')
        
        # License requirements
        if config.license_requirements:
            for license_type, count in config.license_requirements.items():
                parts.append(f'-R"rusage[{license_type}={count}]"')
        
        # Custom resource requirements
        for resource in config.custom_resources:
            parts.append(f'-R"{resource}"')
        
        # Environment variables
        for var, value in config.environment_vars.items():
            parts.append(f'-env "{var}={value}"')
        
        # Command to execute
        if config.command:
            if config.job_type == JobType.INTERACTIVE:
                # For interactive jobs, the command is usually a shell
                parts.append(config.command)
            else:
                # For batch jobs, quote the command
                parts.append(f"'{config.command}'")
        
        return " ".join(parts)
    
    def validate_configuration(self, config: JobConfiguration) -> List[str]:
        """Validate configuration and return list of warnings/errors"""
        warnings = []
        
        # Check job name
        if not config.job_name.strip():
            warnings.append("Job name is required")
        elif len(config.job_name) > 100:
            warnings.append("Job name should be shorter than 100 characters")
        
        # Check for reserved words in job name
        reserved_words = ['spark', 'janelia', 'master', 'int']
        if any(word in config.job_name.lower() for word in reserved_words):
            warnings.append(f"Job name should not contain reserved words: {', '.join(reserved_words)}")
        
        # Check slots
        if config.slots < 1:
            warnings.append("Number of slots must be at least 1")
        elif config.slots > self.cluster_config.get('max_slots_per_node', 64):
            warnings.append(f"Number of slots cannot exceed {self.cluster_config.get('max_slots_per_node', 64)}")
        
        # GPU-specific validation
        if config.job_type == JobType.GPU:
            if not config.gpu_config:
                warnings.append("GPU configuration is required for GPU jobs")
            else:
                # Check GPU slots compatibility
                if config.gpu_config.gpu_type in self.cluster_config.get('gpu_costs', {}):
                    # This would need cluster info to validate properly
                    pass
        
        # Runtime validation
        if config.runtime_limit:
            if not self._is_valid_time_format(config.runtime_limit):
                warnings.append("Runtime limit must be in format MM or HH:MM")
        
        # Queue validation
        if config.queue:
            # This would need cluster info to validate queue exists
            pass
        
        # Array job validation
        if config.array_config.enabled:
            if config.array_config.start_index > config.array_config.end_index:
                warnings.append("Array start index must be less than or equal to end index")
            if config.array_config.step < 1:
                warnings.append("Array step must be at least 1")
        
        # File path validation
        if config.output_file and not config.output_file.startswith('/'):
            warnings.append("Output file should use absolute path")
        
        if config.error_file and not config.error_file.startswith('/'):
            warnings.append("Error file should use absolute path")
        
        return warnings
    
    def _is_valid_time_format(self, time_str: str) -> bool:
        """Check if time string is in valid MM or HH:MM format"""
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) != 2:
                return False
            try:
                hours, minutes = int(parts[0]), int(parts[1])
                return 0 <= hours <= 999 and 0 <= minutes <= 59
            except ValueError:
                return False
        else:
            try:
                minutes = int(time_str)
                return 0 <= minutes <= 59999
            except ValueError:
                return False
    
    def estimate_cost(self, config: JobConfiguration) -> float:
        """Calculate estimated cost for the job"""
        if not config.runtime_limit:
            return 0.0
        
        # Parse runtime to hours
        try:
            if ':' in config.runtime_limit:
                hours, minutes = map(int, config.runtime_limit.split(':'))
                runtime_hours = hours + minutes / 60
            else:
                runtime_hours = int(config.runtime_limit) / 60
        except ValueError:
            return 0.0
        
        # CPU cost
        cpu_cost_per_slot_hour = self.cluster_config.get('cpu_cost_per_slot_hour', 0.05)
        cpu_cost = config.slots * runtime_hours * cpu_cost_per_slot_hour
        
        # GPU cost
        gpu_cost = 0.0
        if config.job_type == JobType.GPU and config.gpu_config:
            gpu_costs = self.cluster_config.get('gpu_costs', {})
            gpu_type = config.gpu_config.gpu_type or 'default'
            gpu_cost_per_hour = gpu_costs.get(gpu_type, 0.20)
            gpu_cost = config.gpu_config.num_gpus * runtime_hours * gpu_cost_per_hour
        
        # Array job multiplier
        array_multiplier = 1
        if config.array_config.enabled:
            total_tasks = (config.array_config.end_index - config.array_config.start_index + 1) // config.array_config.step
            array_multiplier = total_tasks
        
        return (cpu_cost + gpu_cost) * array_multiplier
    
    def generate_job_script(self, config: JobConfiguration) -> str:
        """Generate a complete job script with bsub command and additional setup"""
        script_lines = [
            "#!/bin/bash",
            "",
            "# Generated by BSub Wizard",
            f"# Job: {config.job_name}",
            f"# Type: {config.job_type.value}",
            "",
        ]
        
        # Add environment setup if needed
        if config.environment_vars:
            script_lines.append("# Environment variables")
            for var, value in config.environment_vars.items():
                script_lines.append(f"export {var}='{value}'")
            script_lines.append("")
        
        # Add the bsub command
        bsub_command = self.build_command(config)
        script_lines.append("# Submit job")
        script_lines.append(bsub_command)
        
        return "\n".join(script_lines)
    
    def get_example_commands(self, job_type: JobType) -> List[str]:
        """Get example commands for different job types"""
        examples = {
            JobType.CPU: [
                'bsub -J "my_cpu_job" -n 4 -o /dev/null \'python my_script.py\'',
                'bsub -J "long_job" -n 16 -W 24:00 -q local -o output.log \'./my_program\'',
            ],
            JobType.GPU: [
                'bsub -J "gpu_training" -n 12 -gpu "num=1" -q gpu_a100 -o training.log \'python train.py\'',
                'bsub -J "multi_gpu" -n 24 -gpu "num=2:nvlink=yes" -q gpu_h100 -o output.log \'python train_multi.py\'',
            ],
            JobType.INTERACTIVE: [
                'bsub -n 1 -Is /bin/bash',
                'bsub -n 4 -W 8:00 -Is -XF python',
            ],
            JobType.MPI: [
                'bsub -n 48 -app parallel-48 -J "mpi_job" -o mpi.log \'mpirun -np 48 my_mpi_program\'',
            ]
        }
        
        return examples.get(job_type, [])