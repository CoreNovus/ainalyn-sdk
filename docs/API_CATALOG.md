# API Service Directory

> This document lists all API services supported by the SDK, including feature descriptions, endpoint lists, and data structures.

## 1. Service Overview

The SDK supports the following 16 CoreNovus AI services:

| #  | Service                                                              | Client Class            | Description                              | Contract File                     |
| -- | -------------------------------------------------------------------- | ----------------------- | ---------------------------------------- | --------------------------------- |
| 1  | [Chat](#1-chat-chat-service)                                         | `ChatClient`            | Multi-provider chat service              | `chat-api.yaml`                   |
| 2  | [Translation](#2-translation-translation-service)                    | `TranslationClient`     | Multilingual translation service         | `translation-api.yaml`            |
| 3  | [Image Analysis](#3-image-analysis-image-analysis)                   | `ImageAnalysisClient`   | Image analysis and Q&A                   | `image-analysis-api.yaml`         |
| 4  | [Speech to Text](#4-speech-to-text-speech-to-text)                   | `SpeechToTextClient`    | Speech-to-text                           | `speech-to-text-api.yaml`         |
| 5  | [Speech to Image](#5-speech-to-image-speech-to-image)                | `SpeechToImageClient`   | Image generation from speech description | `speech-to-image-api.yaml`        |
| 6  | [Sketch to Image](#6-sketch-to-image-sketch-to-image)                | `SketchToImageClient`   | Sketch-to-image generation               | `sketch-to-image-api.yaml`        |
| 7  | [Sketch to Video](#7-sketch-to-video-sketch-to-video)                | `SketchToVideoClient`   | Sketch-to-video generation               | `sketch-to-video-api.yaml`        |
| 8  | [Video Analysis (YouTube)](#8-video-analysis-youtube-video-analysis) | `VideoAnalysisClient`   | YouTube video analysis                   | `video-analysis-youtube-api.yaml` |
| 9  | [Video Generation](#9-video-generation-video-generation)             | `VideoGenerationClient` | AI video generation                      | `video-generation-api.yaml`       |
| 10 | [Text to Music](#10-text-to-music-text-to-music)                     | `TextToMusicClient`     | Music generation from text descriptions  | `text-to-music-api.yaml`          |
| 11 | [Image to Music](#11-image-to-music-image-to-music)                  | `ImageToMusicClient`    | Music generation from images             | `image-to-music-api.yaml`         |
| 12 | [Travel Planning](#12-travel-planning-travel-planning)               | `TravelPlanningClient`  | AI travel planning                       | `travel-planning-api.yaml`        |
| 13 | [Presentation](#13-presentation-presentation-generation)             | `PresentationClient`    | AI presentation generation               | `presentation-api.yaml`           |
| 14 | [Counseling](#14-counseling-counseling-service)                      | `CounselingClient`      | AI counseling service                    | `counseling-api.yaml`             |
| 15 | [Settings](#15-settings-settings-management)                         | `SettingsClient`        | Settings management                      | `settings-api.yaml`               |
| 16 | [History](#16-history-history-records)                               | `HistoryClient`         | Unified history records                  | `history-api.yaml`                |

---

## 1. Chat (Chat Service)

### Overview

A multi-provider chat service supporting streaming and non-streaming modes, session management, and model switching.

### Supported Providers

* OpenAI (GPT-4, GPT-4o)
* Anthropic (Claude 3)
* Google (Gemini)

### Endpoints

| Method | Endpoint                              | Description                  |
| ------ | ------------------------------------- | ---------------------------- |
| POST   | `/api/v1/chat/send`                   | Send a chat message          |
| POST   | `/api/v1/chat/send-stream`            | Stream chat message response |
| POST   | `/api/v1/chat/sessions`               | Create a new session         |
| GET    | `/api/v1/chat/sessions/{id}`          | Retrieve a session           |
| DELETE | `/api/v1/chat/sessions/{id}`          | Delete a session             |
| GET    | `/api/v1/chat/sessions/{id}/messages` | Retrieve message list        |
| GET    | `/api/v1/chat/providers`              | Get available providers      |
| GET    | `/api/v1/chat/models`                 | Get available models         |

### SDK Usage

```python
# Send a message
response = await client.chat.send_message(
    message="Hello, how are you?",
    session_id="sess_123",  # optional
    provider="openai",       # optional
    model="gpt-4",           # optional
)

# Stream message
async for chunk in client.chat.stream_message(
    message="Tell me a story",
    session_id="sess_123",
):
    print(chunk.content, end="")

# Create session
session = await client.chat.create_session(
    system_prompt="You are a helpful assistant",
)
```

### Core Data Structures

```python
@dataclass
class ChatMessage:
    id: str
    role: str  # "user" | "assistant" | "system"
    content: str
    created_at: datetime
    metadata: dict[str, Any] | None = None

@dataclass
class ChatResponse:
    message: ChatMessage
    session_id: str
    usage: Usage
    provider: str
    model: str

@dataclass
class Usage:
    input_tokens: int
    output_tokens: int
    total_tokens: int
```

---

## 2. Translation (Translation Service)

### Overview

Multilingual translation service supporting language detection, text translation, document translation, and streaming translation.

### Supported Languages

30+ languages including: en, zh-TW, zh-CN, ja, ko, es, fr, de, etc.

### Endpoints

| Method | Endpoint                                     | Description                     |
| ------ | -------------------------------------------- | ------------------------------- |
| POST   | `/api/v1/translation/detect`                 | Detect language                 |
| POST   | `/api/v1/translation/translate`              | Translate text                  |
| POST   | `/api/v1/translation/translate-stream`       | Stream translation              |
| POST   | `/api/v1/translation/document/upload`        | Upload document for translation |
| GET    | `/api/v1/translation/document/{id}/status`   | Check translation status        |
| GET    | `/api/v1/translation/document/{id}/download` | Download translated document    |
| GET    | `/api/v1/translation/languages`              | Get supported language list     |

### SDK Usage

```python
# Detect language
detected = await client.translation.detect_language("Hello world")
print(f"Language: {detected.language}, confidence: {detected.confidence}")

# Translate text
result = await client.translation.translate(
    text="Hello world",
    source_language="en",  # optional, auto-detected
    target_language="zh-TW",
)
print(result.translated_text)

# Document translation
task = await client.translation.upload_document(
    file_path="document.pdf",
    target_language="ja",
)
```

---

## 3. Image Analysis

### Overview

Image analysis service supporting image description, object detection, text extraction, and Q&A.

### Endpoints

| Method | Endpoint                              | Description                    |
| ------ | ------------------------------------- | ------------------------------ |
| POST   | `/api/v1/image-analysis/analyze`      | Analyze image                  |
| POST   | `/api/v1/image-analysis/describe`     | Describe image                 |
| POST   | `/api/v1/image-analysis/detect`       | Object detection               |
| POST   | `/api/v1/image-analysis/extract-text` | Text extraction (OCR)          |
| POST   | `/api/v1/image-analysis/ask`          | Image-based question answering |

### SDK Usage

```python
# Analyze image
result = await client.image_analysis.analyze(
    image_path="photo.jpg",
    features=["description", "objects", "text"],
)

# Image Q&A
answer = await client.image_analysis.ask(
    image_path="diagram.png",
    question="What is shown in this diagram?",
)
```

---

## 4. Speech to Text

### Overview

Speech-to-text service supporting multiple audio formats, multilingual transcription, speaker diarization, and timestamps.

### Supported Formats

WAV, MP3, M4A, WebM, FLAC

### Endpoints

| Method | Endpoint                                  | Description                                   |
| ------ | ----------------------------------------- | --------------------------------------------- |
| POST   | `/api/v1/speech-to-text/transcribe`       | Transcribe audio                              |
| POST   | `/api/v1/speech-to-text/transcribe-async` | Async transcription (long audio)              |
| GET    | `/api/v1/speech-to-text/tasks/{id}`       | Check transcription status                    |
| POST   | `/api/v1/speech-to-text/stream`           | Real-time streaming transcription (WebSocket) |
| GET    | `/api/v1/speech-to-text/languages`        | Get supported languages                       |

### SDK Usage

```python
# Transcribe audio
result = await client.speech_to_text.transcribe(
    audio_path="recording.mp3",
    language="zh-TW",
    enable_timestamps=True,
    enable_speaker_diarization=True,
)

print(result.text)
for word in result.words:
    print(f"{word.word} ({word.start_time:.2f}s - {word.end_time:.2f}s)")
```

---

## 5. Speech to Image

### Overview

Generate images from spoken descriptions by first transcribing speech and then generating images accordingly.

### Endpoints

| Method | Endpoint                                  | Description                |
| ------ | ----------------------------------------- | -------------------------- |
| POST   | `/api/v1/speech-to-image/generate`        | Generate image from speech |
| POST   | `/api/v1/speech-to-image/generate-batch`  | Batch variations           |
| GET    | `/api/v1/speech-to-image/generation/{id}` | Check generation status    |
| GET    | `/api/v1/speech-to-image/styles`          | Get supported styles       |

### Supported Styles

realistic, artistic, cartoon, abstract, fantasy, minimalist, vintage, futuristic

### SDK Usage

```python
# Speech to image
result = await client.speech_to_image.generate(
    audio_path="description.wav",
    language="zh-TW",
    style="artistic",
    options=ImageOptions(
        size="1024x1024",
        quality="hd",
    ),
)

print(f"Generated image: {result.images[0].url}")
print(f"Transcription: {result.transcription}")
```

---

## 6. Sketch to Image

### Overview

Convert sketches into complete images.

### Endpoints

| Method | Endpoint                             | Description                |
| ------ | ------------------------------------ | -------------------------- |
| POST   | `/api/v1/sketch-to-image/generate`   | Generate image from sketch |
| GET    | `/api/v1/sketch-to-image/tasks/{id}` | Check task status          |
| GET    | `/api/v1/sketch-to-image/styles`     | Get supported styles       |

---

## 7. Sketch to Video

### Overview

Generate animated videos from sketches.

### Endpoints

| Method | Endpoint                                 | Description                |
| ------ | ---------------------------------------- | -------------------------- |
| POST   | `/api/v1/sketch-to-video/generate-image` | Generate image from sketch |
| POST   | `/api/v1/sketch-to-video/image-to-video` | Convert image to video     |
| GET    | `/api/v1/sketch-to-video/tasks/{id}`     | Check task status          |

---

## 8. Video Analysis (YouTube)

### Overview

YouTube video analysis service supporting summarization, Q&A, and conversational interaction.

### Endpoints

| Method | Endpoint                                    | Description             |
| ------ | ------------------------------------------- | ----------------------- |
| POST   | `/api/v1/video-analysis/youtube/analyze`    | Analyze YouTube video   |
| GET    | `/api/v1/video-analysis/youtube/tasks/{id}` | Check analysis status   |
| POST   | `/api/v1/video-analysis/youtube/chat`       | Chat with video content |
| POST   | `/api/v1/video-analysis/youtube/validate`   | Validate YouTube URL    |

### SDK Usage

```python
# Analyze YouTube video
task = await client.video_analysis.analyze_youtube(
    youtube_url="https://www.youtube.com/watch?v=xxx",
    question="What is the main topic of this video?",
)

# Wait for result
result = await client.video_analysis.wait_for_task(task.task_id)
print(result.answer)

# Continue conversation
response = await client.video_analysis.chat(
    task_id=task.task_id,
    message="Can you summarize the key points?",
)
```

---

## 9. Video Generation

### Overview

AI video generation service supporting script-based or image-sequence input.

### Endpoints

| Method | Endpoint                                       | Description                |
| ------ | ---------------------------------------------- | -------------------------- |
| POST   | `/api/v1/video-generation/upload-images`       | Upload image sequence      |
| POST   | `/api/v1/video-generation/tasks`               | Create generation task     |
| GET    | `/api/v1/video-generation/tasks`               | Get task list              |
| GET    | `/api/v1/video-generation/tasks/{id}`          | Get task details           |
| DELETE | `/api/v1/video-generation/tasks/{id}`          | Cancel task                |
| GET    | `/api/v1/video-generation/tasks/{id}/download` | Download video             |
| GET    | `/api/v1/video-generation/ws`                  | WebSocket progress updates |

### SDK Usage

```python
# Generate video from text
task = await client.video_generation.create_task(
    input_mode="text",
    content={"text_script": "A beautiful sunset over the ocean..."},
    video_settings=VideoSettings(
        duration=10,
        resolution="1080p",
        style="cinematic",
    ),
)

# Watch progress
async for progress in client.video_generation.watch_progress(task.id):
    print(f"Progress: {progress.progress}%")
```

---

## 10. Text to Music

### Overview

Generate music based on text descriptions.

### Endpoints

| Method | Endpoint                                    | Description          |
| ------ | ------------------------------------------- | -------------------- |
| POST   | `/api/v1/text-to-music/generate`            | Generate music       |
| GET    | `/api/v1/text-to-music/tasks/{id}`          | Check task status    |
| GET    | `/api/v1/text-to-music/tasks/{id}/download` | Download music       |
| GET    | `/api/v1/text-to-music/genres`              | Get supported genres |

### SDK Usage

```python
# Generate music
task = await client.text_to_music.generate(
    prompt="A peaceful piano melody with soft strings",
    genre="classical",
    duration=60,
    mood="relaxing",
)

# Wait and download
result = await client.text_to_music.wait_and_download(
    task_id=task.task_id,
    output_path="music.mp3",
)
```

---

## 11. Image to Music

### Overview

Generate music according to image content.

### Endpoints

| Method | Endpoint                                     | Description               |
| ------ | -------------------------------------------- | ------------------------- |
| POST   | `/api/v1/image-to-music/generate`            | Generate music from image |
| GET    | `/api/v1/image-to-music/tasks/{id}`          | Check task status         |
| GET    | `/api/v1/image-to-music/tasks/{id}/download` | Download music            |

---

## 12. Travel Planning

### Overview

AI travel planning service offering personalized itineraries, budgeting, and destination insights.

### Travel Types

leisure, business, adventure, cultural, family, romantic, budget, luxury

### Endpoints

| Method | Endpoint                            | Description                 |
| ------ | ----------------------------------- | --------------------------- |
| POST   | `/api/v1/travel/planning`           | AI travel planning          |
| POST   | `/api/v1/travel/planning/stream`    | Stream planning results     |
| GET    | `/api/v1/travel/templates`          | Get itinerary templates     |
| GET    | `/api/v1/travel/destination/{name}` | Get destination information |

### SDK Usage

```python
# Get travel plan
plan = await client.travel_planning.plan(
    travel_type="leisure",
    user_question="Plan a 5-day trip to Tokyo",
    duration={"days": 5, "nights": 4},
    context={
        "budget": "medium",
        "travelers": 2,
        "preferences": ["food", "culture"],
    },
)

print(plan.response)
if plan.structured_plan:
    for day in plan.structured_plan.itinerary:
        print(f"Day {day.day_number}: {day.theme}")
```

---

## 13. Presentation

### Overview

AI presentation generation service that automatically creates professional presentations from a topic.

### Endpoints

| Method | Endpoint                           | Description                |
| ------ | ---------------------------------- | -------------------------- |
| POST   | `/api/v1/presentation/generate`    | Generate presentation      |
| GET    | `/api/v1/presentation/tasks/{id}`  | Check generation status    |
| GET    | `/api/v1/presentation/{id}`        | Get presentation details   |
| PUT    | `/api/v1/presentation/{id}`        | Update presentation        |
| DELETE | `/api/v1/presentation/{id}`        | Delete presentation        |
| POST   | `/api/v1/presentation/{id}/export` | Export presentation        |
| GET    | `/api/v1/presentation/templates`   | Get templates              |
| GET    | `/api/v1/presentation/ws`          | WebSocket progress updates |

### Export Formats

PPTX, PDF, HTML, PNG, JPG

### SDK Usage

```python
# Generate presentation
task = await client.presentation.generate(
    topic="Introduction to Machine Learning",
    slide_count=10,
    theme="professional",
    language="zh-TW",
    include_images=True,
)

# Wait for completion
presentation = await client.presentation.wait_for_task(task.task_id)

# Export
export = await client.presentation.export(
    presentation_id=presentation.id,
    format="pptx",
)
print(f"Download: {export.download_url}")
```

---

## 14. Counseling

### Overview

AI counseling conversation service for specific domain consultation scenarios.

### Endpoints

| Method | Endpoint                           | Description               |
| ------ | ---------------------------------- | ------------------------- |
| POST   | `/api/v1/counseling/send`          | Send counseling message   |
| POST   | `/api/v1/counseling/send-stream`   | Stream counseling message |
| POST   | `/api/v1/counseling/sessions`      | Create counseling session |
| GET    | `/api/v1/counseling/sessions/{id}` | Retrieve session          |

---

## 15. Settings

### Overview

User settings management service.

### Endpoints

| Method | Endpoint                 | Description     |
| ------ | ------------------------ | --------------- |
| GET    | `/api/v1/settings`       | Get settings    |
| PUT    | `/api/v1/settings`       | Update settings |
| POST   | `/api/v1/settings/reset` | Reset settings  |

---

## 16. History

### Overview

Unified usage history service for managing activity across all features.

### Supported Feature Types

chat, translation, image_analysis, speech_to_text, speech_to_image, sketch_to_image, sketch_to_video, video_analysis, video_generation, text_to_music, image_to_music, travel_planning, presentation, counseling

### Endpoints

| Method | Endpoint                      | Description          |
| ------ | ----------------------------- | -------------------- |
| GET    | `/api/v1/history`             | Get history          |
| GET    | `/api/v1/history/{id}`        | Get single record    |
| DELETE | `/api/v1/history/{id}`        | Delete single record |
| POST   | `/api/v1/history/bulk-delete` | Bulk delete          |
| POST   | `/api/v1/history/clear`       | Clear history        |
| POST   | `/api/v1/history/export`      | Export history       |
| GET    | `/api/v1/history/stats`       | Get statistics       |

### SDK Usage

```python
# Get history
history = await client.history.get_history(
    feature="chat",
    date_from=datetime(2024, 1, 1),
    limit=50,
)

# Export history
export = await client.history.export(
    format="json",
    feature="chat",
    include_content=True,
)
```

---

## Common Data Structures

### Basic API Response Structure

```python
@dataclass
class ApiResponse[T]:
    success: bool
    data: T | None = None
    error: str | None = None
    message: str | None = None
    code: str | None = None

@dataclass
class PaginatedResponse[T]:
    items: list[T]
    pagination: Pagination

@dataclass
class Pagination:
    total: int
    page: int
    limit: int
    total_pages: int
    has_more: bool
```

### Async Task Structure

```python
@dataclass
class AsyncTask:
    task_id: str
    status: TaskStatus  # pending, processing, completed, failed
    progress: int  # 0-100
    created_at: datetime
    completed_at: datetime | None = None
    error: str | None = None

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

*Last Updated: 2024-12*