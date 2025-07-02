from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button, TextArea, Markdown
from textual.widget import Widget
import json


class ReviewScreen(Widget):
    """Final screen for reviewing and generating the bsub command"""
    
    CSS = """
    .review-container {
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
    
    .summary-section {
        background: $surface-lighten-1;
        padding: 2;
        margin: 1 0;
        border: solid $primary;
    }
    
    .command-section {
        background: $surface-darken-1;
        padding: 2;
        margin: 1 0;
        border: solid $accent;
    }
    
    .cost-section {
        background: $success;
        color: $text;
        padding: 2;
        margin: 1 0;
        border: solid $success-lighten-1;
    }
    
    .warning-section {
        background: $warning;
        color: $text;
        padding: 2;
        margin: 1 0;
        border: solid $warning-lighten-1;
    }
    
    .command-text {
        background: $surface-darken-2;
        color: $text;
        padding: 1;
        border: solid $accent-lighten-1;
        font-family: monospace;
        margin: 1 0;
    }
    
    .action-buttons {
        height: auto;
        margin: 2 0;
    }
    
    Button {
        margin: 0 1;
        min-width: 15;
    }
    
    Button.primary {
        background: $accent;
        color: $text;
    }
    
    Button.secondary {
        background: $surface-lighten-2;
        color: $text;
    }
    
    TextArea {
        height: 10;
        margin: 1 0;
    }
    """
    
    def __init__(self, wizard_app, job_config, cluster_config, final_command=None, estimated_cost=0.0):
        super().__init__()
        self.wizard_app = wizard_app
        self.job_config = job_config
        self.cluster_config = cluster_config
        self.final_command = final_command
        self.estimated_cost = estimated_cost
    
    def compose(self) -> ComposeResult:
        """Create the review and command generation layout"""
        with Container(classes="review-container"):
            with Vertical():
                yield Static(
                    "✅ Step 8: Review & Generate Command",
                    classes="section-title"
                )
                
                yield Markdown("""
Review your job configuration and generated command. Make sure everything looks correct before saving or submitting.
""")
                
                # Job summary
                with Container(classes="summary-section"):
                    yield Static("📋 **Job Summary**", classes="subsection-title")
                    yield Static("", id="job-summary")
                
                # Cost estimate
                with Container(classes="cost-section", id="cost-section"):
                    yield Static("💰 **Cost Estimate**", classes="subsection-title")
                    yield Static("", id="cost-estimate")
                
                # Warnings (if any)
                with Container(classes="warning-section", id="warnings-section"):
                    yield Static("⚠️ **Warnings**", classes="subsection-title")
                    yield Static("", id="warnings-text")
                
                # Generated command
                with Container(classes="command-section"):
                    yield Static("🚀 **Generated BSub Command**", classes="subsection-title")
                    yield TextArea("", id="command-display", read_only=True)
                    yield Static("💡 Click 'Copy Command' to copy to clipboard", classes="help-text")
                
                # Generated script (if applicable)
                with Container(classes="command-section", id="script-section"):
                    yield Static("📜 **Complete Job Script**", classes="subsection-title")
                    yield TextArea("", id="script-display", read_only=True)
                
                # Action buttons
                with Horizontal(classes="action-buttons"):
                    yield Button("📋 Copy Command", id="copy-command-button", classes="primary")
                    yield Button("📄 Copy Script", id="copy-script-button", classes="secondary")
                    yield Button("💾 Save Config", id="save-config-button", classes="secondary")
                    yield Button("📤 Export Script", id="export-script-button", classes="secondary")
                    yield Button("🔄 Restart Wizard", id="restart-button", classes="secondary")
    
    def on_mount(self) -> None:
        """Initialize the review screen"""
        self._generate_command_and_script()
        self._update_job_summary()
        self._update_cost_estimate()
        self._check_warnings()
    
    def _generate_command_and_script(self) -> None:
        """Generate the final command and script"""
        # Generate command if not provided
        if not self.final_command:
            self.final_command = self.wizard_app.command_builder.build_command(self.job_config)
        
        # Display command
        command_display = self.query_one("#command-display", TextArea)
        command_display.text = self.final_command
        
        # Generate complete script
        script_content = self.wizard_app.command_builder.generate_job_script(self.job_config)
        script_display = self.query_one("#script-display", TextArea)
        script_display.text = script_content
    
    def _update_job_summary(self) -> None:
        """Update the job summary display"""
        summary_lines = [
            f"**Job Name:** {self.job_config.job_name}",
            f"**Job Type:** {self.job_config.job_type.value.upper()}",
            f"**Queue:** {self.job_config.queue}",
            f"**CPU Slots:** {self.job_config.slots}",
            f"**Memory:** {self.job_config.slots * 15} GB",
        ]
        
        # Add GPU information
        if self.job_config.gpu_config:
            gpu_info = self.cluster_config.gpus.get(self.job_config.gpu_config.gpu_type)
            if gpu_info:
                summary_lines.extend([
                    f"**GPU Type:** {gpu_info.model}",
                    f"**Number of GPUs:** {self.job_config.gpu_config.num_gpus}",
                    f"**Total GPU Memory:** {gpu_info.vram_gb * self.job_config.gpu_config.num_gpus} GB"
                ])
        
        # Add runtime information
        if self.job_config.runtime_limit:
            summary_lines.append(f"**Runtime Limit:** {self.job_config.runtime_limit}")
        
        # Add array job information
        if self.job_config.array_config.enabled:
            total_jobs = (self.job_config.array_config.end_index - self.job_config.array_config.start_index) // self.job_config.array_config.step + 1
            summary_lines.extend([
                f"**Array Job:** {total_jobs:,} tasks",
                f"**Array Range:** {self.job_config.array_config.start_index}-{self.job_config.array_config.end_index}:{self.job_config.array_config.step}"
            ])
        
        # Add file information
        if self.job_config.output_file:
            summary_lines.append(f"**Output File:** {self.job_config.output_file}")
        
        if self.job_config.working_directory:
            summary_lines.append(f"**Working Directory:** {self.job_config.working_directory}")
        
        summary_text = self.query_one("#job-summary", Static)
        summary_text.update("\\n".join(summary_lines))
    
    def _update_cost_estimate(self) -> None:
        """Update the cost estimate display"""
        if not self.estimated_cost:
            self.estimated_cost = self.wizard_app.command_builder.estimate_cost(self.job_config)
        
        cost_lines = []
        
        if self.job_config.runtime_limit:
            # Parse runtime
            if ':' in self.job_config.runtime_limit:
                hours, minutes = map(int, self.job_config.runtime_limit.split(':'))
                runtime_hours = hours + minutes / 60
            else:
                runtime_hours = int(self.job_config.runtime_limit) / 60
            
            # CPU cost breakdown
            cpu_cost = self.job_config.slots * runtime_hours * 0.05
            cost_lines.extend([
                f"**CPU Cost:** {self.job_config.slots} slots × {runtime_hours:.1f} hours × $0.05 = ${cpu_cost:.2f}",
            ])
            
            # GPU cost breakdown
            if self.job_config.gpu_config:
                gpu_info = self.cluster_config.gpus.get(self.job_config.gpu_config.gpu_type)
                if gpu_info:
                    gpu_cost = self.job_config.gpu_config.num_gpus * runtime_hours * gpu_info.cost_per_hour
                    cost_lines.append(
                        f"**GPU Cost:** {self.job_config.gpu_config.num_gpus} GPUs × {runtime_hours:.1f} hours × ${gpu_info.cost_per_hour:.2f} = ${gpu_cost:.2f}"
                    )
            
            # Array job multiplier
            if self.job_config.array_config.enabled:
                total_jobs = (self.job_config.array_config.end_index - self.job_config.array_config.start_index) // self.job_config.array_config.step + 1
                cost_lines.append(f"**Array Multiplier:** × {total_jobs:,} tasks")
            
            cost_lines.extend([
                "",
                f"**Total Estimated Cost: ${self.estimated_cost:.2f}**"
            ])
            
            if self.estimated_cost > 100:
                cost_lines.append("⚠️ **High cost job** - please verify requirements")
        else:
            cost_lines = [
                "**No runtime limit specified**",
                "Cannot estimate cost without runtime limit",
                "💡 Set a runtime limit to see cost estimate"
            ]
        
        cost_estimate = self.query_one("#cost-estimate", Static)
        cost_estimate.update("\\n".join(cost_lines))
    
    def _check_warnings(self) -> None:
        """Check for potential issues and show warnings"""
        warnings = []
        
        # Validate configuration
        validation_warnings = self.wizard_app.command_builder.validate_configuration(self.job_config)
        warnings.extend(validation_warnings)
        
        # Additional checks
        if not self.job_config.runtime_limit:
            warnings.append("No runtime limit set - job may run indefinitely")
        
        if self.job_config.output_file == self.job_config.error_file:
            warnings.append("Output and error files are the same")
        
        if self.job_config.array_config.enabled and self.estimated_cost > 1000:
            warnings.append("Array job has very high estimated cost")
        
        # Show/hide warnings section
        warnings_section = self.query_one("#warnings-section")
        if warnings:
            warnings_section.display = True
            warnings_text = self.query_one("#warnings-text", Static)
            warnings_text.update("\\n".join([f"• {w}" for w in warnings]))
        else:
            warnings_section.display = False
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "copy-command-button":
            self._copy_command()
        elif button_id == "copy-script-button":
            self._copy_script()
        elif button_id == "save-config-button":
            self._save_configuration()
        elif button_id == "export-script-button":
            self._export_script()
        elif button_id == "restart-button":
            self._restart_wizard()
    
    def _copy_command(self) -> None:
        """Copy the bsub command to clipboard"""
        try:
            import pyperclip
            pyperclip.copy(self.final_command)
            self.wizard_app.show_success_message("Command Copied", "BSub command copied to clipboard!")
        except ImportError:
            # Fallback - show the command in a modal
            self.wizard_app.show_success_message(
                "Copy Command", 
                f"Copy this command:\\n\\n{self.final_command}"
            )
    
    def _copy_script(self) -> None:
        """Copy the complete script to clipboard"""
        script_display = self.query_one("#script-display", TextArea)
        script_content = script_display.text
        
        try:
            import pyperclip
            pyperclip.copy(script_content)
            self.wizard_app.show_success_message("Script Copied", "Complete job script copied to clipboard!")
        except ImportError:
            self.wizard_app.show_success_message(
                "Copy Script",
                "Script content displayed in text area - select and copy manually"
            )
    
    def _save_configuration(self) -> None:
        """Save the current configuration"""
        # Convert job config to dictionary for JSON serialization
        config_dict = {
            "job_type": self.job_config.job_type.value,
            "job_name": self.job_config.job_name,
            "command": self.job_config.command,
            "slots": self.job_config.slots,
            "queue": self.job_config.queue,
            "runtime_limit": self.job_config.runtime_limit,
            "runtime_estimate": self.job_config.runtime_estimate,
            "output_file": self.job_config.output_file,
            "error_file": self.job_config.error_file,
            "working_directory": self.job_config.working_directory,
            "email_notifications": self.job_config.email_notifications,
            "email_on_start": self.job_config.email_on_start,
            "x11_forwarding": self.job_config.x11_forwarding,
            "architecture_requirements": self.job_config.architecture_requirements,
            "license_requirements": self.job_config.license_requirements,
            "custom_resources": self.job_config.custom_resources,
            "environment_vars": self.job_config.environment_vars,
            "parallel_environment": self.job_config.parallel_environment,
        }
        
        # Add GPU config if present
        if self.job_config.gpu_config:
            config_dict["gpu_config"] = {
                "gpu_type": self.job_config.gpu_config.gpu_type,
                "num_gpus": self.job_config.gpu_config.num_gpus,
                "gpu_mode": self.job_config.gpu_config.gpu_mode.value,
                "mps": self.job_config.gpu_config.mps,
                "nvlink": self.job_config.gpu_config.nvlink,
                "min_memory": self.job_config.gpu_config.min_memory,
                "j_exclusive": self.job_config.gpu_config.j_exclusive,
            }
        
        # Add array config if enabled
        if self.job_config.array_config.enabled:
            config_dict["array_config"] = {
                "enabled": True,
                "start_index": self.job_config.array_config.start_index,
                "end_index": self.job_config.array_config.end_index,
                "step": self.job_config.array_config.step,
                "max_parallel": self.job_config.array_config.max_parallel,
            }
        
        # Create filename
        filename = f"{self.job_config.job_name or 'job_config'}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            self.wizard_app.show_success_message(
                "Configuration Saved",
                f"Job configuration saved to {filename}"
            )
        except Exception as e:
            self.wizard_app.show_error_message(
                "Save Failed",
                [f"Could not save configuration: {str(e)}"]
            )
    
    def _export_script(self) -> None:
        """Export the complete job script to a file"""
        script_display = self.query_one("#script-display", TextArea)
        script_content = script_display.text
        
        filename = f"{self.job_config.job_name or 'job'}_submit.sh"
        
        try:
            with open(filename, 'w') as f:
                f.write(script_content)
            
            self.wizard_app.show_success_message(
                "Script Exported",
                f"Job script exported to {filename}\\nMake it executable with: chmod +x {filename}"
            )
        except Exception as e:
            self.wizard_app.show_error_message(
                "Export Failed",
                [f"Could not export script: {str(e)}"]
            )
    
    def _restart_wizard(self) -> None:
        """Restart the wizard from the beginning"""
        # Reset the app state
        self.wizard_app.current_step = 0
        self.wizard_app.job_config = type(self.wizard_app.job_config)()  # Create new instance
        self.wizard_app.show_current_step()
    
    def validate(self) -> bool:
        """Validate the final configuration (always valid at this stage)"""
        return True