
# Inclusive Reading Assistant
## AI Testing and Evaluation

### 1. Objective
Evaluate the text simplification functionality of the Inclusive Reading Assistant.

### 2. Evaluation Dataset
A temporary dataset containing 5 manually prepared examples was used for the initial smoke test.

These examples are not part of the official WikiLarge benchmark.

### 3. Evaluation Metrics

- API Success Rate: Measures successful API requests.
- Average Response Time: Measures API response latency.
- SARI: Measures text simplification quality.
- Flesch Reading Ease: Estimates English text readability.
- BERTScore: Planned semantic similarity evaluation, currently unavailable due to a Windows memory limitation.
- LLM-as-a-Judge: Deferred to a later evaluation stage.

### 4. Preliminary Results

| Metric | Result |
|---|---:|
| Total Samples | 5 |
| Successful Requests | 5 |
| Failed Requests | 0 |
| API Success Rate | 100% |
| Average Response Time | 3.251 seconds |
| SARI | 45.15 |
| Flesch Reading Ease | 54.12 |
| BERTScore | Not Available |

### 5. Limitations

- The initial dataset contains only 5 manually prepared examples.
- The results are preliminary and cannot establish overall system quality.
- Readability scores are based on English text.
- BERTScore could not be calculated due to insufficient virtual memory.
- LLM-as-a-Judge has been postponed.

### 6. Future Work

- Integrate the official WikiLarge test dataset.
- Increase the evaluation sample size.
- Reattempt BERTScore with a smaller model if resources allow.
- Integrate LLM-as-a-Judge using Ollama.
- Evaluate additional API endpoints such as Summarize and Explain.
