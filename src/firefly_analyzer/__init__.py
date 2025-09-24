"""
Firefly Asset Management Solution
Cloud to Infrastructure-as-Code (IaC) Resources Analyzer

A comprehensive tool for analyzing differences between cloud resources
and their corresponding Infrastructure-as-Code definitions.
"""

__version__ = "1.0.0"
__author__ = "Victor - Senior QA Automation Engineer"

from .analyzer import CloudIacAnalyzer
from .matcher import ResourceMatcher
from .diff_converter import DiffConverter

__all__ = ["CloudIacAnalyzer", "ResourceMatcher", "DiffConverter"]
