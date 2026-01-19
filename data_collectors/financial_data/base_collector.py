"""
Base Financial Data Collector

Abstract base class for all financial data collectors.
Provides a common interface and enforces implementation of required methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd


class BaseFinancialCollector(ABC):
    """
    Abstract base class for financial data collectors.
    
    All financial data collectors must inherit from this class and implement
    the abstract methods to ensure consistent interface across different data sources.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the collector.
        
        Args:
            api_key: API key for the data source (if required)
        """
        self.api_key = api_key
        self.base_url = None
    
    @abstractmethod
    def get_income_statement(
        self, 
        ticker: str, 
        period: str = "annual",
        limit: int = 5
    ) -> pd.DataFrame:
        """
        Get income statement data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            period: "annual" or "quarter"
            limit: Number of periods to retrieve
            
        Returns:
            DataFrame containing income statement data
            
        Raises:
            ValueError: If ticker is invalid
            APIError: If API request fails
        """
        pass
    
    @abstractmethod
    def get_balance_sheet(
        self, 
        ticker: str, 
        period: str = "annual",
        limit: int = 5
    ) -> pd.DataFrame:
        """
        Get balance sheet data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            period: "annual" or "quarter"
            limit: Number of periods to retrieve
            
        Returns:
            DataFrame containing balance sheet data
            
        Raises:
            ValueError: If ticker is invalid
            APIError: If API request fails
        """
        pass
    
    @abstractmethod
    def get_cashflow_statement(
        self, 
        ticker: str, 
        period: str = "annual",
        limit: int = 5
    ) -> pd.DataFrame:
        """
        Get cash flow statement data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            period: "annual" or "quarter"
            limit: Number of periods to retrieve
            
        Returns:
            DataFrame containing cash flow statement data
            
        Raises:
            ValueError: If ticker is invalid
            APIError: If API request fails
        """
        pass
    
    @abstractmethod
    def get_financial_ratios(
        self, 
        ticker: str, 
        period: str = "annual",
        limit: int = 5
    ) -> pd.DataFrame:
        """
        Get financial ratios for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            period: "annual" or "quarter"
            limit: Number of periods to retrieve
            
        Returns:
            DataFrame containing financial ratios
            
        Raises:
            ValueError: If ticker is invalid
            APIError: If API request fails
        """
        pass
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate ticker symbol format.
        
        Args:
            ticker: Stock ticker symbol to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not ticker or not isinstance(ticker, str):
            return False
        
        # Ticker should be 1-5 uppercase letters/numbers
        # Allow common formats: AAPL, BRK.B, etc.
        import re
        pattern = r'^[A-Z0-9]{1,5}(\.[A-Z])?$'
        return bool(re.match(pattern, ticker.upper()))
    
    def validate_period(self, period: str) -> bool:
        """
        Validate period parameter.
        
        Args:
            period: Period to validate
            
        Returns:
            True if valid, False otherwise
        """
        return period.lower() in ["annual", "quarter"]
