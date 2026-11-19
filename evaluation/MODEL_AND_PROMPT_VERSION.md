

\# Model and Prompt Versioning



\## Project

Inclusive Reading Assistant



\## Evaluation Date

2026-11-19



\## Model Configuration

\- Provider: Google Gemini

\- Generation Model: gemini-3.8-flash

\- Embedding Model: See embedding\_client.py

\- Dataset: WikiLarge (Hugging Face)

\- Evaluation Samples: 200

\- Random Seed: 42



\## Prompt Version

\- Version: v1.0

\- Purpose: Accessible content simplification

\- Grounding: Enabled in RAG pipeline



\## Baseline Evaluation Results



| Metric | Baseline |

|---|---:|

| API Success Rate | 100% |

| SARI | 37.2702 |

| BLEU | 29.6552 |

| ROUGE-L | 0.6257 |

| Flesch Reading Ease | 66.5298 |

| Average Response Time | 4.7165s |

| Median Response Time | 3.5095s |

| P95 Response Time | 9.2804s |



\## Future Evaluation



Every new model or prompt version must be

compared against this baseline.



Track:

\- Quality improvements

\- Semantic similarity

\- Meaning preservation

\- Groundedness

\- Readability

\- Operational performance



\## Version History



| Version | Model | Description |

|---|---|---|

| v1.0 | Gemini | Initial baseline |

parison.

