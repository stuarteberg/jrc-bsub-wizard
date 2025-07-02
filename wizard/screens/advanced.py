from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.widgets import Static, Input, Select, Checkbox, Button, Markdown
from textual.widget import Widget

from ..utils.validators import JobValidator


class AdvancedScreen(Widget):
    """Screen for advanced job configuration options"""
    
    CSS = """
    .advanced-container {
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
    
    .advanced-section {
        background: $surface-lighten-1;
        padding: 2;
        margin: 1 0;
        border: solid $primary;
    }
    
    .optional-section {
        background: $surface-lighten-1;
        padding: 2;
        margin: 1 0;
        border: solid $accent;
    }
    
    .advanced-grid {
        height: auto;
        grid-size: 2 2;
        grid-gutter: 1;
    }
    
    .env-grid {
        height: auto;
        grid-size: 3;
        grid-gutter: 1;
    }
    
    .advanced-item {
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
    
    .env-var-list {
        background: $surface-lighten-2;
        padding: 1;
        margin: 1 0;
        border: solid $surface-lighten-3;
        height: 6;
        overflow-y: auto;
    }
    
    Input {
        margin: 0 0 1 0;
    }
    
    Select {
        margin: 0 0 1 0;
    }
    
    Button.small {
        min-width: 8;
        margin: 0 1;
    }
    """
    
    def __init__(self, app, job_config, cluster_config):
        super().__init__()
        self.app = app
        self.job_config = job_config
        self.cluster_config = cluster_config
    
    def compose(self) -> ComposeResult:
        """Create the advanced options layout"""
        with Container(classes="advanced-container"):
            with Vertical():
                yield Static(
                    "🔧 Step 7: Advanced Options",
                    classes="section-title"
                )
                
                yield Markdown("""
Configure advanced job requirements and optimizations. These options are typically only needed for specialized workloads.
""")
                
                # Architecture and hardware requirements
                with Container(classes="advanced-section"):
                    yield Static("🏗️ **Hardware Requirements**", classes="subsection-title")
                    
                    with Grid(classes="advanced-grid"):
                        with Container(classes="advanced-item"):
                            yield Static("CPU Architecture:")
                            yield Select([
                                ("Any (fastest scheduling)", "any"),
                                ("AVX2 compatible", "avx2"),
                                ("AVX512 compatible", "avx512"),
                                ("AMX compatible (Sapphire Rapids only)", "amx")
                            ], id="arch-requirement-select")
                            yield Static("💡 Leave as 'Any' unless you need specific features", classes="help-text")
                        
                        with Container(classes="advanced-item"):
                            yield Static("Custom Resource Requirements:")
                            yield Input(
                                placeholder='select[mem>64000]',
                                id="custom-resources-input"
                            )
                            yield Static("💡 Advanced LSF resource expressions", classes="help-text")
                
                # Software licenses
                with Container(classes="optional-section"):
                    yield Static("📜 **Software Licenses**", classes="subsection-title")
                    
                    yield Checkbox("Request IDL licenses", id="idl-checkbox")
                    yield Input(
                        placeholder="Number of IDL licenses (default: 1)",
                        id="idl-count-input"
                    )
                    
                    yield Checkbox("Request MATLAB licenses", id="matlab-checkbox")
                    yield Input(
                        placeholder="Number of MATLAB licenses (default: 1)",
                        id="matlab-count-input"
                    )
                    
                    yield Static("💡 Only request licenses if your application needs them", classes="help-text")
                
                # Environment variables
                with Container(classes="optional-section"):
                    yield Static("🌍 **Environment Variables**", classes="subsection-title")
                    
                    with Horizontal():
                        yield Input(placeholder="Variable name", id="env-name-input")
                        yield Input(placeholder="Variable value", id="env-value-input")
                        yield Button("Add", id="add-env-button", classes="small")
                        yield Button("Clear All", id="clear-env-button", classes="small")
                    
                    with Container(classes="env-var-list", id="env-var-list"):
                        yield Static("No environment variables set", id="env-vars-display")
                
                # MPI/Parallel options
                with Container(classes="optional-section", id="mpi-section"):
                    yield Static("🔄 **Parallel Processing Options**", classes="subsection-title")
                    
                    yield Static("Parallel Environment:")
                    yield Select([
                        ("None", "none"),
                        ("parallel-48", "parallel-48"),
                        ("Custom", "custom")
                    ], id="parallel-env-select")
                    
                    yield Input(
                        placeholder="Custom parallel environment",
                        id="custom-parallel-input"
                    )
                    
                    yield Static("💡 Required for MPI jobs, use parallel-48 for most cases", classes="help-text")
                
                # Expert options
                with Container(classes="optional-section"):
                    yield Static("⚠️ **Expert Options**", classes="subsection-title")
                    
                    yield Markdown("""
**Warning**: These options can significantly affect job behavior. Only modify if you understand the implications.

Use these settings for specialized requirements like:
- Custom memory allocation patterns
- Specific node types or features  
- Advanced LSF resource expressions
- Non-standard parallel environments
""")
    
    def on_mount(self) -> None:
        """Initialize the screen with current configuration"""
        # Architecture requirements
        arch_select = self.query_one("#arch-requirement-select", Select)
        if self.job_config.architecture_requirements:
            arch_select.value = self.job_config.architecture_requirements[0]
        else:
            arch_select.value = "any"
        
        # Custom resources
        custom_resources_input = self.query_one("#custom-resources-input", Input)
        if self.job_config.custom_resources:
            custom_resources_input.value = " | ".join(self.job_config.custom_resources)
        
        # License requirements
        if "idl" in self.job_config.license_requirements:
            idl_checkbox = self.query_one("#idl-checkbox", Checkbox)
            idl_checkbox.value = True
            idl_count_input = self.query_one("#idl-count-input", Input)
            idl_count_input.value = str(self.job_config.license_requirements["idl"])
        
        if "matlab" in self.job_config.license_requirements:
            matlab_checkbox = self.query_one("#matlab-checkbox", Checkbox)
            matlab_checkbox.value = True
            matlab_count_input = self.query_one("#matlab-count-input", Input)
            matlab_count_input.value = str(self.job_config.license_requirements["matlab"])
        
        # Parallel environment
        parallel_env_select = self.query_one("#parallel-env-select", Select)
        if self.job_config.parallel_environment:
            if self.job_config.parallel_environment == "parallel-48":
                parallel_env_select.value = "parallel-48"
            else:
                parallel_env_select.value = "custom"
                custom_parallel_input = self.query_one("#custom-parallel-input", Input)
                custom_parallel_input.value = self.job_config.parallel_environment
        else:
            parallel_env_select.value = "none"
        
        # Update displays
        self._update_env_vars_display()
        self._toggle_mpi_section()
    
    def _toggle_mpi_section(self) -> None:
        """Show/hide MPI section based on job type"""
        from ..models.job_config import JobType
        mpi_section = self.query_one("#mpi-section")
        mpi_section.display = (self.job_config.job_type == JobType.MPI)
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select dropdown changes"""
        if event.select.id == "arch-requirement-select":
            if event.value == "any":
                self.job_config.architecture_requirements = []
            else:
                self.job_config.architecture_requirements = [event.value]
        
        elif event.select.id == "parallel-env-select":
            if event.value == "none":
                self.job_config.parallel_environment = None
            elif event.value == "parallel-48":
                self.job_config.parallel_environment = "parallel-48"
            elif event.value == "custom":
                custom_parallel_input = self.query_one("#custom-parallel-input", Input)
                custom_parallel_input.display = True
            
            # Hide custom input for non-custom selections
            if event.value != "custom":
                custom_parallel_input = self.query_one("#custom-parallel-input", Input)
                custom_parallel_input.display = False
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input field changes"""
        if event.input.id == "custom-resources-input":
            if event.value.strip():
                # Split by | for multiple resources
                resources = [r.strip() for r in event.value.split("|") if r.strip()]
                self.job_config.custom_resources = resources
            else:
                self.job_config.custom_resources = []
        
        elif event.input.id == "custom-parallel-input":
            self.job_config.parallel_environment = event.value if event.value else None
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox changes"""
        if event.checkbox.id == "idl-checkbox":
            if event.value:
                # Get count from input or default to 1
                idl_count_input = self.query_one("#idl-count-input", Input)
                count = int(idl_count_input.value) if idl_count_input.value else 1
                self.job_config.license_requirements["idl"] = count
            else:
                self.job_config.license_requirements.pop("idl", None)
        
        elif event.checkbox.id == "matlab-checkbox":
            if event.value:
                # Get count from input or default to 1
                matlab_count_input = self.query_one("#matlab-count-input", Input)
                count = int(matlab_count_input.value) if matlab_count_input.value else 1
                self.job_config.license_requirements["matlab"] = count
            else:
                self.job_config.license_requirements.pop("matlab", None)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "add-env-button":
            self._add_environment_variable()
        elif event.button.id == "clear-env-button":
            self._clear_environment_variables()
    
    def _add_environment_variable(self) -> None:
        """Add a new environment variable"""
        env_name_input = self.query_one("#env-name-input", Input)
        env_value_input = self.query_one("#env-value-input", Input)
        
        var_name = env_name_input.value.strip()
        var_value = env_value_input.value.strip()
        
        if not var_name:
            self.app.show_error_message("Invalid Environment Variable", ["Variable name is required"])
            return
        
        # Validate the environment variable
        valid, error = JobValidator.validate_environment_variable(var_name, var_value)
        if not valid:
            self.app.show_error_message("Invalid Environment Variable", [error])
            return
        
        # Add to configuration
        self.job_config.environment_vars[var_name] = var_value
        
        # Clear inputs
        env_name_input.value = ""
        env_value_input.value = ""
        
        # Update display
        self._update_env_vars_display()
    
    def _clear_environment_variables(self) -> None:
        """Clear all environment variables"""
        self.job_config.environment_vars.clear()
        self._update_env_vars_display()
    
    def _update_env_vars_display(self) -> None:
        """Update the environment variables display"""
        env_vars_display = self.query_one("#env-vars-display", Static)
        
        if self.job_config.environment_vars:
            env_lines = []
            for var_name, var_value in self.job_config.environment_vars.items():
                env_lines.append(f"{var_name}={var_value}")
            env_vars_display.update("\\n".join(env_lines))
        else:
            env_vars_display.update("No environment variables set")
    
    def validate(self) -> bool:
        """Validate advanced configuration"""
        errors = []
        warnings = []
        
        # Validate custom resources
        for resource in self.job_config.custom_resources:
            if not resource.strip():
                errors.append("Empty custom resource expression")
            elif not resource.startswith(('select[', 'rusage[', 'order[')):
                warnings.append(f"Custom resource '{resource}' may not be a valid LSF expression")
        
        # Validate license counts
        for license_type, count in self.job_config.license_requirements.items():
            if count < 1:
                errors.append(f"{license_type.upper()} license count must be at least 1")
            elif count > 100:
                warnings.append(f"{license_type.upper()} license count ({count}) is very high")
        
        # Validate environment variables
        for var_name, var_value in self.job_config.environment_vars.items():
            valid, error = JobValidator.validate_environment_variable(var_name, var_value)
            if not valid:
                errors.append(f"Environment variable {var_name}: {error}")
        
        # Validate parallel environment for MPI jobs
        from ..models.job_config import JobType
        if self.job_config.job_type == JobType.MPI:
            if not self.job_config.parallel_environment:
                errors.append("Parallel environment is required for MPI jobs")
            elif self.job_config.parallel_environment == "parallel-48":
                # Check that slots is multiple of 48
                if self.job_config.slots % 48 != 0:
                    errors.append("MPI jobs with parallel-48 must request slots in multiples of 48")
        
        # Show errors
        if errors:
            self.app.show_error_message("Advanced Configuration Errors", errors)
            return False
        
        # Show warnings
        if warnings:
            self.app.show_warning_message("Advanced Configuration Warnings", "\\n".join(warnings))
        
        return True