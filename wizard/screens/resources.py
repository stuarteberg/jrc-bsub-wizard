from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.widgets import Static, Input, Select, Checkbox, Markdown
from textual.widget import Widget
from textual.validation import Integer, Number

from ..models.job_config import JobType
from ..utils.validators import JobValidator


class ResourcesScreen(Widget):
    """Screen for configuring resource allocation"""
    
    CSS = """
    .resources-container {
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
    
    .resource-section {
        background: $surface-lighten-1;
        padding: 2;
        margin: 1 0;
        border: solid $primary;
    }
    
    .gpu-section {
        background: $surface-lighten-1;
        padding: 2;
        margin: 1 0;
        border: solid $accent;
    }
    
    .resource-grid {
        height: auto;
        grid-size: 2 3;
        grid-gutter: 1;
    }
    
    .gpu-grid {
        height: auto;
        grid-size: 2 2;
        grid-gutter: 1;
    }
    
    .resource-item {
        background: $surface-lighten-2;
        padding: 1;
        border: solid $surface-lighten-3;
    }
    
    .estimate-section {
        background: $surface-darken-1;
        color: $text;
        padding: 1;
        margin: 1 0;
        border: solid $warning;
    }
    
    Input {
        margin: 0 0 1 0;
    }
    
    Select {
        margin: 0 0 1 0;
    }
    """
    
    def __init__(self, wizard_app, job_config, cluster_config):
        super().__init__()
        self.wizard_app = wizard_app
        self.job_config = job_config
        self.cluster_config = cluster_config
    
    def compose(self) -> ComposeResult:
        """Create the resource configuration layout"""
        with Container(classes="resources-container"):
            with Vertical():
                yield Static(
                    "⚙️ Step 3: Configure Resources",
                    classes="section-title"
                )
                
                yield Markdown("""
Configure the computational resources for your job. Resource allocation affects cost and scheduling priority.
""")
                
                # CPU/General Resources
                with Container(classes="resource-section"):
                    yield Static("💻 **CPU Resources**", classes="subsection-title")
                    
                    with Grid(classes="resource-grid"):
                        with Container(classes="resource-item"):
                            yield Static("Number of Slots (CPU cores):")
                            yield Input(
                                placeholder="1-64",
                                validators=[Integer(minimum=1, maximum=64)],
                                id="slots-input"
                            )
                            yield Static("💡 1 slot = 1 CPU core + 15GB RAM", classes="help-text")
                        
                        with Container(classes="resource-item"):
                            yield Static("Memory per Slot:")
                            yield Static("15 GB (fixed)", classes="info-text")
                            yield Static("Total memory calculated automatically", classes="help-text")
                        
                        with Container(classes="resource-item"):
                            yield Static("Architecture Preference:")
                            yield Select([
                                ("Any (recommended)", "any"),
                                ("AVX2 compatible", "avx2"),
                                ("AVX512 compatible", "avx512"),
                                ("AMX compatible (Sapphire Rapids)", "amx")
                            ], id="arch-select")
                            yield Static("💡 'Any' provides fastest scheduling", classes="help-text")
                
                # GPU Resources (shown only for GPU jobs)
                with Container(classes="gpu-section", id="gpu-resources"):
                    yield Static("🎮 **GPU Resources**", classes="subsection-title")
                    
                    with Grid(classes="gpu-grid"):
                        with Container(classes="resource-item"):
                            yield Static("GPU Type:")
                            yield Select([("Loading...", "")], id="gpu-type-select")
                            yield Static("💡 A100 recommended for most ML tasks", classes="help-text")
                        
                        with Container(classes="resource-item"):
                            yield Static("Number of GPUs:")
                            yield Input(
                                placeholder="1-8",
                                validators=[Integer(minimum=1, maximum=8)],
                                id="gpu-count-input"
                            )
                            yield Static("💡 Most jobs work well with 1 GPU", classes="help-text")
                        
                        with Container(classes="resource-item"):
                            yield Static("GPU Mode:")
                            yield Select([
                                ("Exclusive Process (recommended)", "exclusive_process"),
                                ("Shared", "shared")
                            ], id="gpu-mode-select")
                            yield Static("💡 Exclusive gives better performance", classes="help-text")
                        
                        with Container(classes="resource-item"):
                            yield Static("Advanced GPU Options:")
                            yield Checkbox("Enable NVLink (multi-GPU)", id="nvlink-checkbox")
                            yield Checkbox("Enable MPS (Multi-Process Service)", id="mps-checkbox")
                            yield Static("💡 NVLink for multi-GPU communication", classes="help-text")
                
                # Resource estimates
                with Container(classes="estimate-section", id="estimates"):
                    yield Static("📊 **Resource Estimates**", id="estimates-title")
                    yield Static("", id="estimates-text")
    
    def on_mount(self) -> None:
        """Initialize the screen with current configuration"""
        # Set current values
        slots_input = self.query_one("#slots-input", Input)
        slots_input.value = str(self.job_config.slots)
        
        # Architecture selection
        arch_select = self.query_one("#arch-select", Select)
        if self.job_config.architecture_requirements:
            arch_select.value = self.job_config.architecture_requirements[0]
        else:
            arch_select.value = "any"
        
        # Handle GPU-specific setup
        if self.job_config.job_type == JobType.GPU:
            self._setup_gpu_options()
            self.query_one("#gpu-resources").display = True
        else:
            self.query_one("#gpu-resources").display = False
        
        # Update estimates
        self._update_estimates()
    
    def _setup_gpu_options(self) -> None:
        """Set up GPU-specific options"""
        gpu_type_select = self.query_one("#gpu-type-select", Select)
        
        # Populate GPU types based on available queues
        gpu_options = []
        for gpu_name, gpu_info in self.cluster_config.gpus.items():
            display_name = f"{gpu_info.model} ({gpu_info.vram_gb}GB) - ${gpu_info.cost_per_hour:.2f}/hour"
            gpu_options.append((display_name, gpu_name))
        
        if gpu_options:
            gpu_type_select.set_options(gpu_options)
        else:
            gpu_type_select.set_options([("No GPUs available", "")])
        
        # Set current GPU configuration
        if self.job_config.gpu_config:
            if self.job_config.gpu_config.gpu_type:
                gpu_type_select.value = self.job_config.gpu_config.gpu_type
            
            gpu_count_input = self.query_one("#gpu-count-input", Input)
            gpu_count_input.value = str(self.job_config.gpu_config.num_gpus)
            
            gpu_mode_select = self.query_one("#gpu-mode-select", Select)
            gpu_mode_select.value = self.job_config.gpu_config.gpu_mode.value
            
            nvlink_checkbox = self.query_one("#nvlink-checkbox", Checkbox)
            nvlink_checkbox.value = self.job_config.gpu_config.nvlink
            
            mps_checkbox = self.query_one("#mps-checkbox", Checkbox)
            mps_checkbox.value = self.job_config.gpu_config.mps
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input field changes"""
        if event.input.id == "slots-input":
            try:
                self.job_config.slots = int(event.value) if event.value else 1
            except ValueError:
                pass
        elif event.input.id == "gpu-count-input":
            try:
                if self.job_config.gpu_config:
                    self.job_config.gpu_config.num_gpus = int(event.value) if event.value else 1
            except ValueError:
                pass
        
        self._update_estimates()
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select dropdown changes"""
        if event.select.id == "arch-select":
            if event.value == "any":
                self.job_config.architecture_requirements = []
            else:
                self.job_config.architecture_requirements = [event.value]
        
        elif event.select.id == "gpu-type-select":
            if self.job_config.gpu_config:
                self.job_config.gpu_config.gpu_type = event.value
                # Update slots based on GPU type
                if event.value in self.cluster_config.gpus:
                    gpu_info = self.cluster_config.gpus[event.value]
                    self.job_config.slots = gpu_info.slots_per_gpu * self.job_config.gpu_config.num_gpus
                    slots_input = self.query_one("#slots-input", Input)
                    slots_input.value = str(self.job_config.slots)
        
        elif event.select.id == "gpu-mode-select":
            if self.job_config.gpu_config:
                from ..models.job_config import GPUMode
                self.job_config.gpu_config.gpu_mode = GPUMode(event.value)
        
        self._update_estimates()
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox changes"""
        if not self.job_config.gpu_config:
            return
        
        if event.checkbox.id == "nvlink-checkbox":
            self.job_config.gpu_config.nvlink = event.value
        elif event.checkbox.id == "mps-checkbox":
            self.job_config.gpu_config.mps = event.value
    
    def _update_estimates(self) -> None:
        """Update resource estimates display"""
        estimates_text = self.query_one("#estimates-text", Static)
        
        # Calculate memory
        total_memory_gb = self.job_config.slots * 15
        
        estimates = [
            f"**Total CPU Cores:** {self.job_config.slots}",
            f"**Total Memory:** {total_memory_gb} GB ({self.job_config.slots} × 15 GB)",
        ]
        
        # GPU estimates
        if self.job_config.job_type == JobType.GPU and self.job_config.gpu_config:
            gpu_type = self.job_config.gpu_config.gpu_type
            num_gpus = self.job_config.gpu_config.num_gpus
            
            if gpu_type in self.cluster_config.gpus:
                gpu_info = self.cluster_config.gpus[gpu_type]
                total_vram = gpu_info.vram_gb * num_gpus
                estimates.extend([
                    f"**GPU Type:** {gpu_info.model}",
                    f"**Number of GPUs:** {num_gpus}",
                    f"**Total VRAM:** {total_vram} GB",
                    f"**GPU Cost:** ${gpu_info.cost_per_hour:.2f}/hour per GPU"
                ])
        
        # Cost estimate (if runtime is set)
        if self.job_config.runtime_limit:
            cost = self.wizard_app.command_builder.estimate_cost(self.job_config)
            estimates.append(f"**Estimated Cost:** ${cost:.2f}")
        
        estimates_text.update("\\n".join(estimates))
    
    def validate(self) -> bool:
        """Validate resource configuration"""
        errors = []
        
        # Validate slots
        valid, error = JobValidator.validate_slots(self.job_config.slots)
        if not valid:
            errors.append(error)
        
        # Validate GPU configuration
        if self.job_config.job_type == JobType.GPU:
            if not self.job_config.gpu_config:
                errors.append("GPU configuration is required for GPU jobs")
            else:
                valid, error = JobValidator.validate_gpu_count(self.job_config.gpu_config.num_gpus)
                if not valid:
                    errors.append(error)
                
                if not self.job_config.gpu_config.gpu_type:
                    errors.append("GPU type selection is required")
        
        if errors:
            self.wizard_app.show_error_message("Resource Configuration Errors", errors)
            return False
        
        return True