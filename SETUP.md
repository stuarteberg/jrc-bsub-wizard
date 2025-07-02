# BSub Wizard Setup and Usage

## Quick Start with Pixi

The BSub Wizard is now set up with a pixi environment for easy dependency management and execution.

### Prerequisites
- Python 3.8+
- pixi package manager (already installed)

### Getting Started

1. **Initialize the environment** (already done):
   ```bash
   pixi init
   ```

2. **Install dependencies** (already done):
   ```bash
   pixi add textual rich click pyperclip
   ```

3. **Run the wizard**:
   ```bash
   pixi run start
   ```

### Available Commands

- **Start the wizard**: `pixi run start`
- **Run basic tests**: `pixi run test`
- **Test app structure**: `pixi run test-app`
- **Show help**: `pixi run help`

### Example Usage

```bash
# Start the interactive wizard
pixi run start

# Test that everything is working
pixi run test

# Check application structure
pixi run test-app
```

## What the Wizard Does

The BSub Wizard guides you through creating LSF `bsub` commands for the Janelia Research Campus compute cluster:

### 8-Step Process
1. **Welcome** - Introduction and quick start options
2. **Job Type** - Select CPU, GPU, Interactive, or MPI jobs
3. **Resources** - Configure cores, memory, and GPU specifications
4. **Queue Selection** - Choose optimal queue with cost information
5. **Runtime & Scheduling** - Set time limits and job parameters
6. **File Management** - Configure I/O files and working directories
7. **Advanced Options** - Set licenses, environment variables, etc.
8. **Review & Generate** - Preview and export the final command

### Example Generated Commands

**CPU Job:**
```bash
bsub -J "my_analysis" -n 8 -q local -W 4:00 -o /dev/null 'python analyze_data.py'
```

**GPU Job:**
```bash
bsub -J "ml_training" -n 12 -q gpu_a100 -gpu "num=1:gmodel=NVIDIAA100_SXM4_80GB" -W 12:00 -o /dev/null 'python train_model.py'
```

**Interactive Session:**
```bash
bsub -n 4 -W 8:00 -Is -XF /bin/bash
```

## Cluster Resources Supported

### CPU Nodes
- **Sky Lake**: 48 cores, 768GB RAM
- **Cascade Lake**: 48 cores, 768GB RAM  
- **Sapphire Rapids**: 64 cores, 1TB RAM

### GPU Types
- **GH200**: 96GB VRAM ($0.80/hour)
- **H200**: 141GB VRAM ($0.80/hour)
- **H100**: 80GB VRAM ($0.50/hour)
- **A100**: 80GB VRAM ($0.20/hour)
- **L4**: 24GB VRAM ($0.10/hour)
- **T4**: 16GB VRAM ($0.10/hour)

### Queue Types
- **interactive**: Real-time sessions
- **local**: Long-running CPU jobs
- **short**: Quick jobs (<1 hour)
- **gpu_***: GPU-specific queues
- **mpi**: Multi-node parallel processing

## Features

✅ **Complete Implementation**
- All 8 wizard screens implemented
- Full Janelia cluster configuration
- Real-time cost estimation
- Input validation and error handling
- Configuration save/load
- Command generation and export

✅ **User Experience**
- Modern TUI interface with Textual
- Progress tracking and navigation
- Quick start templates
- Context-sensitive help
- Keyboard shortcuts

✅ **Cluster Integration**
- All Janelia queues and GPU types
- Storage path recommendations
- Architecture requirements
- License management
- Array job support

## Troubleshooting

### Common Issues

1. **Dependencies not found**:
   - Make sure you're using `pixi run` commands
   - Verify pixi environment is active

2. **Terminal compatibility**:
   - Use a modern terminal with Unicode support
   - Ensure terminal size is at least 80x24

3. **Validation errors**:
   - Check job name format (no spaces, no reserved words)
   - Verify time format (MM or HH:MM)
   - Ensure file paths are absolute

### Getting Help

- Run `pixi run help` for command-line options
- Press `F1` in the wizard for context help
- Check generated commands in the review screen
- Refer to Janelia cluster documentation for LSF details

## Development

### Project Structure
```
wizard/
├── models/          # Data models (job config, cluster info)
├── screens/         # 8 wizard screens
├── utils/           # Command builder and validators  
├── widgets/         # Custom UI components
└── app.py          # Main Textual application
```

### Running Tests
```bash
# Basic component tests
pixi run test

# Application structure test
pixi run test-app
```

All tests should pass, confirming the wizard is ready for use!