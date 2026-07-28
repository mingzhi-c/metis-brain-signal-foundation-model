"""METIS zero-shot Signal-QA evaluation pseudocode."""

import argparse

import torch
import torch.nn.functional as F

from METIS import Metis, MetisConfig


class ZeroShotSignalQADataset(torch.utils.data.Dataset):
    """Pseudocode dataset interface for zero-shot Signal-QA evaluation.

    Expected output per sample:
      signal: Tensor shaped [channels, time]
      prompt_ids: tokenized question prefix
      option_token_ids: token ids for candidate answers such as A/B/C/D
      label: integer index of the correct option
    """

    def __init__(self, manifest_path, tokenizer_name):
        self.manifest_path = manifest_path
        self.tokenizer_name = tokenizer_name
        self.samples = self._load_manifest(manifest_path)

    def _load_manifest(self, manifest_path):
        # Read a sanitized manifest with signal_uri, question, options, and label.
        raise NotImplementedError("Implement evaluation manifest loading.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        # 1. Load and preprocess one signal segment.
        # 2. Build the natural-language question.
        # 3. Tokenize the question prefix.
        # 4. Map each candidate answer to its first answer token.
        raise NotImplementedError("Return signal, prompt_ids, option_token_ids, label.")


def compute_zero_shot_scores(model, signal, prompt_ids, option_token_ids):
    """Score candidate answers with next-token logits."""

    logits = model(signal, prompt_ids)
    next_token_logits = logits[:, -1, :]
    option_logits = next_token_logits.gather(dim=1, index=option_token_ids)
    return option_logits


def evaluate(args):
    device = torch.device(args.device)
    config = MetisConfig()
    model = Metis(config).to(device)

    checkpoint = torch.load(args.checkpoint, map_location="cpu")
    model.load_state_dict(checkpoint)
    model.eval()

    dataset = ZeroShotSignalQADataset(
        manifest_path=args.manifest,
        tokenizer_name=args.tokenizer,
    )
    loader = torch.utils.data.DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
    )

    all_probs = []
    all_labels = []

    with torch.no_grad():
        for signal, prompt_ids, option_token_ids, labels in loader:
            signal = signal.to(device)
            prompt_ids = prompt_ids.to(device)
            option_token_ids = option_token_ids.to(device)
            labels = labels.to(device)

            option_logits = compute_zero_shot_scores(
                model=model,
                signal=signal,
                prompt_ids=prompt_ids,
                option_token_ids=option_token_ids,
            )
            all_probs.append(F.softmax(option_logits, dim=-1).cpu())
            all_labels.append(labels.cpu())

    all_probs = torch.cat(all_probs, dim=0)
    all_labels = torch.cat(all_labels, dim=0)

    # Common metrics include accuracy, macro AUROC, and task-specific scores.
    predictions = all_probs.argmax(dim=-1)
    accuracy = (predictions == all_labels).float().mean().item()
    print({"zero_shot_accuracy": accuracy})


def parse_args():
    parser = argparse.ArgumentParser(description="METIS zero-shot evaluation pseudocode")
    parser.add_argument("--manifest", type=str, default="path/to/sanitized_eval_manifest.jsonl")
    parser.add_argument("--tokenizer", type=str, default="path/to/tokenizer")
    parser.add_argument("--checkpoint", type=str, default="checkpoints/metis.pt")
    parser.add_argument("--batch_size", type=int, default=128)
    parser.add_argument("--num_workers", type=int, default=4)
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    return parser.parse_args()


if __name__ == "__main__":
    evaluate(parse_args())
