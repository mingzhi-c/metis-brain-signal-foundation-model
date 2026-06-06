# Benchmarks

This page summarizes the public benchmark interface without exposing dataset
names, private paths, subject metadata, or restricted evaluation manifests.
Exact tables should be released only through approved publication artifacts.

## Evaluation Modes

| Mode | Description | Why It Matters |
|---|---|---|
| Zero-shot classification | The pretrained model receives a signal and natural-language query without target-task fine-tuning. | Tests whether language-signal alignment can replace task-specific retraining. |
| Signal-QA | The model answers multiple-choice or open-ended questions grounded in brain signals. | Makes brain-signal analysis closer to a general assistant interface. |
| Few-shot classification | Frozen representations are evaluated with a small number of labeled examples. | Measures data efficiency in low-label clinical settings. |
| Transfer evaluation | Models train on a source setting and evaluate on a distinct target setting. | Tests robustness to acquisition and cohort shifts. |

## Key Manuscript Claims

The public repository does not include dataset-specific benchmark tables. Please
refer to the paper for audited results, statistical tests, and task definitions.
This repository keeps only the safe evaluation pattern used by METIS:

1. Build a sanitized manifest.
2. Load a preprocessed signal segment.
3. Tokenize the natural-language prompt.
4. Score candidate answer tokens.
5. Report aggregate metrics without sample identifiers.

## Visual Summary

The public visual assets intentionally avoid dataset-specific benchmark panels.

## Open Items Before Release

- Add approved aggregate result tables under `results/`.
- Add prompt templates after privacy and license review.
- Add statistical test details and random seed handling.
