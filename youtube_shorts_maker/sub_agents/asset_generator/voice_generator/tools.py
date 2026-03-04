from typing import List, Dict, Any

from google.genai import types
from google.adk.tools import ToolContext
from openai import OpenAI

client = OpenAI()


async def generate_narrations(
    tool_context: ToolContext,
    voice: str,
    voice_instructions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate narration audio for each scene using OpenAI TTS API.

    Args:
        tool_context: Tool context to access artifacts and save files
        voice: Selected voice for TTS (alloy, echo, fable, onyx, nova, shimmer)
        voice_instructions: List of dictionaries containing narration instructions
            for each scene. Each dictionary should contain:
                - input (str): The exact text to speak for that scene
                - instructions (str): Combined instruction for speed and tone
                  based on scene duration and content
                - scene_id (int): The scene number

    Returns:
        A dictionary containing:
            - success (bool): Whether all narrations were generated successfully
            - narrations (list): Array of generated audio file metadata
            - total_narrations (int): Total number of scenes processed
            - voice_used (str): The voice model used for generation
    """
    # Fix: missing await
    existing_artifacts = await tool_context.list_artifacts()

    generated_narrations = []

    for instruction in voice_instructions:
        text_input = instruction.get("input")
        instructions = instruction.get("instructions")
        scene_id = instruction.get("scene_id")

        filename = f"scene_{scene_id}_narration.mp3"

        if filename in existing_artifacts:
            print(f"Skipping scene {scene_id}, artifact already exists: {filename}")
            generated_narrations.append({
                "scene_id": scene_id,
                "filename": filename,
                "input": text_input,
                "instructions": instructions[:50],
            })
            continue

        print(f"🎙️  Generating narration for scene {scene_id}...")

        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text_input,
            instructions=instructions,
        ) as response:
            audio_data = response.read()

        artifact = types.Part(
            inline_data=types.Blob(
                mime_type="audio/mpeg",
                data=audio_data,
            )
        )

        await tool_context.save_artifact(filename=filename, artifact=artifact)

        print(f"Saved narration artifact: {filename}")

        generated_narrations.append({
            "scene_id": scene_id,
            "filename": filename,
            "input": text_input,
            "instructions": instructions[:50],
        })

    # Store filenames in state so VideoAssemblerAgent can find them
    tool_context.state["generated_audio_files"] = [
        n["filename"] for n in generated_narrations
    ]

    return {
        "success": True,
        "narrations": generated_narrations,
        "total_narrations": len(generated_narrations),
        "voice_used": voice,
    }