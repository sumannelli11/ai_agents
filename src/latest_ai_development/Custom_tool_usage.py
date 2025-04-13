import os
from crewai import Agent, Task, Crew
from tools.custom_tool import StockDataTool
import os

stock_data_tool = StockDataTool()

print(os.getenv('SERPER_API_KEY'))
print("'test")

# Importing crewAI tools
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,

)
import os
# # Set up API keys
# os.environ["OPENAI_API_KEY"] = "dummy_key"
os.environ["SERPER_API_KEY"] = 'fdb8fa46ff5b203b254aacc91de76d216a56028d'# serper.dev API key
os.environ["GEMINI_API_KEY"] = 'AIzaSyBB6sbOPqSqRcyO7uEWJ-tfDv51vtjhnDo'

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
    api_key='AIzaSyBB6sbOPqSqRcyO7uEWJ-tfDv51vtjhnDo'
)
# Create agents
researcher = Agent(
    role='Indian share Market Research Analyst',
    goal='Provide up-to-date market analysis of the indian share market industry',
    backstory='An expert analyst with a keen eye for market trends. Search in differerent repurce about a specific share based on current price need to decied buy or not',
    tools=[stock_data_tool],
    verbose=True,
    llm=llm
)

writer = Agent(
    role='Share Marked senior analyst with 10 years experience',
    goal='Looks for the suzlon share market',
    backstory='A great Share marked analyst ',
    tools=[docs_tool, file_tool],
    verbose=True,
llm=llm
)

# Define tasks
research = Task(
    description='''
    Use real-time data to analyze these stocks: SUZLON.NS, TCS.NS, RELIANCE.NS, INFY.NS, HDFCBANK.NS.
    For each one, gather price, P/E, volume, highs/lows, and a 1-line buy/sell recommendation.
    ''',
    expected_output='''
    A markdown report with:
    - 📌 Stock Name
    - ✅ Key Stats
    - 💡 Recommendation
    ''',
    agent=researcher
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
    agent=writer,
    output_file='blog-posts/new_post.md'  # The final blog post will be saved here
)

# Assemble a crew with planning enabled
crew = Crew(
    agents=[researcher, writer],
    tasks=[research, write],
    verbose=False,
    planning=False,  # Enable planning feature
    llm=llm
)
from datetime import datetime
inputs = {
    'topic': 'the best performing stocks or sectors for investment in 2025 based on trading volume, price trends, and growth potential',
    'current_year': str(datetime.now().year)
}
# Execute tasks
crew.kickoff(inputs=inputs)