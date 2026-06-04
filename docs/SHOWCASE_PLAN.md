# Showcase Plan

This document records the repository packaging direction for METIS. It is meant to keep the GitHub repository, future project page, demo video, and model hub pages visually and narratively consistent.

## Reference Patterns

The current direction borrows structural patterns from strong model repositories rather than copying their visual identity:

| Reference Pattern | What To Borrow | METIS Adaptation |
|---|---|---|
| Qwen / DeepSeek style landing block | Centered wordmark, concise tagline, dense link row, clean performance sections | Use a professional METIS wordmark and a compact link matrix for paper, demo, model hubs, and docs. |
| PKU-YuanGroup / Helios style release page | Clear launch links, demo video section, model download matrix, news log | Add planned project page, demo video, Hugging Face, ModelScope, and release-roadmap slots before public launch. |
| MiniMind-V style community packaging | Strong visual identity, demo entry, collection links, accessible onboarding | Keep README friendly and skimmable while preserving the serious biomedical tone. |

## Visual System

| Element | Direction |
|---|---|
| Palette | Clinical navy, signal teal, soft cyan, restrained warm accent. |
| Logo | Waveform icon plus METIS wordmark, designed to work on white backgrounds. |
| Hero visual | Lightweight mechanism diagram: signal + prompt -> METIS -> generated clinical answer. |
| Figures | Manuscript figures stay white-background PNGs in README, with PDF versions in `assets/pdf`. |
| Tone | Foundation-model release page, not a generic paper repository. |

## Project Page

Planned sections:

1. Hero: METIS wordmark, one-line claim, and main action buttons.
2. Interactive Signal-QA demo clip or video.
3. Four capability cards: zero-shot, Signal-QA, few-shot, cross-dataset transfer.
4. Architecture story with Figure 1 and simplified diagrams.
5. Benchmark highlights with Figure 2 / Figure 3 / Figure 5.
6. Dataset scale and evaluation coverage.
7. Citation, license, and release status.

## Demo Video

Recommended video structure:

1. 5 seconds: problem framing, "brain signal analysis is fragmented".
2. 10 seconds: show signal + natural-language prompt.
3. 15 seconds: METIS answer generation and Signal-QA examples.
4. 15 seconds: zero-shot and generalist-model comparison.
5. 10 seconds: dataset scale and release information.
6. 5 seconds: GitHub / Hugging Face / paper links.

Visual teaser asset: [`assets/demo_teaser.svg`](../assets/demo_teaser.svg).

## Hugging Face And Model Hubs

When weights are ready, create:

- a Hugging Face collection for METIS
- one model card for the main checkpoint
- one dataset / preprocessing card if redistribution rules allow it
- a demo Space if inference can be simplified safely
- a matching ModelScope collection for China-based access

Keep the same wordmark, hero visual, summary claim, and citation block across all pages.

Draft model-card structure: [HF_MODEL_CARD_TEMPLATE.md](HF_MODEL_CARD_TEMPLATE.md).

## Next Visual Improvements

- Add a short animated GIF once the Signal-QA demo is available.
- Replace planned badges with real links after paper and model release.
- Add a repository social preview image using `assets/social_preview.png`.
- Consider a separate static project page under GitHub Pages after the paper link is available.
