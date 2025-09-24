"""
Setup script for Firefly Asset Management Solution
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open("requirements.txt", "r") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="firefly-analyzer",
    version="1.0.0",
    author="Victor - Senior QA Automation Engineer",
    author_email="victor@example.com",
    description="Cloud to Infrastructure-as-Code (IaC) Resources Analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Chibuzorchi/firefly-analyzer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Systems Administration",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "s3": [
            "boto3>=1.34.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "firefly-analyze=firefly_analyzer.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "firefly_analyzer": ["samples/*.json"],
    },
    keywords="cloud, infrastructure, iac, terraform, aws, devops, analysis, monitoring",
    project_urls={
        "Bug Reports": "https://github.com/Chibuzorchi/firefly-analyzer/issues",
        "Source": "https://github.com/Chibuzorchi/firefly-analyzer",
        "Documentation": "https://github.com/Chibuzorchi/firefly-analyzer#readme",
    },
)
