from google.adk.agents import Agent
from google.adk.models import LiteLlm

from .prompt import VOICE_GENERATOR_DESCRIPTION, VOICE_GENERATOR_PROMPT
from .tools import generate_narrations

MODEL = LiteLlm("openai/gpt-4o")

voice_generator_agent = Agent(
    name="VoiceGeneratorAgent",
    model=MODEL,
    description=VOICE_GENERATOR_DESCRIPTION,
    instruction=VOICE_GENERATOR_PROMPT,
    tools=[
        generate_narrations
    ]
)