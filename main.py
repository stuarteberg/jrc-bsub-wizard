#!/usr/bin/env python3
"""
BSub Wizard - Interactive job submission guide for Janelia Research Campus compute cluster

Usage:
    python main.py              # Start the wizard
    python main.py --help       # Show help
"""

import sys
import argparse
from pathlib import Path

# Add the wizard module to the path
sys.path.insert(0, str(Path(__file__).parent))

from wizard.app import run_wizard


def main():
    """Main entry point for the BSub Wizard"""
    parser = argparse.ArgumentParser(
        description="BSub Wizard - Interactive guide for creating bsub commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                    # Start the interactive wizard
    python main.py --version          # Show version information

The BSub Wizard helps you create properly formatted bsub commands for the 
Janelia Research Campus compute cluster. It guides you through:

• Job type selection (CPU, GPU, Interactive, MPI)
• Resource configuration (cores, memory, GPUs)
• Queue selection and optimization
• Runtime and scheduling options
• File management and I/O setup
• Advanced options and customization
• Command generation and validation

For more information, visit: https://github.com/janelia/bsub-wizard
"""
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="BSub Wizard 1.0.0"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Load configuration from JSON file"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Set debug mode if requested
    if args.debug:
        import os
        os.environ["TEXTUAL_DEBUG"] = "1"
    
    try:
        # Run the wizard
        run_wizard()
    except KeyboardInterrupt:
        print("\\nBSub Wizard interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error running BSub Wizard: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()