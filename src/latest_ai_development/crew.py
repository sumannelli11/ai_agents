from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from tools.custom_tool import StockDataTool
from crewai import LLM
import os
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,

)
stock_data_tool = StockDataTool()
from tools.custom_tool import StockDataTool
# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class LatestAiDevelopment():
	"""LatestAiDevelopment crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	docs_tool = DirectoryReadTool(directory='./blog-posts')
	file_tool = FileReadTool()

	llm = LLM(
		model="gemini/gemini-1.5-flash",
		temperature=0.7,
		provider="google",  # 👈 Explicitly set the provider
		api_key=os.getenv('GEMINI_API_KEY')
	)

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			verbose=False,
			tools=[stock_data_tool],
			# Ensure this tool supports live data fetch (e.g., from NSE/BSE APIs or yfinance for Indian tickers)

			llm=self.llm
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			verbose=False,
			llm=self.llm
		)


	@agent
	def decider_agent(self) -> Agent:

		return Agent(
			config=self.agents_config['decider_agent'],
			tools=[self.docs_tool, self.file_tool],  # Optional
			verbose=False,
			llm=self.llm
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],

			#output_file='report.md'
		)

	@task
	def decider_task(self) -> Task:
		return Task(
			config=self.tasks_config['decider_task'],

			# output_file='report.md'
		)
	@crew
	def crew(self) -> Crew:
		"""Creates the LatestAiDevelopment crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=False,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)


if __name__ == '__main__':
	share_name = {
		'share_name': 'Can I buy a new share SALASAR.NS?'
	}

	LatestAiDevelopment().crew().kickoff(inputs=share_name)