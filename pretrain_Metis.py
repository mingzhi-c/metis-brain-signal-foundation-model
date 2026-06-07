"""METIS signal-instruction pretraining pseudocode."""

import argparse

import torch
import torch.nn.functional as F

from METIS import Metis, MetisConfig


class SignalInstructionDataset(torch.utils.data.Dataset):
    """Pseudocode dataset interface for signal-instruction pretraining.

    Expected output per sample:
      signal: Tensor shaped [channels, time]
      input_ids: tokenized prompt and answer input ids
      labels: token labels where prompt and padding positions are masked as -100
    """

    def __init__(self, manifest_path, tokenizer_name, max_text_length):
        self.manifest_path = manifest_path
        self.tokenizer_name = tokenizer_name
        self.max_text_length = max_text_length
        self.samples = self._load_manifest(manifest_path)

    def _load_manifest(self, manifest_path):
        # Read a sanitized manifest with signal_uri, task_type, question, and answer.
        raise NotImplementedError("Implement manifest loading.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        # 1. Load one signal segment from the manifest.
        # 2. Apply preprocessing: resampling, normalization, channel mapping.
        # 3. Build a natural-language instruction and canonical target answer.
        # 4. Tokenize prompt + answer and mask prompt tokens in labels.
        raise NotImplementedError("Return signal, input_ids, labels.")


def train(args):
    device = torch.device(args.device)
    config = MetisConfig()
    model = Metis(config).to(device)

    dataset = SignalInstructionDataset(
        manifest_path=args.manifest,
        tokenizer_name=args.tokenizer,
        max_text_length=args.max_text_length,
    )
    loader = torch.utils.data.DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        drop_last=True,
    )

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=args.learning_rate,
        weight_decay=args.weight_decay,
    )
    scaler = torch.cuda.amp.GradScaler(enabled=args.mixed_precision)

    model.train()
    optimizer.zero_grad(set_to_none=True)

    for epoch in range(args.epochs):
        for step, batch in enumerate(loader):
            signal, input_ids, labels = batch
            signal = signal.to(device)
            input_ids = input_ids.to(device)
            labels = labels.to(device)

            # Teacher forcing: the model receives all but the last text token
            # and predicts the next token for answer positions only.
            decoder_input_ids = input_ids[:, :-1]
            target_labels = labels[:, 1:]

            with torch.cuda.amp.autocast(enabled=args.mixed_precision):
                logits, aux_loss = model(
                    signal,
                    decoder_input_ids,
                    return_aux_loss=True,
                )
                lm_loss = F.cross_entropy(
                    logits.reshape(-1, logits.size(-1)),
                    target_labels.reshape(-1),
                    ignore_index=-100,
                )
                loss = lm_loss + args.aux_loss_weight * aux_loss

            scaler.scale(loss / args.gradient_accumulation_steps).backward()

            if (step + 1) % args.gradient_accumulation_steps == 0:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.grad_clip)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad(set_to_none=True)

        # Save checkpoints to the configured output path.
        # torch.save(model.state_dict(), args.output_checkpoint)


def parse_args():
    parser = argparse.ArgumentParser(description="METIS pretraining pseudocode")
    parser.add_argument("--manifest", type=str, default="path/to/sanitized_manifest.jsonl")
    parser.add_argument("--tokenizer", type=str, default="path/to/tokenizer")
    parser.add_argument("--output_checkpoint", type=str, default="checkpoints/metis.pt")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch_size", type=int, default=256)
    parser.add_argument("--learning_rate", type=float, default=2e-4)
    parser.add_argument("--weight_decay", type=float, default=0.1)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=20)
    parser.add_argument("--grad_clip", type=float, default=1.0)
    parser.add_argument("--aux_loss_weight", type=float, default=1.0)
    parser.add_argument("--max_text_length", type=int, default=512)
    parser.add_argument("--num_workers", type=int, default=4)
    parser.add_argument("--mixed_precision", action="store_true")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    return parser.parse_args()


if __name__ == "__main__":
    train(parse_args())
