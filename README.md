# BSub Wizard

Interactive wizard for creating LSF `bsub` commands for the Janelia Research Campus compute cluster.

![BSub Wizard Demo](https://via.placeholder.com/800x400/1e1e1e/00ff00?text=BSub+Wizard+Demo)

## Overview

The BSub Wizard is a modern, terminal-based application that guides users through creating properly formatted `bsub` commands for job submission on the Janelia Research Campus compute cluster. It eliminates the complexity of remembering LSF syntax and cluster-specific options while ensuring optimal resource allocation and cost efficiency.

## Features

### 🎯 **Guided Workflow**
- **8-step wizard** covering all aspects of job submission
- **Smart defaults** based on job type and cluster best practices
- **Real-time validation** with helpful error messages
- **Context-sensitive help** explaining each option

### 🖥️ **Job Types Supported**
- **CPU Jobs** - General computational tasks
- **GPU Jobs** - ML/AI workloads with comprehensive GPU selection
- **Interactive Sessions** - Development and debugging
- **MPI/Parallel Jobs** - Multi-node parallel processing

### ⚙️ **Resource Configuration**
- **CPU allocation** with automatic memory calculation (15GB per slot)
- **GPU selection** from GH200, H200, H100, A100, L4, T4
- **Architecture requirements** (AVX2, AVX512, AMX)
- **Queue optimization** with cost and runtime information

### 📊 **Advanced Features**
- **Cost estimation** before job submission
- **Array job support** with automatic task calculation
- **File management** with Janelia storage integration
- **Environment variables** and license management
- **Command preview** and script generation

### 💾 **Data Management**
- **Configuration saving/loading** for reusable job templates
- **Script export** for integration with existing workflows
- **Copy to clipboard** functionality
- **JSON configuration format** for automation

## Installation

### Prerequisites
- Python 3.8 or higher
- Terminal with Unicode support
- Access to Janelia compute cluster

### Install from Source
```bash
git clone https://github.com/janelia/bsub-wizard.git
cd bsub-wizard
pip install -r requirements.txt
python main.py
```

### Install as Package
```bash
pip install bsub-wizard
bsub-wizard
```

## Quick Start

### 1. Launch the Wizard
```bash
python main.py
```

### 2. Follow the Steps
1. **Welcome** - Choose quick start or custom configuration
2. **Job Type** - Select CPU, GPU, Interactive, or MPI
3. **Resources** - Configure cores, memory, and GPUs
4. **Queue** - Select optimal queue with cost information
5. **Runtime** - Set time limits and job scheduling
6. **Files** - Configure input/output and working directories
7. **Advanced** - Set architecture, licenses, environment variables
8. **Review** - Generate and copy the final command

### 3. Use Generated Command
```bash
# Example output
bsub -J "my_ml_job" -n 12 -gpu "num=1:gmodel=NVIDIAA100_SXM4_80GB" -q gpu_a100 -W 4:00 -o /groups/mylab/output.log 'python train.py'
```

## Cluster Information

### Available Resources

#### **CPU Nodes**
- **Sky Lake (e10)**: 48 cores, 768GB RAM per node
- **Cascade Lake (h07)**: 48 cores, 768GB RAM per node  
- **Sapphire Rapids (H06)**: 64 cores, 1TB RAM per node

#### **GPU Types**
| GPU Model | VRAM | Slots/GPU | Cost/Hour | Best For |
|-----------|------|-----------|-----------|----------|
| GH200 Super Chip | 96GB | 72 | $0.80 | Cutting-edge AI research |
| H200 SXM5 | 141GB | 12 | $0.80 | Large model training |
| H100 SXM5 | 80GB | 12 | $0.50 | High-performance ML |
| A100 SXM4 | 80GB | 12 | $0.20 | General ML/AI workloads |
| Tesla L4 | 24GB | 8-64 | $0.10 | Cost-effective inference |
| Tesla T4 | 16GB | 48 | $0.10 | Development/testing |

#### **Queue Types**
- **interactive** - Real-time sessions (8h default, 48h max)
- **local** - Long-running CPU jobs (30 days max)
- **short** - Quick jobs under 1 hour
- **gpu_*** - Specialized GPU queues by hardware type
- **mpi** - Multi-node parallel processing

### Storage Locations
- **`/groups/`** - Primary research file system (backed up)
- **`/nrs/`** - Non-redundant storage for large datasets
- **`/scratch/`** - Node-local high-speed temporary storage

## Examples

### CPU Job
```bash
bsub -J "data_analysis" -n 8 -q local -W 12:00 -o /groups/mylab/analysis.log 'python analyze_data.py'
```

### GPU Training Job
```bash
bsub -J "model_training" -n 12 -gpu "num=1:gmodel=NVIDIAA100_SXM4_80GB" -q gpu_a100 -W 24:00 -o /groups/mylab/training.log 'python train_model.py'
```

### Interactive Session
```bash
bsub -n 4 -W 8:00 -Is -XF /bin/bash
```

### Array Job
```bash
bsub -J "parallel_analysis[1-100]%10" -n 4 -q local -o /groups/mylab/output_%I.log 'python process.py $LSB_JOBINDEX'
```

## Configuration Files

### Saving Configurations
The wizard can save job configurations as JSON files for reuse:

```json
{
  "job_type": "gpu",
  "job_name": "my_training_job",
  "slots": 12,
  "queue": "gpu_a100",
  "runtime_limit": "24:00",
  "gpu_config": {
    "gpu_type": "NVIDIAA100_SXM4_80GB",
    "num_gpus": 1,
    "gpu_mode": "exclusive_process"
  },
  "command": "python train.py"
}
```

### Loading Configurations
```bash
python main.py --config my_job_config.json
```

## Keyboard Shortcuts

- **Enter** - Next step
- **Escape** - Previous step
- **Ctrl+S** - Save configuration
- **Ctrl+L** - Load configuration
- **F1** - Help
- **Q** or **Ctrl+C** - Quit

## Advanced Usage

### Environment Variables
Set custom environment variables for your jobs:
```bash
export CUDA_VISIBLE_DEVICES=0
export OMP_NUM_THREADS=4
```

### Custom Resource Requirements
Use LSF resource expressions:
```bash
-R"select[mem>64000]"
-R"rusage[idl=6]"
```

### Architecture Targeting
```bash
-R"select[avx512]"  # Require AVX512 support
```

## Troubleshooting

### Common Issues

#### "Permission Denied" Errors
- Ensure your account is enabled for cluster access
- Submit a helpdesk ticket for account activation

#### Jobs Not Starting
- Check queue limits and availability
- Verify resource requirements are reasonable
- Use `bjobs` to monitor job status

#### High Costs
- Review GPU selection (L4/T4 are more economical)
- Set appropriate runtime limits
- Consider using `short` queue for quick jobs

### Getting Help

1. **Built-in Help** - Press F1 in the wizard
2. **Cluster Documentation** - Available on Janelia wiki
3. **Scientific Computing Team** - Submit helpdesk ticket
4. **GitHub Issues** - Report bugs and feature requests

## Development

### Setting Up Development Environment
```bash
git clone https://github.com/janelia/bsub-wizard.git
cd bsub-wizard
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black wizard/
flake8 wizard/
mypy wizard/
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Areas for Contribution
- Additional job templates
- Queue optimization algorithms
- Integration with other cluster tools
- Documentation improvements
- Testing and bug reports

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Janelia Scientific Computing Team** for cluster expertise
- **Textual framework** for the excellent TUI capabilities
- **Janelia Research Campus** for supporting open source development

## Changelog

### Version 1.0.0
- Initial release with full wizard functionality
- Support for all Janelia cluster resources
- Comprehensive validation and cost estimation
- Configuration save/load capabilities
- Complete job script generation

---

**Note**: This tool is specifically designed for the Janelia Research Campus compute cluster. For other LSF clusters, configuration may need to be adapted.

For the latest updates and documentation, visit: https://github.com/janelia/bsub-wizard