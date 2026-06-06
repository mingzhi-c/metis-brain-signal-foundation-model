# Data Policy

This public repository does not include private data, subject metadata, dataset
manifests, raw file paths, or redistribution-restricted preprocessing logic.

METIS training and evaluation code should be connected to data through sanitized
local manifests prepared by the user. Those manifests should contain only fields
that are allowed to be stored in a code repository.

## Public Interface

Training and evaluation examples expect sanitized manifest files with generic
fields such as:

| Field | Purpose |
|---|---|
| `signal_uri` | User-controlled pointer to a local signal segment. |
| `task_type` | Generic task category used to select an instruction template. |
| `question` | Natural-language prompt shown to the model. |
| `answer` | Canonical training answer, when available. |
| `options` | Candidate answer strings for zero-shot evaluation. |
| `label` | Index of the correct option for evaluation. |

## Do Not Commit

- raw clinical or physiological signal files
- subject identifiers or demographic metadata
- private absolute paths
- restricted dataset names when access terms do not allow redistribution
- hidden train/test split files
- institution-specific preprocessing scripts

## Recommended Workflow

1. Keep raw data outside the repository.
2. Build a sanitized manifest locally.
3. Pass the manifest path to the pseudocode scripts.
4. Log only aggregate metrics and losses.
5. Review generated outputs before sharing them publicly.
