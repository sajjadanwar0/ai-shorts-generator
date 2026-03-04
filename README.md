# 🎬 YouTube Shorts Maker

An AI-powered multi-agent pipeline that autonomously generates complete vertical YouTube Shorts videos (9:16) from a single text prompt — including script, images, voiceover, and final MP4 assembly.

Built with [Google ADK](https://google.github.io/adk-docs/), OpenAI GPT-4o, GPT-Image-1, and TTS APIs.

---

## ✨ Demo

> *"Create a 5-scene educational short about the Roman Empire"*

The pipeline automatically:
1. Plans a structured 5-scene script
2. Generates optimized vertical images for each scene
3. Creates AI voiceover narration
4. Assembles everything into a final MP4 — ready to upload

---

## 🏗️ Architecture

```
ShortsProducerAgent (Orchestrator)
├── ContentPlannerAgent        → Structured 5-scene JSON script
├── AssetGeneratorAgent        → Images + Audio in parallel
│   ├── ImageGeneratorAgent (Sequential)
│   │   ├── PromptBuilderAgent → Optimizes prompts for GPT-Image-1
│   │   └── ImageBuilderAgent  → Generates 1080x1920 JPEG images
│   └── VoiceGeneratorAgent    → MP3 narration via OpenAI TTS
└── VideoAssemblerAgent        → FFmpeg MP4 assembly (1080x1920)
```

### Agent Responsibilities

| Agent | Model | Role |
|---|---|---|
| `ShortsProducerAgent` | GPT-4o | Primary orchestrator, user interaction |
| `ContentPlannerAgent` | GPT-4o | Generates structured 5-scene script with timing |
| `PromptBuilderAgent` | GPT-4o | Optimizes visual prompts for vertical format |
| `ImageBuilderAgent` | GPT-Image-1 | Generates 1080x1920 scene images |
| `VoiceGeneratorAgent` | GPT-4o-mini-TTS | Generates scene narration audio |
| `VideoAssemblerAgent` | GPT-4o | Orchestrates FFmpeg video assembly |

---

## 🚀 Getting Started

### Prerequisites

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) package manager
- FFmpeg installed on your system
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/sajjadanwar0/ai-shorts-generator.git
cd ai-shorts-generator

# Install dependencies
uv sync
```

### Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Install FFmpeg

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
winget install ffmpeg
```

---

## 🎯 Usage

### Run with Google ADK Web UI

```bash
adk web
```

Then open your browser at `http://localhost:8000` and start chatting with the `ShortsProducerAgent`.

### Example Prompts

```
Create a 30-second educational short about black holes

Make an energetic fitness short showing a 5-step morning workout routine

Create a cooking tutorial short for a quick pasta recipe
```

---

## 📁 Project Structure

```
youtube_shorts_maker/
├── agent.py                          # Root agent (ShortsProducerAgent)
├── prompt.py                         # Orchestrator prompts
├── sub_agents/
│   ├── content_planner/
│   │   ├── agent.py
│   │   └── prompt.py
│   ├── asset_generator/
│   │   ├── agent.py
│   │   ├── prompt.py
│   │   ├── image_generator/
│   │   │   ├── agent.py              # SequentialAgent
│   │   │   ├── image_builder/
│   │   │   │   ├── agent.py
│   │   │   │   ├── prompt.py
│   │   │   │   └── tools.py          # generate_images()
│   │   │   └── prompt_builder/
│   │   │       ├── agent.py
│   │   │       └── prompt.py
│   │   └── voice_generator/
│   │       ├── agent.py
│   │       ├── prompt.py
│   │       └── tools.py              # generate_narrations()
│   └── video_assembler/
│       ├── agent.py
│       └── tools.py                  # assemble_video()
├── .env
├── main.py
└── pyproject.toml
```

---

## ⚙️ Pipeline Flow

```
User Input
    │
    ▼
ContentPlannerAgent
    │  Outputs: content_planner_output (5 scenes with timing,
    │           narration text, visual descriptions, embedded text)
    ▼
AssetGeneratorAgent
    ├── ImageGeneratorAgent
    │       ├── PromptBuilderAgent → prompt_builder_output
    │       └── ImageBuilderAgent  → scene_N_image.jpeg artifacts
    └── VoiceGeneratorAgent        → scene_N_narration.mp3 artifacts
    │
    ▼
VideoAssemblerAgent
    │  Reads state: generated_image_files, generated_audio_files
    │  Runs FFmpeg to combine scenes with timing
    ▼
youtube_short_final.mp4 (1080x1920, H.264/AAC, 30fps)
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| [Google ADK](https://google.github.io/adk-docs/) | Multi-agent orchestration framework |
| [LiteLLM](https://litellm.ai/) | Unified LLM API interface |
| [OpenAI GPT-4o](https://platform.openai.com/docs/models/gpt-4o) | Reasoning & orchestration |
| [OpenAI GPT-Image-1](https://platform.openai.com/docs/guides/images) | Vertical image generation |
| [OpenAI TTS](https://platform.openai.com/docs/guides/text-to-speech) | Voice narration (gpt-4o-mini-tts) |
| [FFmpeg](https://ffmpeg.org/) | Video assembly & encoding |
| [Pydantic](https://docs.pydantic.dev/) | Structured agent output schemas |

---

## 🎙️ Voice Options

The `VoiceGeneratorAgent` automatically selects the best voice based on content type:

| Voice | Best For |
|---|---|
| `alloy` | Educational, general content |
| `echo` | Relaxation, wellness |
| `fable` | Cooking, storytelling |
| `nova` | Fitness, energetic content |
| `onyx` | Professional, business |
| `shimmer` | Creative, artistic |

---

## 📦 Dependencies

```toml
[project]
requires-python = ">=3.12"
dependencies = [
    "dotenv>=0.9.9",
    "google-adk>=1.26.0",
    "google-genai>=1.65.0",
    "litellm>=1.82.0",
    "openai>=2.24.0",
    "pydantic>=2.12.5",
]
```


## 🙏 Acknowledgements

- [Google ADK](https://google.github.io/adk-docs/) for the powerful multi-agent framework
- [OpenAI](https://openai.com/) for GPT-4o, GPT-Image-1, and TTS APIs
- [FFmpeg](https://ffmpeg.org/) for video processing
