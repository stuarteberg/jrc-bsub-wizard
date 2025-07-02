from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, RadioSet, RadioButton, Markdown
from textual.widget import Widget

from ..models.job_config import JobType, GPUConfiguration


class JobTypeScreen(Widget):
    """Screen for selecting job type"""
    
    CSS = """
    .job-type-container {
        height: 100%;
        padding: 2;
        background: $surface;
    }
    
    .section-title {
        text-align: center;
        background: $primary;
        color: $text;
        padding: 1;
        margin: 1 0;
    }
    
    .job-type-grid {
        height: auto;
        background: $surface-lighten-1;
        padding: 2;
        margin: 1 0;
        border: solid $primary;
    }
    
    .job-type-option {
        background: $surface-lighten-2;
        padding: 1;
        margin: 1 0;
        border: solid $surface-lighten-3;
    }
    
    RadioSet {
        background: transparent;
    }
    
    RadioButton {
        background: $surface-lighten-2;
        margin: 0 0 1 0;
        padding: 1;
    }
    
    RadioButton:hover {
        background: $surface-lighten-3;
    }
    
    .job-description {
        background: $surface-lighten-1;
        padding: 2;
        margin: 1 0;
        border: solid $accent;
    }
    """
    
    def __init__(self, wizard_app, job_config, cluster_config):
        super().__init__()
        self.wizard_app = wizard_app
        self.job_config = job_config
        self.cluster_config = cluster_config
    
    def compose(self) -> ComposeResult:
        """Create the job type selection layout"""
        with Container(classes="job-type-container"):
            with Vertical():
                yield Static(
                    "🎯 Step 2: Select Job Type",
                    classes="section-title"
                )
                
                yield Markdown("""
Choose the type of job you want to submit. This will determine available options in subsequent steps.
""")
                
                with Container(classes="job-type-grid"):
                    with RadioSet(id="job-type-selection"):
                        yield RadioButton(
                            "🖥️  **CPU Job** - General computation using CPU cores only",
                            value="cpu",
                            id="cpu-radio"
                        )
                        yield RadioButton(
                            "🎮 **GPU Job** - Machine learning, AI, or GPU-accelerated computation",
                            value="gpu", 
                            id="gpu-radio"
                        )
                        yield RadioButton(
                            "💻 **Interactive Session** - Command line or GUI applications",
                            value="interactive",
                            id="interactive-radio"
                        )
                        yield RadioButton(
                            "🔄 **MPI/Parallel Job** - Multi-node parallel processing",
                            value="mpi",
                            id="mpi-radio"
                        )
                
                with Container(classes="job-description", id="job-description"):
                    yield Static("Select a job type above to see details", id="description-text")
    
    def on_mount(self) -> None:
        """Initialize the screen with current job type"""
        radio_set = self.query_one("#job-type-selection", RadioSet)
        
        # Set the current selection based on job config
        if self.job_config.job_type:
            radio_set.pressed = self.job_config.job_type.value
        else:
            radio_set.pressed = "cpu"  # Default selection
        
        # Set focus to enable keyboard navigation
        radio_set.focus()
        
        # Update description
        self._update_description(radio_set.pressed)
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle job type selection changes"""
        job_type_value = event.pressed
        
        # Update job configuration
        self.job_config.job_type = JobType(job_type_value)
        
        # Initialize GPU config if switching to GPU
        if job_type_value == "gpu" and not self.job_config.gpu_config:
            self.job_config.gpu_config = GPUConfiguration()
        
        # Update description
        self._update_description(job_type_value)
        
        # Update default values based on job type
        self._update_defaults_for_job_type(job_type_value)
    
    def _update_description(self, job_type: str) -> None:
        """Update the job type description"""
        descriptions = {
            "cpu": """
**CPU Jobs** are suitable for:
- General computational tasks
- Data processing and analysis
- Single-threaded or multi-threaded applications
- Most scientific computing workloads

**Available Resources:**
- Sky Lake: 48 cores, 768GB RAM per node
- Cascade Lake: 48 cores, 768GB RAM per node  
- Sapphire Rapids: 64 cores, 1TB RAM per node

**Recommended Queues:** `local`, `short`
**Cost:** $0.05 per slot per hour
""",
            "gpu": """
**GPU Jobs** are optimized for:
- Machine learning and deep learning
- AI model training and inference
- CUDA-accelerated applications
- Computer vision and image processing

**Available GPUs:**
- **GH200**: 96GB VRAM, 72 slots ($0.80/hour)
- **H200**: 141GB VRAM, 12 slots ($0.80/hour)
- **H100**: 80GB VRAM, 12 slots ($0.50/hour)
- **A100**: 80GB VRAM, 12 slots ($0.20/hour)
- **L4**: 24GB VRAM, 8-64 slots ($0.10/hour)
- **T4**: 16GB VRAM, 48 slots ($0.10/hour)

**Recommended Queues:** `gpu_a100`, `gpu_l4`, `gpu_t4`
""",
            "interactive": """
**Interactive Sessions** provide:
- Real-time command line access
- GUI application support (with X11 forwarding)
- Development and debugging environment
- Immediate feedback and interaction

**Use Cases:**
- Testing and debugging code
- Running Jupyter notebooks
- Using IDEs like VSCode or PyCharm
- Interactive data analysis

**Limitations:**
- Maximum 8 hours by default (48 hours max)
- Limited to 96 slots per user
- Should not be used for long-running batch jobs

**Queue:** `interactive`
""",
            "mpi": """
**MPI/Parallel Jobs** enable:
- Multi-node parallel processing
- Message Passing Interface (MPI) applications
- Large-scale scientific simulations
- Distributed computing workloads

**Requirements:**
- Jobs must request slots in increments of 48
- Use `-app parallel-48` parameter
- MPI-enabled applications

**Examples:**
- Molecular dynamics simulations
- Weather modeling
- Computational fluid dynamics
- Large-scale linear algebra

**Queue:** `mpi`
"""
        }
        
        description_text = self.query_one("#description-text", Static)
        description_text.update(descriptions.get(job_type, "Unknown job type"))
    
    def _update_defaults_for_job_type(self, job_type: str) -> None:
        """Update default configuration values based on job type"""
        if job_type == "cpu":
            self.job_config.slots = 4
            self.job_config.queue = "local"
            if not self.job_config.command:
                self.job_config.command = "python my_script.py"
                
        elif job_type == "gpu":
            self.job_config.slots = 12
            self.job_config.queue = "gpu_a100"
            if not self.job_config.gpu_config:
                self.job_config.gpu_config = GPUConfiguration(
                    gpu_type="NVIDIAA100_SXM4_80GB",
                    num_gpus=1
                )
            if not self.job_config.command:
                self.job_config.command = "python train.py"
                
        elif job_type == "interactive":
            self.job_config.slots = 1
            self.job_config.queue = "interactive"
            self.job_config.runtime_limit = "8:00"
            if not self.job_config.command:
                self.job_config.command = "/bin/bash"
                
        elif job_type == "mpi":
            self.job_config.slots = 48
            self.job_config.queue = "mpi"
            self.job_config.parallel_environment = "parallel-48"
            if not self.job_config.command:
                self.job_config.command = "mpirun -np 48 my_mpi_program"
    
    def validate(self) -> bool:
        """Validate the job type selection"""
        radio_set = self.query_one("#job-type-selection", RadioSet)
        
        if not radio_set.pressed:
            self.wizard_app.show_error_message("Job Type Required", ["Please select a job type"])
            return False
        
        return True