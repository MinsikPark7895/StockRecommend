"""
Financial Data Collectors Module

This module contains implementations for collecting financial statement data
from various sources (FMP, SEC EDGAR, etc.).
"""

from .fmp_collector import FMPCollector

__all__ = ['FMPCollector']
