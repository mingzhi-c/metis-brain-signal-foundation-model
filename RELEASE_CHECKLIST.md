# Public Release Checklist

Use this checklist before switching the repository from private to public.

## Content

- [ ] Replace placeholder paper links with arXiv, DOI, or journal page.
- [ ] Confirm the final project title and author order.
- [ ] Confirm whether the README can display all manuscript figures.
- [ ] Add model checkpoints or mark the model release date clearly.
- [ ] Add minimal inference examples after code cleanup.
- [ ] Add benchmark result tables under a stable path such as `results/`.

## Legal and Access

- [ ] Choose the final code license.
- [ ] Choose the final model-weight license.
- [ ] Confirm whether figures can be redistributed in the repository.
- [ ] Check dataset licenses and avoid redistributing restricted data.
- [ ] Remove any private paths, credentials, or local machine metadata.

## Reproducibility

- [ ] Pin environment dependencies.
- [ ] Add smoke-test commands for inference.
- [ ] Add seed and split documentation.
- [ ] Add preprocessing notes for every public dataset.
- [ ] Add expected outputs for at least one tiny example.

## GitHub Polish

- [ ] Set `assets/social_preview.png` as the repository social preview image.
- [ ] Add repository topics such as `eeg`, `ieeg`, `brain-signals`, `foundation-model`, `signal-qa`, `multimodal-learning`.
- [ ] Enable issue templates only after public release.
- [ ] Add release notes when the first checkpoint is published.
