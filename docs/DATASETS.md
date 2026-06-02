# Datasets

METIS is pretrained on a large heterogeneous EEG/iEEG instruction corpus and evaluated across diverse clinical signal tasks. Dataset redistribution may be restricted by the original providers; this page is meant to document provenance and preprocessing rather than mirror protected data.

## Pretraining Corpus

| Dataset | Type | Subjects | Segments | Duration (hours) |
|---|---:|---:|---:|---:|
| HUP | iEEG | 57 | 3,322,242 | 2,768.54 |
| UPenn | iEEG | 12 | 1,691,209 | 469.78 |
| SWEC_ETHZ | iEEG | 16 | 1,004,999 | 837.50 |
| FNUSA | iEEG | 12 | 147,030 | 122.53 |
| SHHS | EEG | 6,441 | 5,789,088 | 48,242.40 |
| SeiZelT2 | EEG | 125 | 4,519,290 | 12,553.58 |
| TUSZ | EEG | 675 | 687,375 | 1,909.38 |
| TUAB | EEG | 2,329 | 409,455 | 1,137.38 |
| CHB MIT | EEG | 23 | 384,834 | 1,068.98 |
| TUEP | EEG | 179 | 214,376 | 595.49 |
| SleepEDF | EEG | 78 | 195,478 | 1,628.98 |
| HaaglandenSleep | EEG | 151 | 137,244 | 1,143.70 |
| TDBrain | EEG | 911 | 115,668 | 64.26 |
| TUEV | EEG | 370 | 111,547 | 154.93 |
| ADFTD | EEG | 88 | 34,876 | 19.38 |
| BrainLat | EEG | 135 | 30,699 | 17.06 |
| AD-Auditory | EEG | 35 | 17,757 | 9.87 |
| ShuMI | EEG | 25 | 11,988 | 13.32 |
| REEG-PD | EEG | 149 | 11,878 | 6.60 |
| PhysionetMI | EEG | 109 | 9,527 | 7.94 |

## Downstream Evaluation

| Dataset | Task Family | Signal Type | Evaluation Role |
|---|---|---|---|
| ISRUC | Sleep stage classification | EEG | Zero-shot, few-shot, transfer |
| Dreams | Sleep stage classification | EEG | Zero-shot, few-shot, transfer |
| SEE | Epilepsy detection | EEG | Zero-shot, transfer |
| Siena | Seizure-state detection | EEG | Few-shot, transfer |
| Mayo | Interictal epileptiform discharge detection | iEEG | Zero-shot, few-shot, transfer |
| IEDS | Interictal epileptiform discharge detection | iEEG | Zero-shot, few-shot, transfer |
| ADFSU | Alzheimer's disease detection | EEG | Signal-QA, few-shot, transfer |
| APAVA | Parkinson's disease detection | EEG | Few-shot, transfer |
| ADHD-80 | ADHD detection | EEG | Zero-shot, few-shot, transfer |
| ADHD-121 | ADHD detection | EEG | Zero-shot, few-shot, transfer |
| Schizo-28 | Schizophrenia detection | EEG | Few-shot, transfer |
| Schizo-Youth | Schizophrenia detection | EEG | Zero-shot, few-shot, transfer |
| MDD | Major depressive disorder detection | EEG | Signal-QA, few-shot |
| SanDiego | Neurological / clinical signal classification | EEG | Few-shot |
| RatEpilepsy | Cross-species seizure detection | EEG | Zero-shot, few-shot |
| NTUHBIS | Anesthesia depth monitoring | EEG | Few-shot |
| NMT | Signal anomaly detection | EEG | Zero-shot, Signal-QA |

## Documentation To Add Before Public Release

- original dataset links and citations
- license / access restrictions
- preprocessing scripts and channel selection
- sampling-rate normalization
- segment duration
- train/validation/test split policy
- subject-wise split guarantees
