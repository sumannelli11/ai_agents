from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool



# tools/StockDataTool.py
import yfinance as yf

# tools/StockDataTool.py

import yfinance as yf

class StockDataTool(BaseTool):
    name: str = "LiveStockDataTool"
    description: str = "Provides real-time stock data for Indian companies using their NSE tickers"

    def _run(self, ticker: str) -> str:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return f"""
📊 **{info.get('longName', ticker)} ({ticker})**

- **Current Price**: ₹{info.get('currentPrice')}
- **52-Week High**: ₹{info.get('fiftyTwoWeekHigh')}
- **52-Week Low**: ₹{info.get('fiftyTwoWeekLow')}
- **P/E Ratio**: {info.get('trailingPE')}
- **Volume**: {info.get('volume')}
- **Market Cap**: ₹{info.get('marketCap')}
- **Sector**: {info.get('sector', 'N/A')}

📝 **Summary**: {info.get('longBusinessSummary', 'No summary available.')}
"""
        except Exception as e:
            return f"⚠️ Error fetching data for {ticker}: {str(e)}"




from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."
