import os
from crewai import Agent, Task, Crew
from tools.custom_tool import StockDataTool
import os

stock_data_tool = StockDataTool()

# Importing crewAI tools
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,

)
import os
# # Set up API keys
# os.environ["OPENAI_API_KEY"] = "dummy_key"

# Instantiate tools
docs_tool = DirectoryReadTool(directory='./blog-posts')
file_tool = FileReadTool()
search_tool = SerperDevTool()
#web_rag_tool = WebsiteSearchTool()
from crewai import LLM
from fastapi import FastAPI
app = FastAPI()

@app.get("/analyze_stock/")
def get_stock_analysis(user_input:str):

    llm =  LLM(
        model="gemini/gemini-1.5-flash",
        temperature=0.7,
            provider="google",  # 👈 Explicitly set the provider
        api_key= os.getenv('GEMINI_API_KEY')
    )
    from crewai import Agent

    # Research Analyst Agent
    researcher_agent = Agent(
        role='Indian Stock Market Research Analyst',
        goal=(
            "Conduct a real-time technical analysis in Indian stock market. for user question {share_name} "
            "Use live market data and indicators including current price trend, volume changes, 50/200-day moving averages, and RSI. "
            "Summarize the stock's momentum, volatility, and potential opportunities or red flags in a clear, actionable insight report."
        ),
        backstory=(
            "An expert Indian equity market analyst with a strong background in quantitative analysis and real-time data monitoring. "
            "Skilled in identifying short- and mid-term trends using live price feeds, volume spikes, and key technical signals like MA crossovers and RSI shifts. "
            "This agent is purpose-built to support traders and investors by generating timely, data-driven insights on specific stocks."
        ),
        tools=[stock_data_tool],
        # Ensure this tool supports live data fetch (e.g., from NSE/BSE APIs or yfinance for Indian tickers)
        verbose=False,
        llm=llm
    )

    # Senior Analyst Agent
    writer_agent = Agent(
        role='Senior Indian Stock Market Analyst with 10+ years of experience',
        goal=(
            "Evaluate the technical analysis and current market sentiment for {share_name} to determine whether it's the right time to BUY, HOLD, or SELL. "
            "Provide a concise investment recommendation backed by market reasoning, risk factors, and investor outlook (short-term and medium-term)."
        ),
        backstory=(
            "A veteran equity strategist with over a decade of experience analyzing Indian stocks. "
            "Expert at synthesizing technical signals, market psychology, and macroeconomic trends to guide investor decisions. "
            "Regularly advises clients on equity positioning, portfolio strategy, and timing market entries/exits. "
            "This agent reviews research findings and distills them into clear, actionable investment guidance tailored for retail and semi-institutional investors."
        ),
        # Optionally enable these if report writing is part of your pipeline:
        # tools=[docs_tool, file_tool],
        verbose=False,
        llm=llm
    )

    decider_agent = Agent(
        role='Investment Decision Maker. Your task is to analyze a given stock and make an actionable investment recommendation: **BUY**, **SELL**, or **HOLD**.',

        goal='Combine data and analysis to output a clear recommendation: BUY, HOLD, or SELL on given user_input {share_name}.',
        backstory=(
            "An AI advisor trained to make strategic stock decisions using both data and experience-backed analysis. "
            "It balances risk with reward and always looks out for long-term gains."

        ),
        tools=[docs_tool, file_tool],  # Optional
        verbose=False,
        llm=llm
    )

    # Define tasks
    research = Task(
        description='''
        Use real-time data to analyze these stocks: {share_name}.
        For each one, gather price, P/E, volume, highs/lows, MACD, RSI, Debt-to-Equity, Earnings Growth (YoY) and a 1-line buy/sell recommendation.
        
        ''',
        expected_output='''
        A markdown report with:
        - 📌 Stock Name
        - ✅ Key Stats
        - 💡 Recommendation
        - RSI
        - MACD
        ''',
        agent=researcher_agent
    )


    write = Task(
        description=''' 
        Use the research findings to generate a clear and informative market summary report.
        Each section should explain the stock/sector, why it was selected, key financial metrics, potential growth, and any market risks.
        The language should be beginner-friendly while still providing solid insights for potential investors or analysts.
        ''',
        expected_output='''
        A markdown-formatted report with one section per stock or sector.
        Each section should include a headline, summary paragraph, key stats (e.g., 52-week high/low, P/E ratio, volume), pros and cons, and investment notes.
        
        '''      ,
        agent=writer_agent,
        context=[research]
        #output_file='blog-posts/new_post_write.md'  # The final blog post will be saved here
    )







    decider_task = Task(
        description=(
            "Review the detailed market research and expert analysis of the stock {share_name}. "
            "Based on this information, make a final recommendation: BUY, SELL, or HOLD. "
            "Support your decision with 2-3 key points from the research or analysis. "
            "Consider technical indicators, market sentiment, price trends, and overall outlook."
        ),
        expected_output=(
            "A clear recommendation: BUY / SELL / HOLD {share_name}, followed by a short explanation of why."
        ),
        agent=decider_agent,
        context=[research, write] , # This links to the earlier agents' output
        #output_file='blog-posts/new_post.md'
    )



    # Assemble a crew with planning enabled
    crew = Crew(
        agents=[researcher_agent, writer_agent, decider_agent],
        tasks=[research, write, decider_task],
        verbose=False,
        planning=False,  # Enable planning feature
        llm=llm
    )
    from datetime import datetime
    inputs = {
        'share_name': user_input,
        'current_year': str(datetime.now().year)
    }
    # Execute tasks
    res = crew.kickoff(inputs=inputs)
    return res

@app.get("/crew_analysis/")
def get_analysis_report(user_input:str):
    from crew import LatestAiDevelopment
    inputs =  {
		'share_name': user_input
	}
    response = LatestAiDevelopment().crew().kickoff(inputs=inputs)
    print(response)
    return response
if __name__ == '__main__':
    result = hello()
