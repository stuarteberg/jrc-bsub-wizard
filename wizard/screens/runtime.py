from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.widgets import Static, Input, Checkbox, Markdown
from textual.widget import Widget

from ..utils.validators import JobValidator


class RuntimeScreen(Widget):
    """Screen for configuring runtime and scheduling options"""
    
    CSS = """
    .runtime-container {
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
    
    .runtime-section {
        background: $surface-lighten-1;
        padding: 2;
        margin: 1 0;
        border: solid $primary;
    }
    
    .array-section {
        background: $surface-lighten-1;
        padding: 2;
        margin: 1 0;
        border: solid $accent;
    }
    
    .runtime-grid {
        height: auto;
        grid-size: 2 2;
        grid-gutter: 1;
    }
    
    .array-grid {
        height: auto;
        grid-size: 3 2;
        grid-gutter: 1;
    }
    
    .runtime-item {
        background: $surface-lighten-2;
        padding: 1;
        border: solid $surface-lighten-3;
    }
    
    .help-text {
        color: $text-muted;
        font-style: italic;
    }
    
    .warning-text {
        color: $warning;
        font-weight: bold;
    }
    
    Input {
        margin: 0 0 1 0;
    }
    
    Checkbox {
        margin: 0 0 1 0;
    }
    """
    
    def __init__(self, app, job_config, cluster_config):
        super().__init__()
        self.app = app
        self.job_config = job_config
        self.cluster_config = cluster_config
    
    def compose(self) -> ComposeResult:
        """Create the runtime configuration layout"""
        with Container(classes="runtime-container"):
            with Vertical():
                yield Static(
                    "⏰ Step 5: Runtime & Scheduling",
                    classes="section-title"
                )
                
                yield Markdown("""
Configure job scheduling, runtime limits, and notification options. These settings affect job priority and behavior.
""")
                
                # Basic runtime configuration
                with Container(classes="runtime-section"):
                    yield Static("⏱️ **Job Timing**", classes="subsection-title")
                    
                    with Grid(classes="runtime-grid"):
                        with Container(classes="runtime-item"):
                            yield Static("Job Name:")
                            yield Input(
                                placeholder="my_job_name",
                                id="job-name-input"
                            )
                            yield Static("💡 Use descriptive names, avoid spaces", classes="help-text")
                        
                        with Container(classes="runtime-item"):
                            yield Static("Command to Execute:")
                            yield Input(
                                placeholder="python script.py",
                                id="command-input"
                            )
                            yield Static("💡 The command that will be executed", classes="help-text")
                        
                        with Container(classes="runtime-item"):
                            yield Static("Runtime Limit (MM or HH:MM):")
                            yield Input(
                                placeholder="60 or 1:00",
                                id="runtime-limit-input"
                            )
                            yield Static("💡 Job will be killed after this time", classes="help-text")
                        
                        with Container(classes="runtime-item"):
                            yield Static("Runtime Estimate (MM or HH:MM):")
                            yield Input(
                                placeholder="30 or 0:30",
                                id="runtime-estimate-input"
                            )
                            yield Static("💡 Helps scheduler optimize placement", classes="help-text")
                
                # Notification options
                with Container(classes="runtime-section"):
                    yield Static("📧 **Notifications**", classes="subsection-title")
                    
                    yield Checkbox("Send email when job completes", id="email-complete-checkbox")
                    yield Checkbox("Send email when job starts", id="email-start-checkbox")
                    yield Static("💡 Emails sent to your cluster account", classes="help-text")
                
                # Array job configuration
                with Container(classes="array-section", id="array-section"):
                    yield Static("🔢 **Array Jobs** (Optional)", classes="subsection-title")
                    
                    yield Checkbox("Enable array job", id="array-enable-checkbox")
                    yield Static("💡 Run multiple similar jobs with different parameters", classes="help-text")
                    
                    with Grid(classes="array-grid", id="array-grid"):
                        with Container(classes="runtime-item"):
                            yield Static("Start Index:")
                            yield Input(
                                placeholder="1",
                                id="array-start-input"
                            )
                        
                        with Container(classes="runtime-item"):
                            yield Static("End Index:")
                            yield Input(
                                placeholder="100",
                                id="array-end-input"
                            )
                        
                        with Container(classes="runtime-item"):
                            yield Static("Step Size:")
                            yield Input(
                                placeholder="1",
                                id="array-step-input"
                            )
                        
                        with Container(classes="runtime-item"):
                            yield Static("Max Parallel Jobs:")
                            yield Input(
                                placeholder="10 (optional)",
                                id="array-parallel-input"
                            )
                        
                        with Container(classes="runtime-item"):
                            yield Static("Total Jobs:")
                            yield Static("", id="array-total-display")
                        
                        with Container(classes="runtime-item"):
                            yield Static("Cost Multiplier:")
                            yield Static("", id="array-cost-display")
                
                # Additional options
                with Container(classes="runtime-section"):
                    yield Static("⚙️ **Additional Options**", classes="subsection-title")
                    
                    yield Checkbox("Enable X11 forwarding (for GUI apps)", id="x11-checkbox")
                    yield Static("💡 Required for graphical applications", classes="help-text")
    
    def on_mount(self) -> None:
        """Initialize the screen with current configuration"""
        # Set current values
        job_name_input = self.query_one("#job-name-input", Input)
        job_name_input.value = self.job_config.job_name or ""
        
        command_input = self.query_one("#command-input", Input)
        command_input.value = self.job_config.command or ""
        
        runtime_limit_input = self.query_one("#runtime-limit-input", Input)
        runtime_limit_input.value = self.job_config.runtime_limit or ""
        
        runtime_estimate_input = self.query_one("#runtime-estimate-input", Input)
        runtime_estimate_input.value = self.job_config.runtime_estimate or ""
        
        # Notification settings
        email_complete_checkbox = self.query_one("#email-complete-checkbox", Checkbox)
        email_complete_checkbox.value = self.job_config.email_notifications
        
        email_start_checkbox = self.query_one("#email-start-checkbox", Checkbox)
        email_start_checkbox.value = self.job_config.email_on_start
        
        # Array job settings
        array_enable_checkbox = self.query_one("#array-enable-checkbox", Checkbox)
        array_enable_checkbox.value = self.job_config.array_config.enabled
        
        if self.job_config.array_config.enabled:
            array_start_input = self.query_one("#array-start-input", Input)
            array_start_input.value = str(self.job_config.array_config.start_index)
            
            array_end_input = self.query_one("#array-end-input", Input)
            array_end_input.value = str(self.job_config.array_config.end_index)
            
            array_step_input = self.query_one("#array-step-input", Input)
            array_step_input.value = str(self.job_config.array_config.step)
            
            if self.job_config.array_config.max_parallel:
                array_parallel_input = self.query_one("#array-parallel-input", Input)
                array_parallel_input.value = str(self.job_config.array_config.max_parallel)
        
        # Additional options
        x11_checkbox = self.query_one("#x11-checkbox", Checkbox)
        x11_checkbox.value = self.job_config.x11_forwarding
        
        # Update displays
        self._update_array_display()
        self._toggle_array_controls()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input field changes"""
        if event.input.id == "job-name-input":
            self.job_config.job_name = event.value
        elif event.input.id == "command-input":
            self.job_config.command = event.value
        elif event.input.id == "runtime-limit-input":
            self.job_config.runtime_limit = event.value if event.value else None
        elif event.input.id == "runtime-estimate-input":
            self.job_config.runtime_estimate = event.value if event.value else None
        elif event.input.id == "array-start-input":
            try:
                self.job_config.array_config.start_index = int(event.value) if event.value else 1
            except ValueError:
                pass
        elif event.input.id == "array-end-input":
            try:
                self.job_config.array_config.end_index = int(event.value) if event.value else 1
            except ValueError:
                pass
        elif event.input.id == "array-step-input":
            try:
                self.job_config.array_config.step = int(event.value) if event.value else 1
            except ValueError:
                pass
        elif event.input.id == "array-parallel-input":
            try:
                if event.value:
                    self.job_config.array_config.max_parallel = int(event.value)
                else:
                    self.job_config.array_config.max_parallel = None
            except ValueError:
                pass
        
        # Update array calculations
        if event.input.id.startswith("array-"):
            self._update_array_display()
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox changes"""
        if event.checkbox.id == "email-complete-checkbox":
            self.job_config.email_notifications = event.value
        elif event.checkbox.id == "email-start-checkbox":
            self.job_config.email_on_start = event.value
        elif event.checkbox.id == "array-enable-checkbox":
            self.job_config.array_config.enabled = event.value
            self._toggle_array_controls()
            self._update_array_display()
        elif event.checkbox.id == "x11-checkbox":
            self.job_config.x11_forwarding = event.value
    
    def _toggle_array_controls(self) -> None:
        """Show/hide array job controls based on checkbox"""
        array_grid = self.query_one("#array-grid")
        array_grid.display = self.job_config.array_config.enabled
    
    def _update_array_display(self) -> None:
        """Update array job calculations"""
        if not self.job_config.array_config.enabled:
            return
        
        try:
            start = self.job_config.array_config.start_index
            end = self.job_config.array_config.end_index
            step = self.job_config.array_config.step
            
            if start <= end and step > 0:
                total_jobs = (end - start) // step + 1
                
                total_display = self.query_one("#array-total-display", Static)
                total_display.update(f"{total_jobs:,} jobs")
                
                cost_display = self.query_one("#array-cost-display", Static)
                cost_display.update(f"{total_jobs}x base cost")
            else:
                total_display = self.query_one("#array-total-display", Static)
                total_display.update("Invalid range")
                
                cost_display = self.query_one("#array-cost-display", Static)
                cost_display.update("N/A")
        except:
            pass
    
    def validate(self) -> bool:
        """Validate runtime configuration"""
        errors = []
        
        # Validate job name
        valid, error = JobValidator.validate_job_name(self.job_config.job_name)
        if not valid:
            errors.append(f"Job name: {error}")
        
        # Validate command
        valid, error = JobValidator.validate_command(self.job_config.command)
        if not valid:
            errors.append(f"Command: {error}")
        
        # Validate runtime format
        if self.job_config.runtime_limit:
            valid, error = JobValidator.validate_time_format(self.job_config.runtime_limit)
            if not valid:
                errors.append(f"Runtime limit: {error}")
        
        if self.job_config.runtime_estimate:
            valid, error = JobValidator.validate_time_format(self.job_config.runtime_estimate)
            if not valid:
                errors.append(f"Runtime estimate: {error}")
        
        # Validate array configuration
        if self.job_config.array_config.enabled:
            valid, error = JobValidator.validate_array_config(
                self.job_config.array_config.start_index,
                self.job_config.array_config.end_index,
                self.job_config.array_config.step
            )
            if not valid:
                errors.append(f"Array job: {error}")
        
        if errors:
            self.app.show_error_message("Runtime Configuration Errors", errors)
            return False
        
        return True