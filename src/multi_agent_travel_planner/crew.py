from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from .tools.custom_tool import CalculatorTool
from typing import List

import logging
import os

logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)

os.environ["LITELLM_PROXY"] = "False"
os.environ["LITELLM_SERVER"] = "False"
os.environ["LITELLM_DISABLE_SPEND_LOGGING"] = "True"
os.environ["LITELLM_TELEMETRY"] = "False"
os.environ["LITELLM_LOG"] = "CRITICAL"
os.environ["LITELLM_MODE"] = "PRODUCTION"


MODEL = os.getenv("MODEL_NAME")
MAX_TOKEN = os.getenv("MAX_TOKEN")


@CrewBase
class MultiAgentTravelPlanner:
    """MultiAgentTravelPlanner crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    serper_tool = SerperDevTool()
    serper_tool.name = "serper_search"

    llm = LLM(
        model=MODEL,
        temperature=0.2,
        max_tokens=int(MAX_TOKEN),
    )

    @agent
    def destination_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["destination_researcher"],
            verbose=True,
            tools=[self.serper_tool],
            llm=self.llm,
            max_iter=2,
        )

    @agent
    def budget_planner(self) -> Agent:
        return Agent(
            config=self.agents_config["budget_planner"],
            verbose=True,
            tools=[self.serper_tool, CalculatorTool()],
            llm=self.llm,
            max_iter=2,
        )

    @agent
    def itinerary_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["itinerary_designer"],
            verbose=True,
            tools=[self.serper_tool],
            llm=self.llm,
            max_iter=2,
        )

    @agent
    def validation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["validation_agent"],
            verbose=True,
            tools=[CalculatorTool()],
            llm=self.llm,
            max_iter=1,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            output_file="output/research.md",
        )

    @task
    def budget_task(self) -> Task:
        return Task(
            config=self.tasks_config["budget_task"],
            context=[self.research_task()],
            output_file="output/budget.md",
        )

    @task
    def itinerary_task(self) -> Task:
        return Task(
            config=self.tasks_config["itinerary_task"],
            context=[self.research_task(), self.budget_task()],
            output_file="output/itinerary.md",
        )

    @task
    def validation_task(self) -> Task:
        return Task(
            config=self.tasks_config["validation_task"],
            context=[
                self.research_task(),
                self.budget_task(),
                self.itinerary_task(),
            ],
            output_file="output/validation.md",
        )

    # ─── Merge Hook ───────────────────────────────────────────────────────────

    @after_kickoff
    def merge_all_task_outputs_hook(self, output):
        output_files = [
            "output/research.md",
            "output/budget.md",
            "output/itinerary.md",
            "output/validation.md",
        ]
        merged_file = "output/full_trip_plan.md"

        with open(merged_file, "w", encoding="utf-8") as outfile:
            for idx, file_path in enumerate(output_files, start=1):
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as infile:
                        outfile.write(f"# Section {idx}\n\n")
                        outfile.write(infile.read() + "\n\n---\n\n")

        print(f"[INFO] All task outputs merged into {merged_file}")
        return output

    # ─── Crew ─────────────────────────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            tracing=True,
        )
