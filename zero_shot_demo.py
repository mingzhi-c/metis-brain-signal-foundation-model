import numpy as np
import torch
from transformers import AutoTokenizer

from METIS import Metis, MetisConfig


DATA_PATH = "./demo_data/isruc_demo.npz"
MODEL_PATH = "./checkpoints/metis.pt"
TOKENIZER_NAME = "Qwen/Qwen2.5-0.5B"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
SAMPLE_INDEX = 0
MAX_NEW_TOKENS = 16
BATCH_SIZE = 64

QUESTION = "Which sleep stage does this signal belong to?"
LABELS = ["Wake", "Non-REM Stage 1", "Non-REM Stage 2", "Non-REM Stage 3", "Rapid Eye Movement"]
LETTERS = ["A", "B", "C", "D", "E"]


def build_mcq_question():
    options = " ".join([f"({LETTERS[i]}){LABELS[i]}" for i in range(len(LABELS))])
    return QUESTION + " Options: " + options


def prepare_input(question, tokenizer):
    text = f"<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant\n"
    return tokenizer(text, return_tensors="pt", add_special_tokens=True).input_ids


def load_model():
    model = Metis(MetisConfig())
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.to(DEVICE)
    model.eval()
    return model


def predict_mcq_batch(model, tokenizer, signal):
    question = build_mcq_question()

    input_ids = prepare_input(question, tokenizer).to(DEVICE)
    input_ids = input_ids.repeat(signal.size(0), 1)

    option_ids = torch.tensor(
        [tokenizer.convert_tokens_to_ids(x) for x in LETTERS],
        device=DEVICE
    )

    signal = signal.to(DEVICE)

    with torch.no_grad():
        logits = model(signal, input_ids)
        last_logits = logits[:, -1, :]
        option_logits = last_logits[:, option_ids]
        preds = option_logits.argmax(dim=-1)

    return preds


def run_mcq_demo(model, tokenizer, x, y, index):
    pred = predict_mcq_batch(model, tokenizer, x[index:index + 1]).item()
    label = int(y[index])

    print("\n[Multiple-choice QA]")
    print("Question:", build_mcq_question())
    print("Prediction:", LETTERS[pred], LABELS[pred])
    print("Answer:", LETTERS[label], LABELS[label])


def run_generation_demo(model, tokenizer, x, y, index):
    input_ids = prepare_input(QUESTION, tokenizer).to(DEVICE)
    signal = x[index:index + 1].to(DEVICE)

    with torch.no_grad():
        for _ in range(MAX_NEW_TOKENS):
            logits = model(signal, input_ids)
            next_id = logits[:, -1, :].argmax(dim=-1, keepdim=True)
            input_ids = torch.cat([input_ids, next_id], dim=1)

            if next_id.item() == tokenizer.eos_token_id:
                break

    answer = tokenizer.decode(input_ids[0], skip_special_tokens=True).split("assistant")[-1].strip()

    print("\n[Detailed QA]")
    print("Question:", QUESTION)
    print("Prediction:", answer)
    print("Answer:", LABELS[int(y[index])])


def run_accuracy_demo(model, tokenizer, x, y):
    all_preds = []

    for i in range(0, len(y), BATCH_SIZE):
        batch_x = x[i:i + BATCH_SIZE]
        preds = predict_mcq_batch(model, tokenizer, batch_x)
        all_preds.append(preds.cpu())

    all_preds = torch.cat(all_preds)
    correct = (all_preds == y).sum().item()
    total = len(y)

    print("\n[Multiple-choice Accuracy]")
    print(f"Accuracy: {correct}/{total} = {100 * correct / total:.2f}%")


if __name__ == "__main__":
    data = np.load(DATA_PATH)
    x = torch.tensor(data["x"], dtype=torch.float32)
    y = torch.tensor(data["y"], dtype=torch.long)

    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)
    model = load_model()

    run_mcq_demo(model, tokenizer, x, y, SAMPLE_INDEX)
    run_generation_demo(model, tokenizer, x, y, SAMPLE_INDEX)
    run_accuracy_demo(model, tokenizer, x, y)
