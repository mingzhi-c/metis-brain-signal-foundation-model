# Model Zoo

The pretrained METIS checkpoint is hosted on Hugging Face.

| Model | Modality | Architecture | Intended Use | Download |
|---|---|---|---|---|
| METIS | EEG + iEEG | 12 layers, hidden size 512, MoE | Signal-QA, zero-shot classification, representation learning, and downstream fine-tuning | [Hugging Face](https://huggingface.co/cccmmmzzz/metis-brain-signal-foundation-model) |

Place the downloaded checkpoint at:

```text
checkpoints/metis.pt
```

See the [Quick Start](README.md#quick-start) for inference and fine-tuning examples. The model hub lists the checkpoint license and current model metadata.
