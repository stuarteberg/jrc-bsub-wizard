from textual.app import ComposeResult
from textual.containers import Container, Vertical, Grid
from textual.widgets import Static, Input, Checkbox, Markdown
from textual.widget import Widget

from ..utils.validators import JobValidator


class FilesScreen(Widget):
    """Screen for configuring file management options"""
    
    CSS = """
    .files-container {
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
    
    .files-section {
        background: $surface-lighten-1;
        padding: 2;
        margin: 1 0;
        border: solid $primary;
    }
    
    .files-grid {
        height: auto;
        grid-size: 1 3;
        grid-gutter: 1;
    }
    
    .file-item {
        background: $surface-lighten-2;
        padding: 1;
        border: solid $surface-lighten-3;
    }
    
    .storage-info {
        background: $surface-darken-1;
        color: $text;
        padding: 2;
        margin: 1 0;
        border: solid $warning;
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
    
    def __init__(self, wizard_app, job_config, cluster_config):
        super().__init__()
        self.wizard_app = wizard_app
        self.job_config = job_config
        self.cluster_config = cluster_config
    
    def compose(self) -> ComposeResult:
        """Create the file management layout"""
        with Container(classes="files-container"):
            with Vertical():
                yield Static(
                    "📁 Step 6: File Management",
                    classes="section-title"
                )
                
                yield Markdown("""
Configure input/output files and working directories. Proper file management is crucial for job execution and data organization.
""")
                
                # Storage information
                with Container(classes="storage-info"):
                    yield Static("💾 **Storage Options on Janelia Cluster**", classes="subsection-title")
                    yield Markdown("""
**Primary Storage Locations:**
- `/groups/...` - **PRFS** - Primary research file system (backed up)
- `/nrs/...` - **Non-redundant storage** - Large datasets (not backed up)  
- `/scratch/...` - **Node-local storage** - Temporary, high-speed I/O

**Best Practices:**
- Use absolute paths (starting with `/`)
- Store input data in `/groups` or `/nrs`
- Use `/scratch` for temporary files and intensive I/O
- Avoid storing large outputs in `/groups` (quota limited)
""")
                
                # File configuration
                with Container(classes="files-section"):
                    yield Static("📄 **Output Files**", classes="subsection-title")
                    
                    with Grid(classes="files-grid"):
                        with Container(classes="file-item"):
                            yield Static("Standard Output File (stdout):")
                            yield Input(
                                placeholder="/groups/yourlab/output.log",
                                id="output-file-input"
                            )
                            yield Static("💡 Leave empty to receive email with output", classes="help-text")
                        
                        with Container(classes="file-item"):
                            yield Static("Standard Error File (stderr):")
                            yield Input(
                                placeholder="/groups/yourlab/errors.log",
                                id="error-file-input"
                            )
                            yield Static("💡 Separate file for error messages", classes="help-text")
                        
                        with Container(classes="file-item"):
                            yield Static("Working Directory:")
                            yield Input(
                                placeholder="/groups/yourlab/project",
                                id="working-dir-input"
                            )
                            yield Static("💡 Directory where job will execute", classes="help-text")
                
                # Advanced file options
                with Container(classes="files-section"):
                    yield Static("⚙️ **Advanced File Options**", classes="subsection-title")
                    
                    yield Checkbox("Suppress email notifications (use /dev/null for output)", id="suppress-email-checkbox")
                    yield Static("💡 Useful for jobs that don't produce important output", classes="help-text")
                    
                    yield Markdown("""
**File Path Examples:**
- **Research data**: `/groups/yourlab/data/input.txt`
- **Large datasets**: `/nrs/yourlab/bigdata/dataset.h5`
- **Temporary files**: `/scratch/output_temp.txt`
- **Log files**: `/groups/yourlab/logs/job_$(date +%Y%m%d).log`

**Array Job Variables:**
- Use `$LSB_JOBINDEX` in paths for array jobs
- Example: `/groups/yourlab/output_$LSB_JOBINDEX.txt`
""")
    
    def on_mount(self) -> None:
        """Initialize the screen with current configuration"""
        # Set current values
        output_file_input = self.query_one("#output-file-input", Input)
        output_file_input.value = self.job_config.output_file or ""
        
        error_file_input = self.query_one("#error-file-input", Input)
        error_file_input.value = self.job_config.error_file or ""
        
        working_dir_input = self.query_one("#working-dir-input", Input)
        working_dir_input.value = self.job_config.working_directory or ""
        
        suppress_email_checkbox = self.query_one("#suppress-email-checkbox", Checkbox)
        suppress_email_checkbox.value = (self.job_config.output_file == "/dev/null")
        
        # Set intelligent defaults based on job type
        self._set_default_paths()
    
    def _set_default_paths(self) -> None:
        """Set intelligent default file paths"""
        output_file_input = self.query_one("#output-file-input", Input)
        error_file_input = self.query_one("#error-file-input", Input)
        
        # Only set defaults if fields are empty
        if not output_file_input.value and self.job_config.job_name:
            if self.job_config.array_config.enabled:
                output_file_input.placeholder = f"/groups/yourlab/{self.job_config.job_name}_$LSB_JOBINDEX.log"
                error_file_input.placeholder = f"/groups/yourlab/{self.job_config.job_name}_$LSB_JOBINDEX.err"
            else:
                output_file_input.placeholder = f"/groups/yourlab/{self.job_config.job_name}.log"
                error_file_input.placeholder = f"/groups/yourlab/{self.job_config.job_name}.err"
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input field changes"""
        if event.input.id == "output-file-input":
            self.job_config.output_file = event.value if event.value else None
            # Update suppress email checkbox
            suppress_checkbox = self.query_one("#suppress-email-checkbox", Checkbox)
            suppress_checkbox.value = (event.value == "/dev/null")
            
        elif event.input.id == "error-file-input":
            self.job_config.error_file = event.value if event.value else None
            
        elif event.input.id == "working-dir-input":
            self.job_config.working_directory = event.value if event.value else None
    
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox changes"""
        if event.checkbox.id == "suppress-email-checkbox":
            output_file_input = self.query_one("#output-file-input", Input)
            
            if event.value:
                # Set to /dev/null to suppress output
                output_file_input.value = "/dev/null"
                self.job_config.output_file = "/dev/null"
            else:
                # Clear the field so user can enter custom path
                output_file_input.value = ""
                self.job_config.output_file = None
    
    def _suggest_storage_location(self, file_type: str) -> str:
        """Suggest appropriate storage location based on file type"""
        suggestions = {
            "output": "/groups/yourlab/outputs/",
            "error": "/groups/yourlab/logs/", 
            "working": "/groups/yourlab/projects/",
            "scratch": "/scratch/",
            "data": "/nrs/yourlab/data/"
        }
        return suggestions.get(file_type, "/groups/yourlab/")
    
    def validate(self) -> bool:
        """Validate file configuration"""
        errors = []
        warnings = []
        
        # Validate output file path
        if self.job_config.output_file:
            valid, error = JobValidator.validate_file_path(self.job_config.output_file)
            if not valid:
                errors.append(f"Output file: {error}")
            elif not self.job_config.output_file.startswith(('/groups', '/nrs', '/scratch', '/dev')):
                warnings.append("Output file should typically be in /groups, /nrs, or /scratch")
        
        # Validate error file path
        if self.job_config.error_file:
            valid, error = JobValidator.validate_file_path(self.job_config.error_file)
            if not valid:
                errors.append(f"Error file: {error}")
            elif not self.job_config.error_file.startswith(('/groups', '/nrs', '/scratch', '/dev')):
                warnings.append("Error file should typically be in /groups, /nrs, or /scratch")
        
        # Validate working directory
        if self.job_config.working_directory:
            valid, error = JobValidator.validate_file_path(self.job_config.working_directory)
            if not valid:
                errors.append(f"Working directory: {error}")
            elif not self.job_config.working_directory.startswith(('/groups', '/nrs', '/scratch')):
                warnings.append("Working directory should typically be in /groups, /nrs, or /scratch")
        
        # Check for potential issues
        if self.job_config.output_file and self.job_config.error_file:
            if self.job_config.output_file == self.job_config.error_file:
                warnings.append("Output and error files are the same - outputs will be mixed")
        
        # Check for array job variable usage
        if self.job_config.array_config.enabled:
            files_to_check = [
                ("output file", self.job_config.output_file),
                ("error file", self.job_config.error_file)
            ]
            
            for file_type, file_path in files_to_check:
                if file_path and file_path != "/dev/null" and "$LSB_JOBINDEX" not in file_path:
                    warnings.append(f"Array job {file_type} should include $LSB_JOBINDEX to avoid conflicts")
        
        # Show errors
        if errors:
            self.wizard_app.show_error_message("File Configuration Errors", errors)
            return False
        
        # Show warnings
        if warnings:
            self.wizard_app.show_warning_message("File Configuration Warnings", "\\n".join(warnings))
        
        return True