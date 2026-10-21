# Results

## Local — Ground shader fixture

| Model | Solo seconds | Trio seconds | Checks |
|---|---:|---:|---:|
| qwen3-coder:30b | 31.28 | 76.88 | 7/7 |
| gemma4:12b | 56.92 | 92.39 | 6/7 |
| qwen3:8b | 39.01 | 101.59 | 7/7 |

Pair: 75.83 s versus 88.20 s sequential. Trio: 101.59 s versus 127.21 s sequential.
Peak observed model GPU allocation: 33.98 GB.
Gemma repeatedly returned Scale type "linear" instead of the declared "float".

## Cloud — synthetic shader fixture

| Alias | Seconds | Checks |
|---|---:|---:|
| copilot | 2.0 | 7/7 |
| kimik3 | 4.19 | 7/7 |
| gflash | 7.9 | 7/7 |
| bonsai | 9.12 | 7/7 |
| g35 | 10.03 | 7/7 |

All completed the required read/submit tool sequence. Gemini Flash needed one retry after 503.
These cloud calls are smaller than the local fixture; timing is not directly comparable.

## Working recommendation

Use Qwen3-Coder 30B for bounded local extraction, Qwen3 8B as a smaller candidate,
and the passing cloud endpoints for synthetic/public or separately authorized work.
Do not promote Gemma based on these results. One local worker plus cloud parallelism
is the initial interactive default; the local trio is viable for batch throughput.
This small single-trial benchmark does not certify general code-editing ability.
No permanent Ollama settings changed. All benchmark models unloaded afterward.
