import os
import re
import subprocess
import tempfile

from google.adk.tools import ToolContext
from google.genai import types


async def assemble_video(tool_context: ToolContext) -> str:
    """
    Assemble generated image and audio artifacts into a final vertical YouTube Shorts video.

    Reads the content plan from tool context state, retrieves all previously generated
    image (JPEG) and audio (MP3) artifacts, and uses FFmpeg to combine them into a
    single 1080x1920 MP4 video file. Each scene's image is displayed for its specified
    duration while the corresponding narration audio plays. The final video is saved
    as an artifact named 'youtube_short_final.mp4'.

    Args:
        tool_context: Tool context used to access state (content_planner_output,
            generated_image_files, generated_audio_files), load image and audio
            artifacts, and save the final video artifact.

    Returns:
        A string representation of a result dictionary containing:
            - status (str): 'success' if assembly completed
            - scenes_processed (int): Number of scenes included in the video
            - total_duration (float): Total video duration in seconds
            - output_file (str): Artifact filename of the final video
            - resolution (str): Video resolution (1080x1920)
            - format (str): Video format description (MP4 H.264/AAC)

    Raises:
        subprocess.CalledProcessError: If FFmpeg command fails during video assembly
        ValueError: If no media artifacts are found to assemble
        KeyError: If content_planner_output is missing from tool context state
    """
    temp_files = []

    try:
        content_planner_output = tool_context.state.get("content_planner_output")
        scenes = content_planner_output.get("scenes")

        # Read filenames saved to state by generate_images and generate_narrations tools
        image_files = tool_context.state.get("generated_image_files", [])
        audio_files = tool_context.state.get("generated_audio_files", [])

        print(f"Image files from state ({len(image_files)}): {image_files}")
        print(f"Audio files from state ({len(audio_files)}): {audio_files}")

        def extract_scene_number(filename: str) -> int:
            """
            Extract the scene number from an artifact filename.

            Args:
                filename: Artifact filename in the format 'scene_N_...'

            Returns:
                The integer scene number, or 0 if no match is found.
            """
            match = re.search(r"scene_(\d+)_", filename)
            return int(match.group(1)) if match else 0

        image_files.sort(key=extract_scene_number)
        audio_files.sort(key=extract_scene_number)

        temp_image_paths = []
        temp_audio_paths = []

        # Load images independently — do NOT zip, audio may not exist yet
        for image_name in image_files:
            image_artifact = await tool_context.load_artifact(filename=image_name)

            if image_artifact and image_artifact.inline_data:
                temp_image = tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False)
                temp_image.write(image_artifact.inline_data.data)
                temp_image.close()
                temp_image_paths.append(temp_image.name)
                temp_files.append(temp_image.name)
                print(f"Loaded image: {image_name} → {temp_image.name}")
            else:
                print(f"Failed to load image artifact: {image_name}")

        # Load audio independently
        for audio_name in audio_files:
            audio_artifact = await tool_context.load_artifact(filename=audio_name)

            if audio_artifact and audio_artifact.inline_data:
                temp_audio = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                temp_audio.write(audio_artifact.inline_data.data)
                temp_audio.close()
                temp_audio_paths.append(temp_audio.name)
                temp_files.append(temp_audio.name)
                print(f"Loaded audio: {audio_name} → {temp_audio.name}")
            else:
                print(f"Failed to load audio artifact: {audio_name}")

        print(f"Temp image paths ({len(temp_image_paths)}): {temp_image_paths}")
        print(f"Temp audio paths ({len(temp_audio_paths)}): {temp_audio_paths}")

        if not temp_image_paths or not temp_audio_paths:
            raise ValueError(
                f"No media files loaded.\n"
                f"  Images found: {len(image_files)} → {image_files}\n"
                f"  Audio found:  {len(audio_files)} → {audio_files}\n"
                f"  Images loaded: {len(temp_image_paths)}\n"
                f"  Audio loaded:  {len(temp_audio_paths)}\n"
                f"Make sure both ImageBuilderAgent and VoiceGeneratorAgent have completed successfully."
            )

        if len(temp_image_paths) != len(temp_audio_paths):
            raise ValueError(
                f"Mismatched media counts: "
                f"{len(temp_image_paths)} images vs {len(temp_audio_paths)} audio files. "
                f"Ensure every scene has both an image and an audio artifact."
            )

        input_args = []
        filter_parts = []

        for i, (temp_image, temp_audio) in enumerate(zip(temp_image_paths, temp_audio_paths)):
            input_args.extend(["-i", temp_image, "-i", temp_audio])
            scene_duration = scenes[i].get("duration", 4)
            total_frames = int(30 * scene_duration)

            filter_parts.append(
                f"[{i * 2}:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
                f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,"
                f"loop={total_frames - 1}:size=1:start=0[v{i}]"
            )
            filter_parts.append(f"[{i * 2 + 1}:a]anull[a{i}]")

        # Use actual number of loaded scenes, not content plan length
        num_scenes = len(temp_image_paths)

        # Concatenate all video and audio streams
        video_inputs = "".join([f"[v{i}]" for i in range(num_scenes)])
        audio_inputs = "".join([f"[a{i}]" for i in range(num_scenes)])
        filter_parts.append(f"{video_inputs}concat=n={num_scenes}:v=1:a=0[outv]")
        filter_parts.append(f"{audio_inputs}concat=n={num_scenes}:v=0:a=1[outa]")

        # Create temporary output file
        temp_output = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        temp_output.close()
        output_path = temp_output.name
        temp_files.append(output_path)

        # Build final FFmpeg command
        ffmpeg_cmd = (
            ["ffmpeg", "-y"]
            + input_args
            + [
                "-filter_complex",
                ";".join(filter_parts),
                "-map", "[outv]",
                "-map", "[outa]",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                output_path,
            ]
        )

        print("Executing FFmpeg command...")
        print(" ".join(ffmpeg_cmd))

        # Execute FFmpeg and capture stderr for better error messages
        result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"FFmpeg stderr:\n{result.stderr}")
            raise subprocess.CalledProcessError(
                result.returncode, ffmpeg_cmd,
                output=result.stdout,
                stderr=result.stderr,
            )

        print("✅ FFmpeg completed successfully")

        with open(output_path, "rb") as f:
            video_data = f.read()

        artifact = types.Part(
            inline_data=types.Blob(
                mime_type="video/mp4",
                data=video_data,
            )
        )

        await tool_context.save_artifact(
            filename="youtube_short_final.mp4", artifact=artifact
        )

        total_duration = sum(scene.get("duration", 4) for scene in scenes)

        result_info = {
            "status": "success",
            "scenes_processed": num_scenes,
            "total_duration": total_duration,
            "output_file": "youtube_short_final.mp4",
            "resolution": "1080x1920",
            "format": "MP4 (H.264/AAC)",
        }

        print(f"Video assembly successfully completed! Created {total_duration}s YouTube Short.")

        return str(result_info)

    finally:
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except Exception:
                pass