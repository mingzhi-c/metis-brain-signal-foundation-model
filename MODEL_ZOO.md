# Model Zoo

METIS checkpoints are planned for release after publication. This table is designed to be filled without changing the README structure.

| Model | Modality | Layers | Hidden Size | MoE | Intended Use | Release Target | Status |
|---|---|---:|---:|---|---|---|---|
| METIS-Base | EEG + iEEG | 12 | 512 | 8 routed experts + 1 shared expert | Zero-shot Signal-QA, few-shot linear probing, cross-dataset transfer | Hugging Face + ModelScope | Planned |
| METIS-Encoder | EEG + iEEG | 12 | 512 | Same backbone | Feature extraction for downstream classifiers | Hugging Face + ModelScope | Planned |

## Release Notes

- Checkpoints will be released for non-commercial academic use after the article is published, subject to the final license decision.
- The first public package should include model weights, preprocessing examples, inference scripts, and evaluation recipes.
- If a model hub is used later, add Hugging Face / ModelScope links in the `Status` column and keep SHA256 checksums here.
- The matching model-card draft lives in [docs/HF_MODEL_CARD_TEMPLATE.md](docs/HF_MODEL_CARD_TEMPLATE.md).

## Suggested Card Fields

When checkpoints are ready, add:

- parameter count and active parameter count
- input channel assumptions
- accepted sampling-rate handling
- maximum signal duration
- prompt templates
- known limitations
- checksum and release date
