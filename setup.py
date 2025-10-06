#!/usr/bin/env python3
"""Setup configuration for dedupe-tarball CLI application."""

from setuptools import setup, find_packages
import os.path

# Read version from package
def get_version():
    """Extract version from package __init__.py"""
    version_file = os.path.join('src', 'dedupe', '__init__.py')
    with open(version_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '0.1.0'

# Read long description from README if it exists
def get_long_description():
    """Get long description from README file."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Command-line tool for detecting and managing duplicate files in tarball archives"

setup(
    name="dedupe-tarball",
    version=get_version(),
    author="System Administrator",
    author_email="admin@example.com",
    description="Command-line tool for detecting and managing duplicate files in tarball archives",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/dedupe-tarball",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Archiving",
        "Topic :: Utilities",
    ],
    python_requires=">=3.12",
    install_requires=[
        "psycopg2-binary>=2.9.0,<3.0.0",
        "toml>=0.10.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0", 
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dedupe-tarball=dedupe.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)