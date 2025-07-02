from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, RadioSet, RadioButton, Markdown
from textual.widget import Widget

from ..models.job_config import JobType


class QueueScreen(Widget):
    """Screen for selecting compute queue"""
    
    CSS = """
    .queue-container {
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
    
    .queue-selection {
        background: $surface-lighten-1;
        padding: 2;
        margin: 1 0;
        border: solid $primary;
    }
    
    .queue-details {
        background: $surface-lighten-1;
        padding: 2;
        margin: 1 0;
        border: solid $accent;
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
    
    .recommended {
        background: $success;
        color: $text;
        padding: 0 1;
        border-radius: 1;
    }
    
    .expensive {
        background: $warning;
        color: $text;
        padding: 0 1;
        border-radius: 1;
    }
    """
    
    def __init__(self, wizard_app, job_config, cluster_config):
        super().__init__()
        self.wizard_app = wizard_app
        self.job_config = job_config
        self.cluster_config = cluster_config
    
    def compose(self) -> ComposeResult:
        """Create the queue selection layout"""
        with Container(classes="queue-container"):
            with Vertical():
                yield Static(
                    "🎯 Step 4: Select Queue",
                    classes="section-title"
                )
                
                yield Markdown("""
Choose the appropriate queue for your job. Queues have different resource limits, runtime limits, and priorities.
""")
                
                with Container(classes="queue-selection"):
                    yield Static("Available Queues:", classes="subsection-title")
                    with RadioSet(id="queue-selection"):
                        pass  # Will be populated dynamically
                
                with Container(classes="queue-details", id="queue-details"):
                    yield Static("Select a queue above to see details", id="queue-description")
    
    def on_mount(self) -> None:
        """Initialize the screen with available queues"""
        self._populate_queues()
        self._set_current_selection()
    
    def _populate_queues(self) -> None:
        """Populate queue options based on job type"""
        radio_set = self.query_one("#queue-selection", RadioSet)
        
        # Get appropriate queues for job type
        job_type_str = self.job_config.job_type.value if self.job_config.job_type else "cpu"
        available_queues = self.cluster_config.get_queues_for_job_type(job_type_str)
        
        # Sort queues by recommendation
        recommended_queues = self._get_recommended_queues()
        
        for queue_info in available_queues:
            # Create display label with indicators
            label_parts = [queue_info.name]
            
            if queue_info.name in recommended_queues:
                label_parts.append("🌟 RECOMMENDED")
            
            # Add cost/runtime info
            if queue_info.max_runtime:
                if queue_info.max_runtime_display:
                    label_parts.append(f"({queue_info.max_runtime_display} max)")
            else:
                label_parts.append("(no time limit)")
            
            # Add GPU cost info for GPU queues
            if self.job_config.job_type == JobType.GPU and queue_info.gpu_types:
                gpu_costs = [self.cluster_config.gpus[gpu].cost_per_hour 
                            for gpu in queue_info.gpu_types 
                            if gpu in self.cluster_config.gpus]
                if gpu_costs:
                    min_cost = min(gpu_costs)
                    max_cost = max(gpu_costs)
                    if min_cost == max_cost:
                        label_parts.append(f"${min_cost:.2f}/GPU/hour")
                    else:
                        label_parts.append(f"${min_cost:.2f}-${max_cost:.2f}/GPU/hour")
            
            label = " - ".join(label_parts)
            
            radio_button = RadioButton(
                label,
                value=queue_info.name,
                id=f"queue-{queue_info.name}"
            )
            radio_set.mount(radio_button)
    
    def _get_recommended_queues(self) -> list:
        """Get recommended queues based on job configuration"""
        job_type = self.job_config.job_type
        
        if job_type == JobType.CPU:
            return ["local", "short"]
        elif job_type == JobType.GPU:
            return ["gpu_a100", "gpu_l4"]
        elif job_type == JobType.INTERACTIVE:
            return ["interactive"]
        elif job_type == JobType.MPI:
            return ["mpi"]
        else:
            return []
    
    def _set_current_selection(self) -> None:
        """Set the current queue selection"""
        radio_set = self.query_one("#queue-selection", RadioSet)
        
        if self.job_config.queue:
            radio_set.pressed = self.job_config.queue
        else:
            # Auto-select recommended queue
            recommended = self._get_recommended_queues()
            if recommended:
                radio_set.pressed = recommended[0]
                self.job_config.queue = recommended[0]
        
        # Update description
        if radio_set.pressed:
            self._update_queue_description(radio_set.pressed)
    
    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle queue selection changes"""
        selected_queue = event.pressed
        self.job_config.queue = selected_queue
        self._update_queue_description(selected_queue)
    
    def _update_queue_description(self, queue_name: str) -> None:
        """Update the queue description display"""
        queue_info = self.cluster_config.queues.get(queue_name)
        if not queue_info:
            return
        
        description_parts = [
            f"**{queue_info.name.upper()}** - {queue_info.description}",
            ""
        ]
        
        # Runtime information
        if queue_info.max_runtime:
            description_parts.extend([
                f"**Maximum Runtime:** {queue_info.max_runtime_display}",
            ])
            if queue_info.default_runtime:
                description_parts.append(f"**Default Runtime:** {queue_info.default_runtime}")
        else:
            description_parts.append("**Maximum Runtime:** No limit (30 days)")
        
        # Resource limits
        if queue_info.max_slots_per_user:
            description_parts.append(f"**Max Slots per User:** {queue_info.max_slots_per_user:,}")
        
        if queue_info.max_jobs_per_user:
            description_parts.append(f"**Max Jobs per User:** {queue_info.max_jobs_per_user}")
        
        # Cost information
        description_parts.extend([
            "",
            f"**CPU Cost:** ${queue_info.cost_per_slot_hour:.2f} per slot per hour"
        ])
        
        # GPU-specific information
        if queue_info.gpu_types:
            description_parts.extend([
                "",
                "**Available GPU Types:**"
            ])
            
            for gpu_type in queue_info.gpu_types:
                if gpu_type in self.cluster_config.gpus:
                    gpu_info = self.cluster_config.gpus[gpu_type]
                    description_parts.append(
                        f"- {gpu_info.model}: {gpu_info.vram_gb}GB VRAM, "
                        f"{gpu_info.slots_per_gpu} slots, ${gpu_info.cost_per_hour:.2f}/hour"
                    )
        
        # Special requirements
        if queue_info.special_requirements:
            description_parts.extend([
                "",
                "**Special Requirements:**"
            ])
            for req in queue_info.special_requirements:
                description_parts.append(f"- {req}")
        
        # Usage recommendations
        description_parts.extend([
            "",
            "**Best For:**"
        ])
        
        recommendations = self._get_queue_recommendations(queue_name)
        for rec in recommendations:
            description_parts.append(f"- {rec}")
        
        # Compatibility check
        compatibility_issues = self._check_compatibility(queue_info)
        if compatibility_issues:
            description_parts.extend([
                "",
                "⚠️ **Compatibility Issues:**"
            ])
            for issue in compatibility_issues:
                description_parts.append(f"- {issue}")
        
        description_text = self.query_one("#queue-description", Static)
        description_text.update("\\n".join(description_parts))
    
    def _get_queue_recommendations(self, queue_name: str) -> list:
        """Get usage recommendations for a specific queue"""
        recommendations = {
            "interactive": [
                "Development and debugging",
                "Interactive data analysis", 
                "Testing code before batch submission",
                "Running Jupyter notebooks",
                "GUI applications (with X11 forwarding)"
            ],
            "local": [
                "Long-running CPU computations",
                "Production workloads",
                "Jobs requiring more than 1 hour",
                "General scientific computing"
            ],
            "short": [
                "Quick tests and validation",
                "Jobs completing in under 1 hour",
                "Priority processing when cluster is busy",
                "Proof-of-concept runs"
            ],
            "gpu_a100": [
                "Deep learning model training",
                "Large-scale ML inference",
                "Computer vision tasks",
                "Natural language processing"
            ],
            "gpu_l4": [
                "Cost-effective ML inference",
                "Light training tasks",
                "Computer graphics workloads",
                "Video processing"
            ],
            "gpu_t4": [
                "Development and testing",
                "Small-scale training",
                "Educational ML projects",
                "Budget-conscious GPU computing"
            ],
            "mpi": [
                "Distributed parallel processing",
                "Large-scale scientific simulations",
                "Multi-node computations",
                "MPI-enabled applications"
            ]
        }
        
        return recommendations.get(queue_name, ["General purpose computing"])
    
    def _check_compatibility(self, queue_info) -> list:
        """Check for compatibility issues with current configuration"""
        issues = []
        
        # Check runtime compatibility
        if queue_info.max_runtime and self.job_config.runtime_limit:
            try:
                # Convert both to minutes for comparison
                max_minutes = self._parse_time_to_minutes(queue_info.max_runtime)
                requested_minutes = self._parse_time_to_minutes(self.job_config.runtime_limit)
                
                if requested_minutes > max_minutes:
                    issues.append(f"Requested runtime ({self.job_config.runtime_limit}) exceeds queue limit ({queue_info.max_runtime})")
            except:
                pass
        
        # Check slot limits
        if queue_info.max_slots_per_job and self.job_config.slots > queue_info.max_slots_per_job:
            issues.append(f"Requested slots ({self.job_config.slots}) exceeds queue limit ({queue_info.max_slots_per_job})")
        
        # Check GPU compatibility
        if self.job_config.job_type == JobType.GPU and not queue_info.gpu_types:
            issues.append("This queue does not support GPU jobs")
        elif self.job_config.job_type != JobType.GPU and queue_info.gpu_types:
            issues.append("This is a GPU queue but your job type is not GPU")
        
        return issues
    
    def _parse_time_to_minutes(self, time_str: str) -> int:
        """Parse time string to minutes"""
        if ':' in time_str:
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        else:
            return int(time_str)
    
    def validate(self) -> bool:
        """Validate queue selection"""
        if not self.job_config.queue:
            self.wizard_app.show_error_message("Queue Selection Required", ["Please select a queue"])
            return False
        
        # Check compatibility
        queue_info = self.cluster_config.queues.get(self.job_config.queue)
        if queue_info:
            compatibility_issues = self._check_compatibility(queue_info)
            if compatibility_issues:
                self.wizard_app.show_warning_message(
                    "Compatibility Issues", 
                    "\\n".join(compatibility_issues) + "\\n\\nDo you want to continue anyway?"
                )
                # For now, continue despite warnings
        
        return True