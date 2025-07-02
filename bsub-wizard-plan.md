# BSub Wizard Implementation Plan

## Project Overview

Create a Python-based text user interface (TUI) wizard that guides users through the various options available for the LSF `bsub` command on the Janelia Research Campus compute cluster. The wizard will simplify job submission by providing an interactive interface that constructs the appropriate `bsub` command based on user selections.

## 1. Framework Selection

### Recommended: Textual
- **Primary choice**: Textual (built on Rich)
- **Rationale**: 
  - Modern, actively developed framework with excellent documentation
  - CSS-like styling system familiar to web developers
  - Built-in widgets for forms, buttons, and interactive elements
  - Cross-platform compatibility
  - 16.7M color support and smooth animations
  - Can run in terminal and potentially web browser
  - Strong community and commercial backing

### Alternative Options Considered:
- **PyTermGUI**: Good alternative with mouse support and modular widgets
- **Rich**: Lower-level but could be used for simpler interfaces
- **Python Prompt Toolkit**: Better for command-line interfaces than full TUIs
- **urwid**: Mature but less modern API

## 2. Application Architecture

### Core Components

```
bsub-wizard/
├── main.py                 # Entry point and main application
├── wizard/
│   ├── __init__.py
│   ├── app.py             # Main Textual application class
│   ├── screens/           # Different wizard screens
│   │   ├── __init__.py
│   │   ├── welcome.py     # Welcome/intro screen
│   │   ├── job_type.py    # Job type selection (CPU/GPU/Interactive)
│   │   ├── resources.py   # Resource allocation (cores, memory, GPUs)
│   │   ├── queue.py       # Queue selection
│   │   ├── runtime.py     # Runtime and scheduling options
│   │   ├── files.py       # Input/output file configuration
│   │   ├── advanced.py    # Advanced options
│   │   └── review.py      # Command review and generation
│   ├── widgets/           # Custom widgets
│   │   ├── __init__.py
│   │   ├── resource_selector.py
│   │   ├── gpu_configurator.py
│   │   └── command_preview.py
│   ├── models/            # Data models
│   │   ├── __init__.py
│   │   ├── job_config.py  # Job configuration data class
│   │   └── cluster_info.py # Cluster specifications
│   └── utils/
│       ├── __init__.py
│       ├── command_builder.py # BSub command generation
│       └── validators.py      # Input validation
├── data/
│   ├── cluster_config.json    # Cluster configuration data
│   └── queue_definitions.json # Queue specifications
├── tests/
│   ├── __init__.py
│   ├── test_command_builder.py
│   ├── test_validators.py
│   └── test_integration.py
├── requirements.txt
├── setup.py
└── README.md
```

## 3. User Flow Design

### Step-by-Step Wizard Flow

1. **Welcome Screen**
   - Brief introduction to the wizard
   - Navigation instructions
   - Option to load previous configuration

2. **Job Type Selection**
   - CPU job
   - GPU job  
   - Interactive session
   - MPI/parallel job

3. **Resource Configuration** (Dynamic based on job type)
   - **CPU Jobs**: Number of slots (1-64), memory requirements
   - **GPU Jobs**: GPU type selection, number of GPUs, slots per GPU
   - **Interactive**: Session duration, resource limits

4. **Queue Selection** (Filtered based on job type)
   - Display available queues with descriptions
   - Show queue limitations and billing information
   - Auto-suggest optimal queue based on requirements

5. **Runtime and Scheduling**
   - Job name input (with validation)
   - Runtime limits (hard and estimated)
   - Email notifications
   - Job arrays (if applicable)

6. **File Management**
   - Input files/directories
   - Output file configuration
   - Working directory
   - X11 forwarding (for interactive jobs)

7. **Advanced Options** (Optional)
   - Architecture requirements (AVX2, AVX512)
   - Software licenses (IDL, etc.)
   - Custom resource requirements
   - Environment variables

8. **Review and Generate**
   - Display complete job configuration
   - Show generated `bsub` command
   - Options to save configuration, copy command, or submit job
   - Validation and warnings

## 4. Technical Implementation Details

### 4.1 Data Models

```python
@dataclass
class JobConfiguration:
    job_type: str  # 'cpu', 'gpu', 'interactive', 'mpi'
    job_name: str
    slots: int
    queue: str
    runtime_limit: Optional[str]
    runtime_estimate: Optional[str]
    gpu_config: Optional[GPUConfiguration]
    output_file: Optional[str]
    error_file: Optional[str]
    email_notifications: bool
    command: str
    working_directory: Optional[str]
    advanced_options: Dict[str, Any]

@dataclass 
class GPUConfiguration:
    gpu_type: str
    num_gpus: int
    gpu_mode: str  # 'shared' or 'exclusive_process'
    mps: bool
    nvlink: bool
    min_memory: Optional[str]
```

### 4.2 Command Generation Engine

```python
class BsubCommandBuilder:
    def __init__(self, cluster_config: Dict):
        self.cluster_config = cluster_config
    
    def build_command(self, config: JobConfiguration) -> str:
        """Generate the complete bsub command from configuration"""
        
    def validate_configuration(self, config: JobConfiguration) -> List[str]:
        """Validate configuration and return list of warnings/errors"""
        
    def estimate_cost(self, config: JobConfiguration) -> float:
        """Calculate estimated cost for the job"""
```

### 4.3 Smart Defaults and Validation

- **Intelligent defaults**: Based on job type and common usage patterns
- **Real-time validation**: Check resource limits, queue availability, naming conventions
- **Cost estimation**: Show estimated billing cost before submission
- **Resource optimization**: Suggest optimal slot/GPU combinations
- **Queue recommendation**: Auto-suggest best queue based on requirements

### 4.4 Configuration Persistence

- Save/load job configurations as JSON files
- Recent configurations history
- Template system for common job types
- Export configurations for sharing

## 5. Key Features

### 5.1 Interactive Elements
- **Dynamic forms** that adapt based on selections
- **Real-time command preview** showing the generated bsub command
- **Context-sensitive help** explaining each option
- **Visual resource calculator** showing memory/core relationships
- **Queue status integration** (if cluster status API available)

### 5.2 User Experience Enhancements
- **Keyboard navigation** with vim-like bindings
- **Progress indicator** showing wizard completion
- **Undo/back functionality** to revise previous steps
- **Search/filter** for queue and GPU type selection
- **Smart suggestions** based on cluster usage patterns

### 5.3 Advanced Capabilities
- **Configuration templates** for common job patterns
- **Batch job support** for array jobs
- **Integration hooks** for job submission and monitoring
- **Export options** (command, script, configuration file)

## 6. Implementation Phases

### Phase 1: Core Framework (Week 1-2)
- Set up Textual application structure
- Implement basic navigation between screens
- Create fundamental data models
- Build command generation engine

### Phase 2: Basic Wizard Flow (Week 3-4)
- Implement all wizard screens with basic functionality
- Add input validation and error handling
- Create job configuration persistence
- Test basic CPU job workflow

### Phase 3: GPU and Advanced Features (Week 5-6)
- Implement GPU configuration interface
- Add advanced options and array job support
- Create interactive session handling
- Implement configuration templates

### Phase 4: Polish and Testing (Week 7-8)
- Comprehensive testing and bug fixes
- Performance optimization
- Documentation and help system
- User testing and feedback integration

## 7. Installation and Deployment

### Requirements
```txt
textual>=0.40.0
rich>=13.0.0
pydantic>=2.0.0
click>=8.0.0
```

### Installation Methods
1. **pip install**: Standard Python package installation
2. **conda package**: For Anaconda/Miniconda users
3. **Standalone executable**: Using PyInstaller for non-Python users
4. **Module loading**: Integration with cluster module system

### Usage
```bash
# Basic usage
bsub-wizard

# Load existing configuration
bsub-wizard --config my_job.json

# Generate command only (no interactive mode)
bsub-wizard --template gpu_training --slots 48 --output-command-only
```

## 8. Testing Strategy

### Unit Tests
- Command generation logic
- Input validation functions  
- Configuration serialization/deserialization

### Integration Tests
- Complete wizard workflows
- Screen transitions and data flow
- File handling and persistence

### User Acceptance Testing
- Test with actual cluster users
- Verify generated commands work correctly
- Usability testing with domain experts

## 9. Documentation Plan

### User Documentation
- **Getting Started Guide**: Installation and basic usage
- **Complete Reference**: All options and features explained
- **Common Workflows**: Examples for typical job types
- **Troubleshooting**: Common issues and solutions

### Developer Documentation  
- **Architecture Overview**: Code organization and design decisions
- **API Reference**: Public interfaces and extension points
- **Contributing Guide**: Development setup and contribution process

## 10. Future Enhancements

### Phase 2 Features
- **Web interface**: Textual's browser support for remote access
- **Job monitoring**: Integration with cluster status and job tracking
- **Cluster integration**: Direct job submission and status checking
- **Template sharing**: Community-contributed job templates
- **Usage analytics**: Track common patterns and optimize defaults

### Advanced Features
- **AI assistance**: ML-powered job optimization suggestions
- **Resource forecasting**: Predict job completion times and costs
- **Workflow integration**: Support for complex multi-job workflows
- **API integration**: RESTful API for programmatic access

## Conclusion

This plan provides a comprehensive roadmap for creating a user-friendly bsub wizard that will significantly improve the job submission experience on the Janelia compute cluster. The modular architecture allows for incremental development and future enhancements, while the choice of Textual ensures a modern, maintainable codebase with excellent user experience capabilities.