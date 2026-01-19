"""
Example usage of FMP Collector

This file demonstrates how to use the FMPCollector class securely.
DO NOT commit this file with actual API keys!
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from data_collectors.financial_data import FMPCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables from .env file
load_dotenv()


def main():
    """
    Example usage of FMP Collector.
    
    Make sure to set FMP_API_KEY in your .env file before running.
    """
    try:
        # Initialize collector (will load API key from environment)
        collector = FMPCollector()
        
        # Example: Get income statement for Apple
        print("\n=== Fetching Income Statement for AAPL ===")
        income_df = collector.get_income_statement("AAPL", period="annual", limit=5)
        print(f"Retrieved {len(income_df)} records")
        if not income_df.empty:
            print("\nColumns:", income_df.columns.tolist()[:10])  # Show first 10 columns
            print("\nFirst record date:", income_df.iloc[0].get('date', 'N/A'))
        
        # Example: Get balance sheet
        print("\n=== Fetching Balance Sheet for AAPL ===")
        balance_df = collector.get_balance_sheet("AAPL", period="annual", limit=5)
        print(f"Retrieved {len(balance_df)} records")
        
        # Example: Get cash flow statement
        print("\n=== Fetching Cash Flow Statement for AAPL ===")
        cashflow_df = collector.get_cashflow_statement("AAPL", period="annual", limit=5)
        print(f"Retrieved {len(cashflow_df)} records")
        
        # Example: Get financial ratios
        print("\n=== Fetching Financial Ratios for AAPL ===")
        ratios_df = collector.get_financial_ratios("AAPL", period="annual", limit=5)
        print(f"Retrieved {len(ratios_df)} records")
        
        # Example: Get all financials at once
        print("\n=== Fetching All Financial Data for MSFT ===")
        all_financials = collector.get_all_financials("MSFT", period="annual", limit=3)
        for statement_type, df in all_financials.items():
            print(f"{statement_type}: {len(df)} records")
        
        print("\n=== Example completed successfully! ===")
        
    except ValueError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Created a .env file from env.example")
        print("2. Set FMP_API_KEY in your .env file")
        print("3. Installed all requirements: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
