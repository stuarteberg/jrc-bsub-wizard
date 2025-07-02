#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="bsub-wizard",
    version="1.0.0",
    description="Interactive wizard for creating LSF bsub commands for Janelia Research Campus compute cluster",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Janelia Research Campus",
    author_email="scientific-computing@janelia.hhmi.org",
    url="https://github.com/janelia/bsub-wizard",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "textual>=0.40.0",
        "rich>=13.0.0", 
        "click>=8.0.0",
        "pyperclip>=1.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ]
    },
    entry_points={
        "console_scripts": [
            "bsub-wizard=wizard.app:run_wizard",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: User Interfaces",
        "Environment :: Console :: Curses",
    ],
    keywords="hpc cluster job-submission lsf bsub janelia scientific-computing",
    project_urls={
        "Bug Reports": "https://github.com/janelia/bsub-wizard/issues",
        "Source": "https://github.com/janelia/bsub-wizard",
        "Documentation": "https://github.com/janelia/bsub-wizard/wiki",
        "Janelia Cluster": "https://www.janelia.org/support-team/scientific-computing",
    },
)