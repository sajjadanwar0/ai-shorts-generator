from typing import List

from google.adk.agents import Agent
from google.adk.models import LiteLlm
from pydantic import BaseModel, Field

from .prompt import CONTENT_PLANNER_PROMPT, CONTENT_PLANNER_DESCRIPTION

MODEL = LiteLlm("openai/gpt-4o")

class SceneOutput(BaseModel):
    id: int = Field(description="Scene ID number")
    narration: str = Field(description="What the narrator of this scene should say")
    visual_description: str = Field(description="Detailed description for image generation")
    embedded_text: str = Field(description="Text overlay for the image")
    embedded_text_location: str = Field(description="Where to position the text on the image(i.e 'top-center', 'bottom-center', 'top-right', 'bottom-right', 'top-left', 'bottom-left','center')")
    duration: int

class ContentPlannerOutput(BaseModel):
    topic: str = Field(description="The topic of the Youtube short")
    total_duration: int = Field(description="Total duration of the Youtube short in seconds(max 20)")
    scenes: List[SceneOutput] = Field(description="List of Scenes (agent decides how many)")


content_planner_agent = Agent(
    name="ContentPlannerAgent",
    description=CONTENT_PLANNER_DESCRIPTION,
    instruction=CONTENT_PLANNER_PROMPT,
    model=MODEL,
    output_schema=ContentPlannerOutput,
    output_key="content_planner_output",

)