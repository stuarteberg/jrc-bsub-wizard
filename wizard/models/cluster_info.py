from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class QueueType(Enum):
    CPU = "cpu"
    GPU = "gpu"
    INTERACTIVE = "interactive"
    SPECIAL = "special"


@dataclass
class QueueInfo:
    name: str
    queue_type: QueueType
    description: str
    max_runtime: Optional[str]  # Format: HH:MM or MM
    default_runtime: Optional[str]
    max_slots_per_job: Optional[int]
    max_slots_per_user: Optional[int]
    max_jobs_per_user: Optional[int]
    cost_per_slot_hour: float
    gpu_types: List[str] = None  # For GPU queues
    special_requirements: List[str] = None
    
    @property
    def max_runtime_display(self) -> str:
        """Human-readable runtime limit"""
        if not self.max_runtime:
            return "No limit"
        
        if ':' in self.max_runtime:
            hours, minutes = self.max_runtime.split(':')
            if int(minutes) == 0:
                return f"{int(hours)} hours"
            else:
                return f"{int(hours)}h {int(minutes)}m"
        else:
            minutes = int(self.max_runtime)
            if minutes < 60:
                return f"{minutes} minutes"
            else:
                hours = minutes // 60
                remaining_minutes = minutes % 60
                if remaining_minutes == 0:
                    return f"{hours} hours"
                else:
                    return f"{hours}h {remaining_minutes}m"


@dataclass  
class GPUInfo:
    model: str
    vram_gb: int
    nodes: int
    total_gpus: int
    tflops: float
    slots_per_gpu: int
    cost_per_hour: float
    features: List[str]  # e.g., ["nvlink", "tensor_cores"]
    queue_names: List[str]  # Which queues support this GPU
    
    @property
    def display_name(self) -> str:
        """Human-readable GPU name"""
        return f"{self.model} ({self.vram_gb}GB VRAM)"


@dataclass
class NodeInfo:
    rack: str
    cpu_type: str
    cores: int
    nodes: int
    memory_gb: int
    interconnect: str
    features: List[str]


class ClusterConfiguration:
    """Central configuration for the Janelia compute cluster"""
    
    def __init__(self):
        self.queues = self._initialize_queues()
        self.gpus = self._initialize_gpus()
        self.nodes = self._initialize_nodes()
        self.general_config = self._initialize_general_config()
    
    def _initialize_queues(self) -> Dict[str, QueueInfo]:
        """Initialize queue configurations"""
        return {
            "interactive": QueueInfo(
                name="interactive",
                queue_type=QueueType.INTERACTIVE,
                description="Interactive sessions for GUI applications and testing",
                max_runtime="48:00",
                default_runtime="8:00",
                max_slots_per_job=None,
                max_slots_per_user=96,
                max_jobs_per_user=4,
                cost_per_slot_hour=0.05
            ),
            "local": QueueInfo(
                name="local",
                queue_type=QueueType.CPU,
                description="Default CPU queue for long-running jobs",
                max_runtime=None,  # 30 days
                default_runtime=None,
                max_slots_per_job=None,
                max_slots_per_user=3001,
                max_jobs_per_user=None,
                cost_per_slot_hour=0.05
            ),
            "short": QueueInfo(
                name="short",
                queue_type=QueueType.CPU,
                description="Quick jobs under 1 hour",
                max_runtime="1:00",
                default_runtime="1:00",
                max_slots_per_job=None,
                max_slots_per_user=None,
                max_jobs_per_user=None,
                cost_per_slot_hour=0.05
            ),
            "gpu_gh200": QueueInfo(
                name="gpu_gh200",
                queue_type=QueueType.GPU,
                description="GH200 Super Chip - Latest generation GPU/CPU combo",
                max_runtime=None,
                default_runtime=None,
                max_slots_per_job=72,
                max_slots_per_user=None,
                max_jobs_per_user=None,
                cost_per_slot_hour=0.05,
                gpu_types=["NVIDIAGH200_96GB"]
            ),
            "gpu_h200": QueueInfo(
                name="gpu_h200",
                queue_type=QueueType.GPU,
                description="H200 - High memory AI/ML workloads",
                max_runtime=None,
                default_runtime=None,
                max_slots_per_job=12,
                max_slots_per_user=None,
                max_jobs_per_user=None,
                cost_per_slot_hour=0.05,
                gpu_types=["NVIDIAH200_141GB"]
            ),
            "gpu_h100": QueueInfo(
                name="gpu_h100",
                queue_type=QueueType.GPU,
                description="H100 - High performance AI/ML training",
                max_runtime=None,
                default_runtime=None,
                max_slots_per_job=12,
                max_slots_per_user=None,
                max_jobs_per_user=None,
                cost_per_slot_hour=0.05,
                gpu_types=["NVIDIAH100_80GB"]
            ),
            "gpu_a100": QueueInfo(
                name="gpu_a100",
                queue_type=QueueType.GPU,
                description="A100 - Versatile GPU for training and inference",
                max_runtime=None,
                default_runtime=None,
                max_slots_per_job=12,
                max_slots_per_user=None,
                max_jobs_per_user=None,
                cost_per_slot_hour=0.05,
                gpu_types=["NVIDIAA100_SXM4_80GB"]
            ),
            "gpu_l4": QueueInfo(
                name="gpu_l4",
                queue_type=QueueType.GPU,
                description="L4 - Cost-effective inference and light training",
                max_runtime=None,
                default_runtime=None,
                max_slots_per_job=8,
                max_slots_per_user=None,
                max_jobs_per_user=None,
                cost_per_slot_hour=0.05,
                gpu_types=["TeslaL4_24GB"]
            ),
            "gpu_l4_large": QueueInfo(
                name="gpu_l4_large",
                queue_type=QueueType.GPU,
                description="L4 Large - Single GPU per node for memory-intensive tasks",
                max_runtime=None,
                default_runtime=None,
                max_slots_per_job=64,
                max_slots_per_user=None,
                max_jobs_per_user=None,
                cost_per_slot_hour=0.05,
                gpu_types=["TeslaL4_24GB"]
            ),
            "gpu_t4": QueueInfo(
                name="gpu_t4",
                queue_type=QueueType.GPU,
                description="T4 - Entry-level GPU for development and testing",
                max_runtime=None,
                default_runtime=None,
                max_slots_per_job=48,
                max_slots_per_user=None,
                max_jobs_per_user=None,
                cost_per_slot_hour=0.05,
                gpu_types=["TeslaT4_16GB"]
            ),
            "gpu_short": QueueInfo(
                name="gpu_short",
                queue_type=QueueType.GPU,
                description="Mixed GPU types for short jobs (1 hour limit)",
                max_runtime="1:00",
                default_runtime="1:00",
                max_slots_per_job=None,
                max_slots_per_user=None,
                max_jobs_per_user=None,
                cost_per_slot_hour=0.05,
                gpu_types=["TeslaT4_16GB", "TeslaL4_24GB", "NVIDIAA100_SXM4_80GB"]
            ),
            "mpi": QueueInfo(
                name="mpi",
                queue_type=QueueType.SPECIAL,
                description="Parallel/MPI jobs (48-slot increments)",
                max_runtime=None,
                default_runtime=None,
                max_slots_per_job=None,
                max_slots_per_user=None,
                max_jobs_per_user=None,
                cost_per_slot_hour=0.05,
                special_requirements=["parallel-48"]
            )
        }
    
    def _initialize_gpus(self) -> Dict[str, GPUInfo]:
        """Initialize GPU configurations"""
        return {
            "NVIDIAGH200_96GB": GPUInfo(
                model="GH200 Super Chip",
                vram_gb=96,
                nodes=1,
                total_gpus=1,
                tflops=67.0,
                slots_per_gpu=72,
                cost_per_hour=0.80,
                features=["grace_cpu", "nvlink", "tensor_cores"],
                queue_names=["gpu_gh200"]
            ),
            "NVIDIAH200_141GB": GPUInfo(
                model="H200 SXM5",
                vram_gb=141,
                nodes=8,
                total_gpus=64,
                tflops=67.0,
                slots_per_gpu=12,
                cost_per_hour=0.80,
                features=["nvlink", "tensor_cores", "transformer_engine"],
                queue_names=["gpu_h200"]
            ),
            "NVIDIAH100_80GB": GPUInfo(
                model="H100 SXM5",
                vram_gb=80,
                nodes=10,
                total_gpus=80,
                tflops=67.0,
                slots_per_gpu=12,
                cost_per_hour=0.50,
                features=["nvlink", "tensor_cores", "transformer_engine"],
                queue_names=["gpu_h100"]
            ),
            "NVIDIAA100_SXM4_80GB": GPUInfo(
                model="A100 SXM4",
                vram_gb=80,
                nodes=19,
                total_gpus=76,
                tflops=19.0,
                slots_per_gpu=12,
                cost_per_hour=0.20,
                features=["nvlink", "tensor_cores"],
                queue_names=["gpu_a100", "gpu_short"]
            ),
            "TeslaL4_24GB": GPUInfo(
                model="Tesla L4",
                vram_gb=24,
                nodes=49,  # 18 + 31
                total_gpus=175,  # 144 + 31
                tflops=30.3,
                slots_per_gpu=8,  # Default for dense nodes
                cost_per_hour=0.10,
                features=["tensor_cores", "rt_cores"],
                queue_names=["gpu_l4", "gpu_l4_large", "gpu_short"]
            ),
            "TeslaT4_16GB": GPUInfo(
                model="Tesla T4",
                vram_gb=16,
                nodes=62,
                total_gpus=62,
                tflops=8.1,
                slots_per_gpu=48,
                cost_per_hour=0.10,
                features=["tensor_cores"],
                queue_names=["gpu_t4", "gpu_short"]
            )
        }
    
    def _initialize_nodes(self) -> Dict[str, NodeInfo]:
        """Initialize node configurations"""
        return {
            "sky_lake": NodeInfo(
                rack="e10",
                cpu_type="2.7 GHz Intel Platinum 8168",
                cores=48,
                nodes=32,
                memory_gb=768,
                interconnect="25Gbit Ethernet",
                features=["avx2", "avx512"]
            ),
            "cascade_lake": NodeInfo(
                rack="h07",
                cpu_type="3.0GHz Intel Gold 6248R",
                cores=48,
                nodes=32,
                memory_gb=768,
                interconnect="25Gbit Ethernet",
                features=["avx2", "avx512"]
            ),
            "sapphire_rapids": NodeInfo(
                rack="H06",
                cpu_type="2.8GHz Intel Platinum 8462Y+",
                cores=64,
                nodes=32,
                memory_gb=1024,
                interconnect="100Gbit Ethernet",
                features=["avx2", "avx512", "amx"]
            )
        }
    
    def _initialize_general_config(self) -> Dict:
        """Initialize general cluster configuration"""
        return {
            "cpu_cost_per_slot_hour": 0.05,
            "memory_per_slot_gb": 15,
            "max_slots_per_node": 64,
            "gpu_costs": {
                "NVIDIAGH200_96GB": 0.80,
                "NVIDIAH200_141GB": 0.80,
                "NVIDIAH100_80GB": 0.50,
                "NVIDIAA100_SXM4_80GB": 0.20,
                "TeslaL4_24GB": 0.10,
                "TeslaT4_16GB": 0.10
            },
            "architecture_options": ["avx2", "avx512", "amx"],
            "license_types": ["idl", "matlab"],
            "storage_paths": {
                "groups": "/groups/...",
                "nrs": "/nrs/...",
                "scratch": "/scratch/..."
            }
        }
    
    def get_queues_for_job_type(self, job_type: str) -> List[QueueInfo]:
        """Get available queues for a specific job type"""
        if job_type == "cpu":
            return [q for q in self.queues.values() if q.queue_type in [QueueType.CPU, QueueType.INTERACTIVE]]
        elif job_type == "gpu":
            return [q for q in self.queues.values() if q.queue_type == QueueType.GPU]
        elif job_type == "interactive":
            return [q for q in self.queues.values() if q.queue_type == QueueType.INTERACTIVE]
        elif job_type == "mpi":
            return [q for q in self.queues.values() if q.queue_type == QueueType.SPECIAL]
        else:
            return list(self.queues.values())
    
    def get_gpus_for_queue(self, queue_name: str) -> List[GPUInfo]:
        """Get available GPU types for a specific queue"""
        queue = self.queues.get(queue_name)
        if not queue or not queue.gpu_types:
            return []
        
        return [gpu for gpu in self.gpus.values() if queue_name in gpu.queue_names]