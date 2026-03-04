from typing import List

from google.adk.agents import Agent
from google.adk.models import LiteLlm
from pydantic import BaseModel, Field

from .prompt import PROMPT_BUILDER_DESCRIPTION, PROMPT_BUILDER_PROMPT

MODEL = LiteLlm(model="openai/gpt-4o")

class OptimizedPrompt(BaseModel):
    scene_id: int = Field(description="Scene ID from the original content plan")
    enhanced_prompt: str = Field(description="Detailed prompt with technical specs and text overlay instructions for vertical Youtube Shorts")

class PromptBuilderOutput(BaseModel):
    optimized_prompts: List[OptimizedPrompt] = Field(description="Array of optimized image generation prompts for vertical Youtube Shorts")


prompt_builder_agent = Agent(
    name="PromptBuilderAgent",
    description=PROMPT_BUILDER_DESCRIPTION,
    instruction=PROMPT_BUILDER_PROMPT,
    model=MODEL,
    output_key="prompt_builder_output",
    output_schema=PromptBuilderOutput,
)