import pandas as pd
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from ta.momentum import RSIIndicator
from ta.trend import MACD



# tools/StockDataTool.py
import yfinance as yf

# tools/StockDataTool.py

import yfinance as yf

class StockDataTool(BaseTool):
    name: str = "LiveStockDataTool"
    description: str = "Provides real-time stock data for Indian companies using their NSE tickers"

    def _stock_analysis(self,ticker: str) -> pd.DataFrame:

        data = yf.download(ticker, period='6mo', interval='1d')

        # Drop rows with NaNs (if any)

        data.dropna(inplace=True)
        close_series = data['Close'][ticker]

        # RSI (Relative Strength Index)
        rsi = RSIIndicator(close=close_series, window=14)
        data['RSI'] = rsi.rsi()

        # MACD (Moving Average Convergence Divergence)
        macd = MACD(close=data['Close'][ticker])
        data['MACD'] = macd.macd()
        data['MACD_Signal'] = macd.macd_signal()
        data['MACD_Diff'] = macd.macd_diff()

        # Preview the latest values
        # print(data[['Close', 'RSI', 'MACD', 'MACD_Signal', 'MACD_Diff']].tail())
        # print(data)
        return data[['Close', 'RSI', 'MACD', 'MACD_Signal', 'MACD_Diff']].tail()


    def _run(self, ticker: str) -> str:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            data = self._stock_analysis(ticker)

            return f"""
📊 **{info.get('longName', ticker)} ({ticker})**

- **Current Price**: ₹{info.get('currentPrice')}
- **52-Week High**: ₹{info.get('fiftyTwoWeekHigh')}
- **52-Week Low**: ₹{info.get('fiftyTwoWeekLow')}
- **P/E Ratio**: {info.get('trailingPE')}
- **Volume**: {info.get('volume')}
- **Market Cap**: ₹{info.get('marketCap')}
- **DebtToEquity**: ₹{info.get('debtToEquity')}
- **EarningsQuarterlyGrowth**: ₹{info.get('earningsQuarterlyGrowth')}
- **Sector**: {info.get('sector', 'N/A')}
- **Dividends**: {info.get('dividends')}
- **RSI**: {data['RSI']}
- **MACD**: {data['MACD']}
- **MACD_Signal**: {data['MACD_Signal']}
- **MACD_diff**: {data['MACD_Diff']}


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
