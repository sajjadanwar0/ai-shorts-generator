from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import AgentTool

from .prompt import SHORTS_PRODUCER_PROMPT, SHORTS_PRODUCER_DESCRIPTION
from .sub_agents.asset_generator.agent import asset_generator_agent
from .sub_agents.content_planner.agent import content_planner_agent
from .sub_agents.video_assembler.agent import video_assembler_agent

MODEL = LiteLlm("openai/gpt-4o")

short_producer_agent = Agent(
    name="ShortsProducerAgent",
    model=MODEL,
    description=SHORTS_PRODUCER_DESCRIPTION,
    instruction=SHORTS_PRODUCER_PROMPT,
    tools=[
        AgentTool(agent=content_planner_agent),
        AgentTool(agent=asset_generator_agent),
        AgentTool(agent=video_assembler_agent),
    ]
)

root_agent = short_producer_agent