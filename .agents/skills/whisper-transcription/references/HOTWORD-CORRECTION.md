# Hotword Correction Reference

Post-processing guide for correcting ASR (Automatic Speech Recognition) transcription errors.

## Overview

Whisper and other ASR systems frequently misrecognize:
- **Technical terms**: API names, programming concepts, domain jargon
- **Proper nouns**: Person names, company names, brand names, product names
- **Abbreviations**: SDK, API, GPU, LLM, etc.
- **Foreign words**: Loanwords, transliterations, code-switching content
- **Homophones**: Words that sound similar but have different meanings

This reference provides guidelines for context-aware correction.

## Correction Principles

1. **Conservative approach**: Only correct when context strongly suggests an error
2. **Preserve intent**: Maintain original meaning, tone, and sentence structure
3. **Prioritize high-value terms**: Focus on terminology that affects comprehension
4. **When uncertain, preserve**: Do not guess; keep original if unsure

## System Prompt for Hotword Correction

Use this prompt when invoking an LLM for hotword correction:

```
You are a "Hotword Correction" specialist. You will receive text transcribed by Whisper that may contain misrecognized words due to noise, audio artifacts, or word segmentation issues—especially for technical terms, proper nouns, abbreviations, brand/product names, and domain-specific vocabulary.

Your task is to correct these errors based on contextual semantics.

Goal: Only correct words that are highly suspicious AND contextually relevant to the overall topic. Preserve the original meaning, tone, and structure. Do not make unsupported rewrites.

Requirements:
1. Only correct when context strongly indicates an error; if uncertain, keep the original word.
2. Prioritize correcting: technical terms, proper nouns, abbreviations, foreign words, brand/product names.
3. Preserve original sentence structure and paragraph formatting; minimize changes.
4. not explain your reasoning.
```

## Common Correction Patterns

### Technical Terms

| Misrecognition | Likely Correction | Context Clue |
|----------------|-------------------|--------------|
| "pie torch" | "PyTorch" | ML/AI discussion |
| "tensor flow" | "TensorFlow" | ML framework context |
| "get hub" | "GitHub" | Version control context |
| "docker" vs "doctor" | Context-dependent | Container vs medical |

### Chinese-English Mixed Content

| Misrecognition | Likely Correction | Context Clue |
|----------------|-------------------|--------------|
| "A P I" (split) | "API" | Technical discussion |
| "机器学习" vs "机器雪莲" | "机器学习" | ML context |
| "大模型" vs "大魔型" | "大模型" | LLM discussion |

### Brand and Product Names

| Misrecognition | Likely Correction | Context Clue |
|----------------|-------------------|--------------|
| "open AI" | "OpenAI" | AI company context |
| "chat GPT" | "ChatGPT" | Conversational AI |
| "whisper" vs "whisker" | Context-dependent | ASR vs other |

## Workflow Integration

### Recommended Pipeline

```
Audio/Video → Whisper Transcription → Hotword Correction → Final Output
                    ↓                        ↓
              Raw transcript          Corrected transcript
```

### Implementation Pattern

```python
def transcribe_with_correction(audio_path: str, llm_client) -> str:
    """Transcribe audio and apply hotword correction."""
    import whisper
    
    # Step 1: Raw transcription
    model = whisper.load_model("large-v3", device="cuda")
    result = model.transcribe(audio_path, language="zh")
    raw_text = result["text"]
    
    # Step 2: Hotword correction via LLM
    corrected_text = llm_client.correct_hotwords(raw_text)
    
    return corrected_text
```

## Quality Indicators

Signs that correction is needed:
- Inconsistent spelling of the same term within document
- Technical terms that don't exist (likely misheard)
- Proper nouns that don't match known entities in context
- Abbreviations split into separate letters

Signs to preserve original:
- Ambiguous context with multiple valid interpretations
- Uncommon but valid terminology
- Intentional non-standard usage (quotes, examples)

## Edge Cases

### Preserve Original When:
- The speaker intentionally uses non-standard pronunciation
- Direct quotes or citations
- Code snippets or command examples
- Uncertainty about domain-specific terminology

### Always Correct When:
- Same term appears correctly elsewhere in transcript
- Obvious phonetic substitution (homophones)
- Split words that should be compound terms
