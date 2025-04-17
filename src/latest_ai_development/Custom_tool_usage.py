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



llm =  LLM(
    model="gemini/gemini-1.5-flash",
    temperature=0.7,
        provider="google",  # 👈 Explicitly set the provider
    api_key= os.getenv('GEMINI_API_KEY')
)
from crewai import Agent

# Research Analyst Agent
researcher_agent = Agent(
    role='Indian Share Market Research Analyst',
    goal='Analyze the current market condition of {share_name} using live data and indicators like price trend, volume, moving average, and RSI, then provide insights.',
    backstory=(
        "A data-driven market researcher specialized in the Indian stock market. "
        "This agent pulls and analyzes live stock data such as price, volume, and key technical indicators, "
        "and generates a clear snapshot of the stock's current momentum and strength."
    ),
    tools=[stock_data_tool],  # This should include your live stock data fetching logic
    verbose=True,
    llm=llm
)

# Senior Analyst Agent
writer_agent = Agent(
    role='Senior Indian Stock Market Analyst with 10 years of experience',
    goal=(
        "Based on the researcher's findings and market sentiment, determine whether it's a good time to BUY, HOLD, or SELL {share_name}. "
        "Provide a clear and concise investment recommendation with reasoning."
    ),
    backstory=(
        "A seasoned investment strategist with deep experience in reading market movements, economic trends, and technical patterns. "
        "This agent evaluates the research and interprets it from an investor's perspective to provide actionable decisions."
    ),
    #tools=[docs_tool, file_tool],  # These tools can help if you're compiling reports or saving outputs
    verbose=True,
    llm=llm
)


decider_agent = Agent(
    role='Investment Decision Maker',
    goal='Combine data and analysis to output a clear recommendation: BUY, HOLD, or SELL the {share_name} stock.',
    backstory=(
        "An AI advisor trained to make strategic stock decisions using both data and experience-backed analysis. "
        "It balances risk with reward and always looks out for long-term gains."
    ),
    tools=[docs_tool, file_tool],  # Optional
    verbose=True,
    llm=llm
)

# Define tasks
research = Task(
    description='''
    Use real-time data to analyze these stocks: {share_name}.
    For each one, gather price, P/E, volume, highs/lows, and a 1-line buy/sell recommendation.
    ''',
    expected_output='''
    A markdown report with:
    - 📌 Stock Name
    - ✅ Key Stats
    - 💡 Recommendation
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
    
    '''
              ,
    agent=writer_agent,
    output_file='blog-posts/new_post_write.md'  # The final blog post will be saved here
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
    output_file='blog-posts/new_post.md'
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
    'share_name': '''I have KHOOBSURAT.BO stock in my portfolio for 1.58 RS. Should I Average or hold or sell?''',
    'current_year': str(datetime.now().year)
}
# Execute tasks
crew.kickoff(inputs=inputs)