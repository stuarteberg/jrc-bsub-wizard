from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, Input, Select
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.reactive import reactive
import json
import os
from pathlib import Path

from .models.job_config import JobConfiguration, JobType
from .models.cluster_info import ClusterConfiguration
from .utils.command_builder import BsubCommandBuilder
from .screens.welcome import WelcomeScreen
from .screens.job_type import JobTypeScreen
from .screens.resources import ResourcesScreen
from .screens.queue import QueueScreen
from .screens.runtime import RuntimeScreen
from .screens.files import FilesScreen
from .screens.advanced import AdvancedScreen
from .screens.review import ReviewScreen


class BsubWizardApp(App):
    """Main application for the BSub Wizard"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    .wizard-container {
        height: 100%;
        background: $surface;
    }
    
    .header-container {
        height: 3;
        background: $primary;
        color: $text;
        padding: 1;
    }
    
    .content-container {
        height: 1fr;
        background: $surface;
    }
    
    .footer-container {
        height: 3;
        background: $primary-darken-1;
    }
    
    .progress-bar {
        height: 1;
        background: $primary-lighten-1;
        margin-top: 1;
    }
    
    .progress-fill {
        height: 100%;
        background: $accent;
    }
    
    .navigation-buttons {
        height: 3;
        background: $surface-lighten-1;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
        min-width: 12;
    }
    
    Button.primary {
        background: $accent;
        color: $text;
    }
    
    Button.secondary {
        background: $surface-lighten-2;
        color: $text;
    }
    
    .error-message {
        background: $error;
        color: $text;
        padding: 1;
        margin: 1;
    }
    
    .warning-message {
        background: $warning;
        color: $text;
        padding: 1;
        margin: 1;
    }
    
    .success-message {
        background: $success;
        color: $text;
        padding: 1;
        margin: 1;
    }
    
    .dialog-container {
        background: $surface;
        border: solid $primary;
        padding: 2;
        margin: 2;
        width: 60%;
        height: auto;
        max-width: 80;
    }
    
    .dialog-title {
        text-align: center;
        background: $primary;
        color: $text;
        padding: 1;
        margin: 0 0 2 0;
    }
    
    .help-container {
        background: $surface;
        border: solid $primary;
        padding: 2;
        margin: 2;
        width: 80%;
        height: 80%;
        max-width: 120;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("f1", "help", "Help"),
        Binding("ctrl+s", "save_config", "Save Config"),
        Binding("ctrl+l", "load_config", "Load Config"),
        Binding("escape", "back", "Back"),
        Binding("enter", "next", "Next"),
    ]
    
    TITLE = "BSub Wizard - Janelia Compute Cluster Job Submission"
    SUB_TITLE = "Interactive guide for creating bsub commands"
    
    # Reactive attributes
    current_step = reactive(0)
    total_steps = reactive(8)
    
    def __init__(self):
        super().__init__()
        
        # Initialize configuration objects
        self.cluster_config = ClusterConfiguration()
        self.job_config = JobConfiguration()
        self.command_builder = BsubCommandBuilder(self.cluster_config.general_config)
        
        # Define wizard steps
        self.steps = [
            ("Welcome", WelcomeScreen),
            ("Job Type", JobTypeScreen),
            ("Resources", ResourcesScreen),
            ("Queue Selection", QueueScreen),
            ("Runtime & Scheduling", RuntimeScreen),
            ("File Management", FilesScreen),
            ("Advanced Options", AdvancedScreen),
            ("Review & Generate", ReviewScreen),
        ]
        
        self.total_steps = len(self.steps)
        
        # Track if configuration has been modified
        self.config_modified = False
    
    def compose(self) -> ComposeResult:
        """Create the main UI layout"""
        yield Header(show_clock=True)
        
        with Container(classes="wizard-container"):
            with Vertical():
                # Progress indicator
                with Container(classes="header-container"):
                    yield Static(self._get_progress_text(), id="progress-text")
                    with Container(classes="progress-bar"):
                        yield Static("", id="progress-fill", classes="progress-fill")
                
                # Main content area
                with Container(classes="content-container", id="content-area"):
                    yield Static("Loading...", id="screen-content")
                
                # Navigation buttons
                with Horizontal(classes="navigation-buttons"):
                    yield Button("← Back", id="back-button", classes="secondary")
                    yield Button("Next →", id="next-button", classes="primary")
                    yield Button("Save Config", id="save-button", classes="secondary")
                    yield Button("Load Config", id="load-button", classes="secondary")
                    yield Button("Help", id="help-button", classes="secondary")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the application"""
        self.show_current_step()
        self.update_navigation_buttons()
        self.update_progress()
    
    def _get_progress_text(self) -> str:
        """Get the current progress text"""
        if self.current_step < len(self.steps):
            step_name = self.steps[self.current_step][0]
            return f"Step {self.current_step + 1} of {self.total_steps}: {step_name}"
        else:
            return f"Step {self.total_steps} of {self.total_steps}: Complete"
    
    def update_progress(self) -> None:
        """Update the progress bar and text"""
        progress_text = self.query_one("#progress-text", Static)
        progress_text.update(self._get_progress_text())
        
        progress_fill = self.query_one("#progress-fill", Static)
        progress_percentage = (self.current_step / self.total_steps) * 100
        progress_fill.styles.width = f"{progress_percentage}%"
    
    def update_navigation_buttons(self) -> None:
        """Update navigation button states"""
        back_button = self.query_one("#back-button", Button)
        next_button = self.query_one("#next-button", Button)
        
        # Back button
        back_button.disabled = self.current_step == 0
        
        # Next button
        if self.current_step == self.total_steps - 1:
            next_button.label = "Generate Command"
        else:
            next_button.label = "Next →"
    
    def show_current_step(self) -> None:
        """Display the current wizard step"""
        if self.current_step >= len(self.steps):
            return
        
        step_name, screen_class = self.steps[self.current_step]
        
        # Create and show the screen
        screen = screen_class(
            wizard_app=self,
            job_config=self.job_config,
            cluster_config=self.cluster_config
        )
        
        content_area = self.query_one("#content-area")
        content_area.remove_children()
        content_area.mount(screen)
        
        self.update_progress()
        self.update_navigation_buttons()
    
    def action_next(self) -> None:
        """Move to the next step"""
        # Validate current step
        if not self.validate_current_wizard_step():
            return
        
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self.show_current_step()
        else:
            # Final step - generate command
            self._generate_final_command()
    
    def action_back(self) -> None:
        """Move to the previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.show_current_step()
    
    def action_save_config(self) -> None:
        """Save current configuration"""
        self.push_screen(SaveConfigScreen(self.job_config))
    
    def action_load_config(self) -> None:
        """Load a saved configuration"""
        self.push_screen(LoadConfigScreen(self))
    
    def action_help(self) -> None:
        """Show help information"""
        self.push_screen(HelpScreen())
    
    def validate_current_wizard_step(self) -> bool:
        """Validate the current step before proceeding"""
        try:
            # Get the current screen and validate it
            content_area = self.query_one("#content-area")
            if content_area.children:
                current_screen = content_area.children[0]
                if hasattr(current_screen, 'validate'):
                    return current_screen.validate()
        except Exception:
            # If we can't query the DOM (app not running), just return True
            pass
        return True
    
    def _generate_final_command(self) -> None:
        """Generate the final bsub command"""
        # Validate the complete configuration
        is_valid, errors = self.job_config.is_valid()
        
        if not is_valid:
            self.show_error_message("Configuration errors", errors)
            return
        
        # Generate the command
        command = self.command_builder.build_command(self.job_config)
        cost = self.command_builder.estimate_cost(self.job_config)
        
        # Show the final result
        self.push_screen(ReviewScreen(
            wizard_app=self,
            job_config=self.job_config,
            cluster_config=self.cluster_config,
            final_command=command,
            estimated_cost=cost
        ))
    
    def show_error_message(self, title: str, messages: list) -> None:
        """Display error messages to the user"""
        error_text = "\\n".join(messages)
        self.push_screen(ErrorScreen(title, error_text))
    
    def show_warning_message(self, title: str, message: str) -> None:
        """Display warning message to the user"""
        self.push_screen(WarningScreen(title, message))
    
    def show_success_message(self, title: str, message: str) -> None:
        """Display success message to the user"""
        self.push_screen(SuccessScreen(title, message))
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "next-button":
            self.action_next()
        elif button_id == "back-button":
            self.action_back()
        elif button_id == "save-button":
            self.action_save_config()
        elif button_id == "load-button":
            self.action_load_config()
        elif button_id == "help-button":
            self.action_help()


class ErrorScreen(ModalScreen):
    """Modal screen for displaying error messages"""
    
    def __init__(self, title: str, message: str):
        super().__init__()
        self.title = title
        self.message = message
    
    def compose(self) -> ComposeResult:
        with Container(classes="error-message"):
            yield Static(f"❌ {self.title}", classes="error-title")
            yield Static(self.message)
            yield Button("OK", id="ok-button", classes="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-button":
            self.dismiss()


class WarningScreen(ModalScreen):
    """Modal screen for displaying warning messages"""
    
    def __init__(self, title: str, message: str):
        super().__init__()
        self.title = title
        self.message = message
    
    def compose(self) -> ComposeResult:
        with Container(classes="warning-message"):
            yield Static(f"⚠️ {self.title}", classes="warning-title")
            yield Static(self.message)
            yield Button("OK", id="ok-button", classes="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-button":
            self.dismiss()


class SuccessScreen(ModalScreen):
    """Modal screen for displaying success messages"""
    
    def __init__(self, title: str, message: str):
        super().__init__()
        self.title = title
        self.message = message
    
    def compose(self) -> ComposeResult:
        with Container(classes="success-message"):
            yield Static(f"✅ {self.title}", classes="success-title")
            yield Static(self.message)
            yield Button("OK", id="ok-button", classes="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok-button":
            self.dismiss()


class SaveConfigScreen(ModalScreen):
    """Modal screen for saving configuration"""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", priority=True),
    ]
    
    def __init__(self, job_config):
        super().__init__()
        self.job_config = job_config
    
    def compose(self) -> ComposeResult:
        with Container(classes="dialog-container"):
            yield Static("💾 Save Configuration", classes="dialog-title")
            yield Static("Enter a name for this configuration:")
            yield Input(placeholder="e.g., ml_training_config", id="config-name-input")
            with Horizontal():
                yield Button("Cancel", id="modal-cancel-button", classes="secondary")
                yield Button("Save", id="modal-save-button", classes="primary")
    
    def on_mount(self) -> None:
        """Focus the input field when the screen loads"""
        try:
            input_field = self.query_one("#config-name-input", Input)
            input_field.focus()
        except:
            pass
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "modal-cancel-button":
            self.dismiss()
        elif event.button.id == "modal-save-button":
            self._save_config()
    
    def _save_config(self) -> None:
        """Save the configuration to file"""
        try:
            name_input = self.query_one("#config-name-input", Input)
            config_name = name_input.value.strip()
            
            if not config_name:
                self.app.push_screen(ErrorScreen("Invalid Name", "Please enter a configuration name"))
                return
            
            # Create configs directory if it doesn't exist
            configs_dir = Path("configs")
            configs_dir.mkdir(exist_ok=True)
            
            # Save configuration
            config_file = configs_dir / f"{config_name}.json"
            config_data = self.job_config.to_dict()
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # First dismiss this modal, then show success
            self.dismiss()
            self.app.push_screen(SuccessScreen(
                "Configuration Saved", 
                f"Configuration saved as '{config_name}'"
            ))
            
        except Exception as e:
            self.app.push_screen(ErrorScreen("Save Error", f"Failed to save configuration: {str(e)}"))


class LoadConfigScreen(ModalScreen):
    """Modal screen for loading configuration"""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", priority=True),
    ]
    
    def __init__(self, wizard_app):
        super().__init__()
        self.wizard_app = wizard_app
    
    def compose(self) -> ComposeResult:
        with Container(classes="dialog-container"):
            yield Static("📂 Load Configuration", classes="dialog-title")
            yield Static("Select a saved configuration:")
            yield Select(self._get_config_options(), id="config-select")
            with Horizontal():
                yield Button("Cancel", id="modal-cancel-button", classes="secondary")
                yield Button("Load", id="modal-load-button", classes="primary")
    
    def _get_config_options(self):
        """Get list of available configuration files"""
        configs_dir = Path("configs")
        if not configs_dir.exists():
            return [("No saved configurations", "")]
        
        config_files = list(configs_dir.glob("*.json"))
        if not config_files:
            return [("No saved configurations", "")]
        
        options = []
        for config_file in config_files:
            name = config_file.stem
            options.append((name, str(config_file)))
        
        return options
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "modal-cancel-button":
            self.dismiss()
        elif event.button.id == "modal-load-button":
            self._load_config()
    
    def _load_config(self) -> None:
        """Load the selected configuration"""
        config_select = self.query_one("#config-select", Select)
        config_file_path = config_select.value
        
        if not config_file_path:
            self.app.push_screen(ErrorScreen("No Selection", "Please select a configuration to load"))
            return
        
        try:
            with open(config_file_path, 'r') as f:
                config_data = json.load(f)
            
            # Load configuration into job_config
            self.wizard_app.job_config.from_dict(config_data)
            
            # Refresh current step to show loaded values
            self.wizard_app.show_current_step()
            
            config_name = Path(config_file_path).stem
            
            # First dismiss this modal, then show success
            self.dismiss()
            self.app.push_screen(SuccessScreen(
                "Configuration Loaded", 
                f"Configuration '{config_name}' loaded successfully"
            ))
            
        except Exception as e:
            self.app.push_screen(ErrorScreen("Load Error", f"Failed to load configuration: {str(e)}"))


class HelpScreen(ModalScreen):
    """Modal screen for displaying help information"""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close", priority=True),
    ]
    
    def compose(self) -> ComposeResult:
        with Container(classes="help-container"):
            yield Static("❓ BSub Wizard Help", classes="dialog-title")
            yield Static("""
**Navigation:**
• Use Next/Back buttons or Enter/Escape keys
• Arrow keys navigate within selections
• Tab to move between form fields

**Steps:**
1. **Welcome** - Overview and getting started
2. **Job Type** - Choose CPU, GPU, Interactive, or MPI
3. **Resources** - Configure CPU/GPU allocation
4. **Queue** - Select appropriate cluster queue
5. **Runtime** - Set time limits and scheduling
6. **Files** - Specify input/output files and paths
7. **Advanced** - Environment variables and special options
8. **Review** - Final command review and submission

**Configuration:**
• Save/Load buttons store your settings
• Configurations saved to 'configs/' directory

**Tips:**
• Start with recommended defaults
• Check resource estimates before proceeding
• Use 'short' queue for testing (1 hour limit)

For more help, see: https://wiki.int.janelia.org/
            """)
            yield Button("Close", id="close-button", classes="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close-button":
            self.dismiss()


def run_wizard():
    """Entry point to run the BSub Wizard"""
    app = BsubWizardApp()
    app.run()