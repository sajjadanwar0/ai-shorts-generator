import base64

from google.genai import types
from google.adk.tools import ToolContext
from openai import OpenAI

client = OpenAI()


async def generate_images(tool_context: ToolContext) -> dict:
    """
    Generate images for each scene using OpenAI GPT-Image-1 API.

    Reads optimized prompts from tool context state (set by PromptBuilderAgent),
    generates a vertical 9:16 JPEG image for each scene, and saves each as an
    artifact. Skips scenes that already have a saved artifact.

    Args:
        tool_context: Tool context used to read state (prompt_builder_output)
            and save/load artifacts.

    Returns:
        A dictionary containing:
            - total_images (int): Total number of images generated or skipped
            - generated_images (list): Metadata for each image including
              scene_id, prompt preview, and filename
            - status (str): 'complete' when all scenes are processed
    """
    prompt_builder_output = tool_context.state.get("prompt_builder_output")
    optimized_prompts = prompt_builder_output.get("optimized_prompts")


    existing_artifacts = await tool_context.list_artifacts()

    generated_images = []

    for prompt in optimized_prompts:
        scene_id = prompt.get("scene_id")
        enhanced_prompt = prompt.get("enhanced_prompt")
        filename = f"scene_{scene_id}_image.jpeg"

        if filename in existing_artifacts:
            print(f"Skipping scene {scene_id}, artifact already exists: {filename}")
            generated_images.append({
                "scene_id": scene_id,
                "prompt": enhanced_prompt[:100],
                "filename": filename,
            })
            continue

        print(f"Generating image for scene {scene_id}...")

        image = client.images.generate(
            model="gpt-image-1",
            prompt=enhanced_prompt,
            n=1,
            quality="low",
            moderation="low",
            output_format="jpeg",
            background="opaque",
            size="1024x1536",
        )

        image_bytes = base64.b64decode(image.data[0].b64_json)

        artifact = types.Part(
            inline_data=types.Blob(
                mime_type="image/jpeg",
                data=image_bytes,
            )
        )

        await tool_context.save_artifact(filename=filename, artifact=artifact)

        print(f"✅ Saved image artifact: {filename}")

        generated_images.append({
            "scene_id": scene_id,
            "prompt": enhanced_prompt[:100],
            "filename": filename,
        })

    # Store filenames in state so VideoAssemblerAgent can find them
    tool_context.state["generated_image_files"] = [
        img["filename"] for img in generated_images
    ]

    return {
        "total_images": len(generated_images),
        "generated_images": generated_images,
        "status": "complete",
    }