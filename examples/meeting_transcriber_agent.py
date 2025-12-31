"""Meeting Transcriber Agent - Speech-to-Text MVP Example.

This example demonstrates a complete Agent for transcribing meeting recordings
(approximately 1 hour long) using OpenAI Whisper with streaming support.

IMPORTANT:
- This code only DESCRIBES what the agent should do
- The SDK does NOT execute this agent
- All execution happens on Platform Core

Key features:
- Audio segmentation for long recordings (>25MB Whisper API limit)
- Streaming transcription using OpenAI Whisper
- Timestamp-aligned transcript output
- Optional meeting summary generation

Reusable components defined:
- audio-segmenter: Module for splitting long audio files
- speech-to-text: Tool for OpenAI Whisper transcription
- transcript-merger: Module for combining segmented transcripts
- meeting-summarizer: Prompt for generating meeting summaries
"""

from __future__ import annotations

from ainalyn import (
    AgentBuilder,
    ModuleBuilder,
    NodeBuilder,
    PromptBuilder,
    ToolBuilder,
    WorkflowBuilder,
)
from ainalyn.api import export_yaml, validate
from ainalyn.domain.entities import CompletionCriteria, EIPBinding, EIPDependency


def create_meeting_transcriber_agent():
    """Create a meeting transcriber agent with streaming support."""

    # ==========================================================================
    # EIP Dependencies - Declare which EIPs this Agent requires
    # ==========================================================================
    openai_whisper_dep = EIPDependency(
        provider="openai",
        service="whisper",
        version=">=1.0.0",
        config_hints={
            "streaming": True,  # Enable streaming for real-time progress
            "model": "whisper-1",
            "response_format": "verbose_json",  # Include timestamps
            "language": "auto",  # Auto-detect language
        },
    )

    openai_gpt_dep = EIPDependency(
        provider="openai",
        service="gpt-4",
        version=">=1.0.0",
        config_hints={
            "streaming": True,
            "temperature": 0.3,  # Lower temperature for factual summary
        },
    )

    # ==========================================================================
    # Completion Criteria - Define success/failure conditions
    # ==========================================================================
    completion_criteria = CompletionCriteria(
        success="完整的會議轉錄稿已生成，包含時間戳記和說話者標記",
        failure="音訊格式不支援、檔案損壞、或語音無法辨識",
    )

    # ==========================================================================
    # Reusable Module 1: Audio Segmenter
    # Splits long audio files into segments suitable for Whisper API
    # ==========================================================================
    audio_segmenter = (
        ModuleBuilder("audio-segmenter")
        .description(
            "將長音訊檔案切分成符合 Whisper API 限制的片段。"
            "每個片段最大 25MB，保持語句完整性以避免切斷說話內容。"
            "Implementation provided by platform EIP."
        )
        .input_schema(
            {
                "type": "object",
                "properties": {
                    "audio_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "音訊檔案的 URL 或存儲路徑",
                    },
                    "max_segment_size_mb": {
                        "type": "number",
                        "default": 24,
                        "description": "每個片段的最大大小（MB）",
                    },
                    "overlap_seconds": {
                        "type": "number",
                        "default": 2,
                        "description": "片段間重疊秒數，確保語句不被切斷",
                    },
                },
                "required": ["audio_url"],
            }
        )
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "segments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "segment_id": {"type": "string"},
                                "segment_url": {"type": "string", "format": "uri"},
                                "start_time": {"type": "number"},
                                "end_time": {"type": "number"},
                                "duration_seconds": {"type": "number"},
                            },
                        },
                        "description": "切分後的音訊片段列表",
                    },
                    "total_duration_seconds": {
                        "type": "number",
                        "description": "原始音訊總長度（秒）",
                    },
                    "segment_count": {
                        "type": "integer",
                        "description": "總片段數",
                    },
                },
            }
        )
        .build()
    )

    # ==========================================================================
    # Reusable Tool: Speech-to-Text (OpenAI Whisper)
    # Core transcription capability with streaming support
    # ==========================================================================
    speech_to_text = (
        ToolBuilder("speech-to-text")
        .description(
            "使用 OpenAI Whisper 進行語音轉文字。"
            "支援 streaming 模式，可即時回傳轉錄進度。"
            "輸出包含詳細時間戳記和置信度分數。"
        )
        .eip_binding(EIPBinding(provider="openai", service="whisper"))
        .input_schema(
            {
                "type": "object",
                "properties": {
                    "audio_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "要轉錄的音訊片段 URL",
                    },
                    "language": {
                        "type": "string",
                        "default": "auto",
                        "description": "音訊語言（auto 為自動偵測）",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "可選的提示詞，幫助模型理解專業術語",
                    },
                    "timestamp_granularity": {
                        "type": "string",
                        "enum": ["word", "segment"],
                        "default": "segment",
                        "description": "時間戳記粒度",
                    },
                },
                "required": ["audio_url"],
            }
        )
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "轉錄的完整文字",
                    },
                    "segments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "start": {"type": "number"},
                                "end": {"type": "number"},
                                "text": {"type": "string"},
                                "confidence": {"type": "number"},
                            },
                        },
                        "description": "帶時間戳的分段轉錄",
                    },
                    "language": {
                        "type": "string",
                        "description": "偵測到的語言",
                    },
                    "duration": {
                        "type": "number",
                        "description": "音訊長度（秒）",
                    },
                },
            }
        )
        .build()
    )

    # ==========================================================================
    # Reusable Module 2: Transcript Merger
    # Combines segmented transcripts into a unified document
    # ==========================================================================
    transcript_merger = (
        ModuleBuilder("transcript-merger")
        .description(
            "合併多個分段轉錄結果為完整的會議記錄。處理重疊部分的去重，校正時間戳記。"
        )
        .input_schema(
            {
                "type": "object",
                "properties": {
                    "transcripts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "segment_id": {"type": "string"},
                                "start_time": {"type": "number"},
                                "text": {"type": "string"},
                                "segments": {"type": "array"},
                            },
                        },
                        "description": "各片段的轉錄結果",
                    },
                    "overlap_seconds": {
                        "type": "number",
                        "default": 2,
                        "description": "片段間重疊秒數，用於去重",
                    },
                },
                "required": ["transcripts"],
            }
        )
        .output_schema(
            {
                "type": "object",
                "properties": {
                    "full_transcript": {
                        "type": "string",
                        "description": "完整的會議轉錄文字",
                    },
                    "timestamped_segments": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "number"},
                                "end": {"type": "number"},
                                "text": {"type": "string"},
                            },
                        },
                        "description": "帶時間戳的完整分段",
                    },
                    "total_duration_seconds": {
                        "type": "number",
                    },
                    "word_count": {
                        "type": "integer",
                    },
                },
            }
        )
        .build()
    )

    # ==========================================================================
    # Reusable Prompt: Meeting Summarizer
    # Optional LLM-based summary generation
    # ==========================================================================
    meeting_summarizer = (
        PromptBuilder("meeting-summarizer")
        .description("生成會議摘要，包含重點議題、決議事項和待辦事項")
        .template("""請根據以下會議轉錄內容，生成一份結構化的會議摘要。

## 會議轉錄
{{transcript}}

## 要求格式
請輸出以下結構：

### 會議基本資訊
- 會議時長：{{duration_minutes}} 分鐘
- 主要語言：{{language}}

### 會議摘要
（3-5 句話概述會議主要內容）

### 重點議題
1. ...
2. ...

### 決議事項
- [ ] ...

### 待辦事項
- [ ] 負責人：... / 期限：...

### 關鍵引述
（如有重要的原話引述，請列出並標註時間戳記）
""")
        .variables("transcript", "duration_minutes", "language")
        .build()
    )

    # ==========================================================================
    # Workflow: Main Transcription Pipeline
    # ==========================================================================

    # Node 1: Segment the audio
    segment_node = (
        NodeBuilder("segment-audio")
        .description("將長音訊切分成適合處理的片段")
        .uses_module("audio-segmenter")
        .inputs("audio_url")
        .outputs("segments", "segment_count")
        .next_nodes("transcribe-segments")
        .build()
    )

    # Node 2: Transcribe each segment (parallel processing by Platform Core)
    transcribe_node = (
        NodeBuilder("transcribe-segments")
        .description("對每個片段進行語音轉文字，支援 streaming")
        .uses_tool("speech-to-text")
        .inputs("segments")
        .outputs("segment_transcripts")
        .next_nodes("merge-transcripts")
        .build()
    )

    # Node 3: Merge transcripts
    merge_node = (
        NodeBuilder("merge-transcripts")
        .description("合併所有片段的轉錄結果")
        .uses_module("transcript-merger")
        .inputs("segment_transcripts")
        .outputs("full_transcript", "timestamped_segments")
        .next_nodes("generate-summary")
        .build()
    )

    # Node 4: Generate summary (optional)
    summary_node = (
        NodeBuilder("generate-summary")
        .description("使用 LLM 生成會議摘要")
        .uses_prompt("meeting-summarizer")
        .inputs("full_transcript", "duration_minutes", "language")
        .outputs("meeting_summary")
        .build()
    )

    # Build the workflow
    main_workflow = (
        WorkflowBuilder("meeting-transcription")
        .description(
            "完整的會議錄音轉錄流程：音訊分段 → 語音轉文字 → 合併結果 → 生成摘要"
        )
        .add_node(segment_node)
        .add_node(transcribe_node)
        .add_node(merge_node)
        .add_node(summary_node)
        .entry_node("segment-audio")
        .build()
    )

    # ==========================================================================
    # Build the complete Agent
    # ==========================================================================
    agent = (
        AgentBuilder("meeting-transcriber")
        .description(
            "將會議錄音（約一小時）轉換為帶時間戳記的文字記錄，並自動生成會議摘要。"
            "支援中文、英文等多種語言的自動偵測。"
        )
        .version("1.0.0")
        .task_goal("將輸入的會議音訊檔案轉換為結構化的文字轉錄稿和會議摘要")
        .completion_criteria(completion_criteria)
        .add_eip_dependency(openai_whisper_dep)
        .add_eip_dependency(openai_gpt_dep)
        .add_module(audio_segmenter)
        .add_module(transcript_merger)
        .add_tool(speech_to_text)
        .add_prompt(meeting_summarizer)
        .add_workflow(main_workflow)
        .build()
    )

    return agent


def main():
    """Main execution."""
    print("=" * 70)
    print("Meeting Transcriber Agent - Speech-to-Text MVP")
    print("=" * 70)

    # Create the agent
    agent = create_meeting_transcriber_agent()
    print(f"\nCreated agent: {agent.name} v{agent.version}")
    print(f"  Description: {agent.description}")
    print(f"  Task Goal: {agent.task_goal}")
    print(f"  Workflows: {len(agent.workflows)}")
    print(f"  Modules: {len(agent.modules)}")
    print(f"  Tools: {len(agent.tools)}")
    print(f"  Prompts: {len(agent.prompts)}")
    print(f"  EIP Dependencies: {len(agent.eip_dependencies)}")

    # Validate the agent
    print("\nValidating agent definition...")
    result = validate(agent)
    if result.is_valid:
        print("[OK] Validation successful!")
    else:
        print("[FAIL] Validation failed:")
        for error in result.errors:
            print(f"  - {error.code}: {error.message}")
        return 1

    # Export to YAML
    print("\nExporting to YAML...")
    yaml_output = export_yaml(agent)

    # Save to file
    output_file = "meeting_transcriber_agent.yaml"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(yaml_output)

    print(f"[OK] Exported to {output_file}")

    # Display YAML
    print("\n" + "=" * 70)
    print("Generated YAML (for Platform Core Review):")
    print("=" * 70)
    print(yaml_output)

    print("\n" + "=" * 70)
    print("MVP Example completed successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Submit this definition to Platform Core for review")
    print("2. Platform Core will validate against Review Gates 1-5")
    print("3. Upon approval, the Agent will be published to Marketplace")
    print("\n⚠️  REMINDER: This is a DESCRIPTION only.")
    print("   Execution is handled exclusively by Platform Core.")

    return 0


if __name__ == "__main__":
    exit(main())
