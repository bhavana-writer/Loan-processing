import os
import json
import yfinance as yf
import pandas as pd
import numpy as np
from writer.blocks.base_block import WorkflowBlock
from writer.ss_types import AbstractTemplate
from writer.abstract import register_abstract_template
class WriterConfigurationError(Exception):
    """Raised when Writer API configuration is invalid."""
    pass

class YFinanceBlock(WorkflowBlock):
    """Block for retrieving stock news and financial data using YFinance API."""

    @classmethod
    def register(cls, type: str):
        """Register the block and define the fields for the visual tool."""
        super(YFinanceBlock, cls).register(type)
        register_abstract_template(type, AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "YFinance Block",
                "description": "Retrieves stock news and financial data using the YFinance API.",
                "category": "Other",
                "fields": {
                    "ticker": {
                        "name": "Ticker Symbol",
                        "type": "Text",
                        "control": "Text",
                        "default": "",
                        "validator": {
                            "type": "string",
                            "minLength": 1
                        },
                        "desc": "Stock ticker symbol to fetch data for (e.g., 'AAPL', 'GOOG')"
                    },
                    "data_type": {
                        "name": "Data Type", 
                        "type": "Text",
                        "options": {
                            "news": "News",
                            "financials": "Financials"
                        },
                        "default": "news",
                        "validator": {
                            "type": "string",
                            "enum": ["news", "financials"]
                        },
                        "desc": "Choose between fetching news or financials."
                    },
                },
                "outs": {
                    "success": {
                        "name": "Success",
                        "description": "The data was successfully retrieved.",
                        "style": "success",
                    },
                    "error": {
                        "name": "Error",
                        "description": "There was an error retrieving the data.",
                        "style": "error",
                    },
                },
            }
        ))

    def fetch_news(self, ticker: str):
        """Fetch stock news using YFinance API."""
        try:
            stock = yf.Ticker(ticker)
            raw_news = stock.news
            if not raw_news:
                raise WriterConfigurationError(f"No news found for ticker: {ticker}")
            
            # Clean and format the news data
            cleaned_news = []
            for article in raw_news:
                content = article.get('content', {})
                cleaned_article = {
                    'title': content.get('title'),
                    'url': content.get('canonicalUrl', {}).get('url'),
                    'description': content.get('summary')
                }
                cleaned_news.append(cleaned_article)
            
            return cleaned_news
        except Exception as e:
            raise WriterConfigurationError(f"Error fetching news for ticker {ticker}: {str(e)}")

    def fetch_financials(self, ticker: str):
        """Fetch financials using YFinance API."""
        try:
            stock = yf.Ticker(ticker)
            financials = stock.financials
            if financials.empty:
                raise WriterConfigurationError(f"No financial data found for ticker: {ticker}")
            
            # Convert to a simpler dictionary structure and handle numeric values
            cleaned_financials = {}
            for column in financials.columns:
                date_str = column.strftime('%Y-%m-%d') if hasattr(column, 'strftime') else str(column)
                cleaned_financials[date_str] = {}
                
                for index in financials.index:
                    # Convert numpy/pandas numeric types to native Python float
                    value = financials[column][index]
                    if pd.isna(value):  # Handle NaN values
                        cleaned_value = None
                    else:
                        cleaned_value = float(value) if isinstance(value, (np.integer, np.floating)) else value
                    cleaned_financials[date_str][str(index)] = cleaned_value
            
            return cleaned_financials
        except Exception as e:
            raise WriterConfigurationError(f"Error fetching financials for ticker {ticker}: {str(e)}")

    def run(self):
        """Execute the block's workflow."""
        try:
            ticker = self._get_field("ticker", required=True)
            data_type = self._get_field("data_type", required=True)

            if data_type == "news":
                self.result = self.fetch_news(ticker)
                self.outcome = "success" if self.result else "error"
            elif data_type == "financials":
                self.result = self.fetch_financials(ticker)
                self.outcome = "success" if self.result else "error"
            else:
                raise WriterConfigurationError("Invalid data type selected.")

        except WriterConfigurationError as e:
            self.outcome = "error"
            self.result = {"error": str(e)}

        except Exception as e:
            self.outcome = "error"
            self.result = {"error": f"An unexpected error occurred: {str(e)}"}

