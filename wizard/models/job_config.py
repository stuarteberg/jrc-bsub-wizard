from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


class JobType(Enum):
    CPU = "cpu"
    GPU = "gpu"
    INTERACTIVE = "interactive"
    MPI = "mpi"


class GPUMode(Enum):
    SHARED = "shared"
    EXCLUSIVE_PROCESS = "exclusive_process"


@dataclass
class GPUConfiguration:
    gpu_type: str = ""
    num_gpus: int = 1
    gpu_mode: GPUMode = GPUMode.EXCLUSIVE_PROCESS
    mps: bool = False
    nvlink: bool = False
    min_memory: Optional[str] = None
    j_exclusive: bool = True
    
    def to_gpu_string(self) -> str:
        """Convert GPU configuration to bsub -gpu parameter string"""
        parts = [f"num={self.num_gpus}"]
        
        if self.gpu_mode != GPUMode.EXCLUSIVE_PROCESS:
            parts.append(f"mode={self.gpu_mode.value}")
        
        if self.mps:
            parts.append("mps=yes")
        
        if not self.j_exclusive:
            parts.append("j_exclusive=no")
            
        if self.gpu_type:
            parts.append(f"gmodel={self.gpu_type}")
            
        if self.min_memory:
            parts.append(f"gmem={self.min_memory}")
            
        if self.nvlink:
            parts.append("nvlink=yes")
        
        return ":".join(parts)


@dataclass
class ArrayJobConfig:
    enabled: bool = False
    start_index: int = 1
    end_index: int = 1
    step: int = 1
    max_parallel: Optional[int] = None
    
    def to_array_string(self) -> str:
        """Convert array configuration to bsub array specification"""
        if not self.enabled:
            return ""
        
        if self.step == 1:
            array_spec = f"[{self.start_index}-{self.end_index}]"
        else:
            array_spec = f"[{self.start_index}-{self.end_index}:{self.step}]"
        
        if self.max_parallel:
            array_spec += f"%{self.max_parallel}"
        
        return array_spec


@dataclass
class JobConfiguration:
    # Basic job information
    job_type: JobType = JobType.CPU
    job_name: str = ""
    command: str = ""
    
    # Resource allocation
    slots: int = 1
    queue: str = ""
    
    # Timing
    runtime_limit: Optional[str] = None  # Format: HH:MM or MM
    runtime_estimate: Optional[str] = None
    
    # GPU configuration (if applicable)
    gpu_config: Optional[GPUConfiguration] = None
    
    # File handling
    output_file: Optional[str] = None
    error_file: Optional[str] = None
    working_directory: Optional[str] = None
    
    # Notifications and behavior
    email_notifications: bool = False
    email_on_start: bool = False
    x11_forwarding: bool = False
    
    # Array jobs
    array_config: ArrayJobConfig = field(default_factory=ArrayJobConfig)
    
    # Advanced options
    architecture_requirements: List[str] = field(default_factory=list)  # avx2, avx512
    license_requirements: Dict[str, int] = field(default_factory=dict)  # e.g., {"idl": 6}
    custom_resources: List[str] = field(default_factory=list)
    environment_vars: Dict[str, str] = field(default_factory=dict)
    
    # Application-specific
    parallel_environment: Optional[str] = None  # For MPI jobs
    
    def __post_init__(self):
        """Initialize GPU config if job type is GPU and config is None"""
        if self.job_type == JobType.GPU and self.gpu_config is None:
            self.gpu_config = GPUConfiguration()
    
    def is_valid(self) -> tuple[bool, List[str]]:
        """Validate the job configuration and return validation errors"""
        errors = []
        
        if not self.job_name.strip():
            errors.append("Job name is required")
        elif any(char in self.job_name for char in [' ', 'spark', 'janelia', 'master', 'int']):
            errors.append("Job name cannot contain spaces or reserved words (spark, janelia, master, int)")
        
        if not self.command.strip():
            errors.append("Command is required")
        
        if self.slots < 1:
            errors.append("Number of slots must be at least 1")
        elif self.slots > 64:
            errors.append("Number of slots cannot exceed 64")
        
        if self.job_type == JobType.GPU:
            if not self.gpu_config:
                errors.append("GPU configuration is required for GPU jobs")
            elif self.gpu_config.num_gpus < 1:
                errors.append("Number of GPUs must be at least 1")
        
        if self.runtime_limit:
            if not self._is_valid_time_format(self.runtime_limit):
                errors.append("Runtime limit must be in format MM or HH:MM")
        
        if self.runtime_estimate:
            if not self._is_valid_time_format(self.runtime_estimate):
                errors.append("Runtime estimate must be in format MM or HH:MM")
        
        return len(errors) == 0, errors
    
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
    
    def estimate_cost(self, cluster_config: Dict[str, Any]) -> float:
        """Estimate the cost of running this job"""
        if not self.runtime_limit:
            return 0.0
        
        # Parse runtime to hours
        if ':' in self.runtime_limit:
            hours, minutes = map(int, self.runtime_limit.split(':'))
            runtime_hours = hours + minutes / 60
        else:
            runtime_hours = int(self.runtime_limit) / 60
        
        # CPU cost
        cpu_cost_per_slot_hour = cluster_config.get('cpu_cost_per_slot_hour', 0.05)
        cpu_cost = self.slots * runtime_hours * cpu_cost_per_slot_hour
        
        # GPU cost
        gpu_cost = 0.0
        if self.job_type == JobType.GPU and self.gpu_config:
            gpu_costs = cluster_config.get('gpu_costs', {})
            gpu_type = self.gpu_config.gpu_type or 'default'
            gpu_cost_per_hour = gpu_costs.get(gpu_type, 0.20)
            gpu_cost = self.gpu_config.num_gpus * runtime_hours * gpu_cost_per_hour
        
        return cpu_cost + gpu_cost