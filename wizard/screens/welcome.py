from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button, Markdown
from textual.widget import Widget


class WelcomeScreen(Widget):
    """Welcome screen for the BSub Wizard"""
    
    CSS = """
    .welcome-container {
        height: 100%;
        padding: 2;
        background: $surface;
    }
    
    .welcome-title {
        text-align: center;
        background: $primary;
        color: $text;
        padding: 1;
        margin: 1 0;
    }
    
    .welcome-content {
        background: $surface-lighten-1;
        padding: 2;
        margin: 1 0;
        border: solid $primary;
    }
    
    .feature-list {
        background: $surface-lighten-2;
        padding: 1;
        margin: 1 0;
    }
    
    .quick-actions {
        height: auto;
        margin: 2 0;
    }
    
    Button.quick-action {
        margin: 0 1;
        min-width: 16;
    }
    """
    
    def __init__(self, app, job_config, cluster_config):
        super().__init__()
        self.app = app
        self.job_config = job_config
        self.cluster_config = cluster_config
    
    def compose(self) -> ComposeResult:
        """Create the welcome screen layout"""
        with Container(classes="welcome-container"):
            with Vertical():
                yield Static(
                    "🚀 Welcome to BSub Wizard",
                    classes="welcome-title"
                )
                
                with Container(classes="welcome-content"):
                    yield Markdown("""
# Interactive Job Submission Guide

This wizard will help you create `bsub` commands for the **Janelia Research Campus** compute cluster. 
Follow the step-by-step process to configure your job submission with all the available options.

## What You Can Do:

""")
                
                with Container(classes="feature-list"):
                    yield Markdown("""
- **Configure Job Types**: CPU, GPU, Interactive, or MPI jobs
- **Select Resources**: Cores, memory, and GPU specifications  
- **Choose Queues**: Optimized for your job requirements
- **Set Runtime Limits**: Hard limits and estimates
- **Manage Files**: Input/output file handling
- **Advanced Options**: Architecture requirements, licenses, arrays
- **Preview Command**: See the generated bsub command before submission
- **Cost Estimation**: Calculate job costs before running
""")
                
                with Container(classes="welcome-content"):
                    yield Markdown("""
## Cluster Overview:

- **CPU Nodes**: Sky Lake (48 cores), Cascade Lake (48 cores), Sapphire Rapids (64 cores)
- **GPU Options**: GH200, H200, H100, A100, L4, T4 with various memory configurations
- **Queue Types**: Interactive, local, short, and specialized GPU queues
- **Billing**: $0.05/slot/hour for CPU, $0.10-$0.80/hour for GPUs
""")
                
                with Horizontal(classes="quick-actions"):
                    yield Button("📊 Quick CPU Job", id="quick-cpu", classes="quick-action")
                    yield Button("🎮 Quick GPU Job", id="quick-gpu", classes="quick-action")
                    yield Button("💻 Interactive Session", id="quick-interactive", classes="quick-action")
                    yield Button("🔄 Load Saved Config", id="quick-load", classes="quick-action")
                
                with Container(classes="welcome-content"):
                    yield Markdown("""
## Getting Started:

1. **Choose Quick Start** (buttons above) for common configurations
2. **Use Step-by-Step Wizard** (Next button) for custom jobs
3. **Load Previous Config** if you've saved configurations before

Press **Next** to begin the wizard, or use the quick action buttons above for common job types.

**Keyboard Shortcuts**: `Enter` (Next), `Esc` (Back), `Ctrl+S` (Save), `Ctrl+L` (Load), `Q` (Quit)
""")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle quick action button presses"""
        button_id = event.button.id
        
        if button_id == "quick-cpu":
            self._setup_quick_cpu_job()
        elif button_id == "quick-gpu":
            self._setup_quick_gpu_job()
        elif button_id == "quick-interactive":
            self._setup_quick_interactive()
        elif button_id == "quick-load":
            self.app.action_load_config()
    
    def _setup_quick_cpu_job(self) -> None:
        """Set up a quick CPU job configuration"""
        from ..models.job_config import JobType
        
        self.job_config.job_type = JobType.CPU
        self.job_config.job_name = "cpu_job"
        self.job_config.slots = 4
        self.job_config.queue = "local"
        self.job_config.command = "python my_script.py"
        
        # Jump to resources screen
        self.app.current_step = 2
        self.app.show_current_step()
    
    def _setup_quick_gpu_job(self) -> None:
        """Set up a quick GPU job configuration"""
        from ..models.job_config import JobType, GPUConfiguration
        
        self.job_config.job_type = JobType.GPU
        self.job_config.job_name = "gpu_job"
        self.job_config.slots = 12
        self.job_config.queue = "gpu_a100"
        self.job_config.gpu_config = GPUConfiguration(
            gpu_type="NVIDIAA100_SXM4_80GB",
            num_gpus=1
        )
        self.job_config.command = "python train.py"
        
        # Jump to resources screen
        self.app.current_step = 2
        self.app.show_current_step()
    
    def _setup_quick_interactive(self) -> None:
        """Set up a quick interactive session configuration"""
        from ..models.job_config import JobType
        
        self.job_config.job_type = JobType.INTERACTIVE
        self.job_config.job_name = "interactive_session"
        self.job_config.slots = 1
        self.job_config.queue = "interactive"
        self.job_config.runtime_limit = "8:00"
        self.job_config.command = "/bin/bash"
        
        # Jump to runtime screen
        self.app.current_step = 4
        self.app.show_current_step()
    
    def validate(self) -> bool:
        """Validate the welcome screen (always valid)"""
        return True