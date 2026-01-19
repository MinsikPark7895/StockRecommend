"""
Financial Modeling Prep (FMP) API Collector

Secure implementation for collecting financial statement data from FMP API.
All security best practices are implemented including input validation,
secure API key handling, error sanitization, and rate limiting.
"""

import os
import logging
import pandas as pd
import requests
from typing import Optional, Dict, List
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from requests.exceptions import (
    RequestException,
    Timeout,
    ConnectionError as RequestsConnectionError
)

from .base_collector import BaseFinancialCollector
from .utils import (
    validate_ticker_symbol,
    validate_period,
    validate_limit,
    mask_api_key,
    sanitize_error_message
)

logger = logging.getLogger(__name__)


class FMPAPIError(Exception):
    """Custom exception for FMP API errors."""
    pass


class FMPCollector(BaseFinancialCollector):
    """
    Financial Modeling Prep API collector.
    
    Implements secure data collection from FMP API with:
    - Input validation and sanitization
    - Secure API key management
    - Error handling with information sanitization
    - Rate limiting and retry logic
    - HTTPS enforcement
    """
    
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    
    # Rate limiting: FMP free tier allows 250 requests/day
    # Conservative limit: 5 requests per minute
    MAX_REQUESTS_PER_MINUTE = 5
    REQUEST_TIMEOUT = 30  # seconds
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FMP collector.
        
        Args:
            api_key: FMP API key. If not provided, will try to load from environment.
            
        Raises:
            ValueError: If API key is not provided and not found in environment
        """
        # Load API key from environment if not provided
        if api_key is None:
            api_key = os.getenv("FMP_API_KEY")
        
        if not api_key:
            raise ValueError(
                "FMP API key is required. "
                "Set FMP_API_KEY environment variable or pass api_key parameter."
            )
        
        super().__init__(api_key=api_key)
        self.base_url = self.BASE_URL
        
        # Log initialization (with masked API key)
        logger.info(f"FMP Collector initialized with API key: {mask_api_key(api_key)}")
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict] = None
    ) -> Dict:
        """
        Make secure HTTP request to FMP API.
        
        Security features:
        - HTTPS enforcement
        - Timeout protection
        - Retry logic with exponential backoff
        - Error sanitization
        - Input validation
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            FMPAPIError: If API request fails
            ValueError: If input parameters are invalid
        """
        # Validate endpoint
        if not endpoint or not isinstance(endpoint, str):
            raise ValueError("Endpoint must be a non-empty string")
        
        # Sanitize endpoint (prevent path traversal)
        endpoint = endpoint.strip().lstrip('/')
        if '..' in endpoint or endpoint.startswith('/'):
            raise ValueError("Invalid endpoint format")
        
        # Build URL
        url = f"{self.base_url}/{endpoint}"
        
        # Prepare parameters
        request_params = params or {}
        request_params['apikey'] = self.api_key
        
        # Log request (without API key)
        logger.debug(f"Making request to FMP API: {endpoint}")
        
        try:
            # Make request with security settings
            response = self._execute_request(url, request_params)
            
            # Check for API errors in response
            if isinstance(response, list) and len(response) == 0:
                logger.warning(f"Empty response from FMP API for endpoint: {endpoint}")
                return []
            
            # Check for error messages in response
            if isinstance(response, dict) and 'Error Message' in response:
                error_msg = response['Error Message']
                logger.error(f"FMP API error: {error_msg}")
                raise FMPAPIError(f"API returned error: {error_msg}")
            
            return response
            
        except FMPAPIError:
            raise
        except Exception as e:
            # Sanitize error message before logging/raising
            sanitized_msg = sanitize_error_message(e)
            logger.error(f"Error making request to FMP API: {sanitized_msg}")
            raise FMPAPIError(f"Failed to retrieve data from FMP API: {sanitized_msg}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Timeout, RequestsConnectionError)),
        reraise=True
    )
    def _execute_request(self, url: str, params: Dict) -> Dict:
        """
        Execute HTTP request with retry logic.
        
        Args:
            url: Full URL
            params: Request parameters
            
        Returns:
            JSON response
            
        Raises:
            RequestException: If request fails after retries
        """
        try:
            response = requests.get(
                url,
                params=params,
                timeout=self.REQUEST_TIMEOUT,
                verify=True,  # Enforce SSL certificate verification
                headers={
                    'User-Agent': 'StockRecommend/1.0',
                    'Accept': 'application/json'
                }
            )
            
            # Check HTTP status
            response.raise_for_status()
            
            # Parse JSON
            return response.json()
            
        except Timeout:
            logger.warning(f"Request timeout for URL: {url}")
            raise
        except RequestsConnectionError as e:
            logger.warning(f"Connection error: {sanitize_error_message(e)}")
            raise
        except requests.exceptions.HTTPError as e:
            # Handle specific HTTP errors
            if e.response.status_code == 401:
                raise FMPAPIError("Invalid API key. Please check your FMP_API_KEY.")
            elif e.response.status_code == 403:
                raise FMPAPIError("API access forbidden. Check your API key permissions.")
            elif e.response.status_code == 429:
                raise FMPAPIError("Rate limit exceeded. Please wait before making more requests.")
            elif e.response.status_code == 404:
                raise FMPAPIError("Endpoint not found. Check the API endpoint.")
            else:
                raise FMPAPIError(f"HTTP error {e.response.status_code}: {sanitize_error_message(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {sanitize_error_message(e)}")
            raise FMPAPIError(f"Request failed: {sanitize_error_message(e)}")
    
    def get_income_statement(
        self, 
        ticker: str, 
        period: str = "annual",
        limit: int = 5
    ) -> pd.DataFrame:
        """
        Get income statement data for a ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
            period: "annual" or "quarter"
            limit: Number of periods to retrieve (1-100)
            
        Returns:
            DataFrame containing income statement data
            
        Raises:
            ValueError: If input parameters are invalid
            FMPAPIError: If API request fails
        """
        # Input validation
        ticker = validate_ticker_symbol(ticker)
        period = validate_period(period)
        limit = validate_limit(limit)
        
        logger.info(f"Fetching income statement for {ticker} ({period}, limit={limit})")
        
        try:
            endpoint = f"income-statement/{ticker}"
            params = {
                'period': period,
                'limit': limit
            }
            
            data = self._make_request(endpoint, params)
            
            if not data or len(data) == 0:
                logger.warning(f"No income statement data found for {ticker}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Validate DataFrame
            if df.empty:
                logger.warning(f"Empty DataFrame returned for {ticker}")
                return df
            
            logger.info(f"Successfully retrieved {len(df)} income statement records for {ticker}")
            return df
            
        except (ValueError, FMPAPIError):
            raise
        except Exception as e:
            sanitized_msg = sanitize_error_message(e)
            logger.error(f"Unexpected error fetching income statement: {sanitized_msg}")
            raise FMPAPIError(f"Failed to fetch income statement: {sanitized_msg}")
    
    def get_balance_sheet(
        self, 
        ticker: str, 
        period: str = "annual",
        limit: int = 5
    ) -> pd.DataFrame:
        """
        Get balance sheet data for a ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
            period: "annual" or "quarter"
            limit: Number of periods to retrieve (1-100)
            
        Returns:
            DataFrame containing balance sheet data
            
        Raises:
            ValueError: If input parameters are invalid
            FMPAPIError: If API request fails
        """
        # Input validation
        ticker = validate_ticker_symbol(ticker)
        period = validate_period(period)
        limit = validate_limit(limit)
        
        logger.info(f"Fetching balance sheet for {ticker} ({period}, limit={limit})")
        
        try:
            endpoint = f"balance-sheet-statement/{ticker}"
            params = {
                'period': period,
                'limit': limit
            }
            
            data = self._make_request(endpoint, params)
            
            if not data or len(data) == 0:
                logger.warning(f"No balance sheet data found for {ticker}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            logger.info(f"Successfully retrieved {len(df)} balance sheet records for {ticker}")
            return df
            
        except (ValueError, FMPAPIError):
            raise
        except Exception as e:
            sanitized_msg = sanitize_error_message(e)
            logger.error(f"Unexpected error fetching balance sheet: {sanitized_msg}")
            raise FMPAPIError(f"Failed to fetch balance sheet: {sanitized_msg}")
    
    def get_cashflow_statement(
        self, 
        ticker: str, 
        period: str = "annual",
        limit: int = 5
    ) -> pd.DataFrame:
        """
        Get cash flow statement data for a ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
            period: "annual" or "quarter"
            limit: Number of periods to retrieve (1-100)
            
        Returns:
            DataFrame containing cash flow statement data
            
        Raises:
            ValueError: If input parameters are invalid
            FMPAPIError: If API request fails
        """
        # Input validation
        ticker = validate_ticker_symbol(ticker)
        period = validate_period(period)
        limit = validate_limit(limit)
        
        logger.info(f"Fetching cash flow statement for {ticker} ({period}, limit={limit})")
        
        try:
            endpoint = f"cash-flow-statement/{ticker}"
            params = {
                'period': period,
                'limit': limit
            }
            
            data = self._make_request(endpoint, params)
            
            if not data or len(data) == 0:
                logger.warning(f"No cash flow statement data found for {ticker}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            logger.info(f"Successfully retrieved {len(df)} cash flow records for {ticker}")
            return df
            
        except (ValueError, FMPAPIError):
            raise
        except Exception as e:
            sanitized_msg = sanitize_error_message(e)
            logger.error(f"Unexpected error fetching cash flow statement: {sanitized_msg}")
            raise FMPAPIError(f"Failed to fetch cash flow statement: {sanitized_msg}")
    
    def get_financial_ratios(
        self, 
        ticker: str, 
        period: str = "annual",
        limit: int = 5
    ) -> pd.DataFrame:
        """
        Get financial ratios for a ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
            period: "annual" or "quarter"
            limit: Number of periods to retrieve (1-100)
            
        Returns:
            DataFrame containing financial ratios
            
        Raises:
            ValueError: If input parameters are invalid
            FMPAPIError: If API request fails
        """
        # Input validation
        ticker = validate_ticker_symbol(ticker)
        period = validate_period(period)
        limit = validate_limit(limit)
        
        logger.info(f"Fetching financial ratios for {ticker} ({period}, limit={limit})")
        
        try:
            endpoint = f"ratios/{ticker}"
            params = {
                'period': period,
                'limit': limit
            }
            
            data = self._make_request(endpoint, params)
            
            if not data or len(data) == 0:
                logger.warning(f"No financial ratios found for {ticker}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            logger.info(f"Successfully retrieved {len(df)} financial ratio records for {ticker}")
            return df
            
        except (ValueError, FMPAPIError):
            raise
        except Exception as e:
            sanitized_msg = sanitize_error_message(e)
            logger.error(f"Unexpected error fetching financial ratios: {sanitized_msg}")
            raise FMPAPIError(f"Failed to fetch financial ratios: {sanitized_msg}")
    
    def get_all_financials(
        self, 
        ticker: str, 
        period: str = "annual",
        limit: int = 5
    ) -> Dict[str, pd.DataFrame]:
        """
        Get all financial statements at once.
        
        Args:
            ticker: Stock ticker symbol
            period: "annual" or "quarter"
            limit: Number of periods to retrieve
            
        Returns:
            Dictionary containing all financial statements:
            {
                'income_statement': DataFrame,
                'balance_sheet': DataFrame,
                'cashflow': DataFrame,
                'ratios': DataFrame
            }
        """
        logger.info(f"Fetching all financial data for {ticker}")
        
        return {
            'income_statement': self.get_income_statement(ticker, period, limit),
            'balance_sheet': self.get_balance_sheet(ticker, period, limit),
            'cashflow': self.get_cashflow_statement(ticker, period, limit),
            'ratios': self.get_financial_ratios(ticker, period, limit)
        }
