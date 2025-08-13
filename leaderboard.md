## **MoNaCo Leaderboard**

Below are the closed-book setting results of models on the full MoNaCo benchmark i.e., over all 1,315 questions. To reproduce our evaluation, please refer to our LLM-as-judge prompt and evaluation script [available here](https://github.com/tomerwolgithub/monaco/tree/main/prompts). Note that we originally used GPT-4.1 as our "judge" language model.

Rank | Model | Date | Link | F1 | Precision | Recall 
------------ | ------------- | ------------- | ------------- | ------------- | ------------- | -------------
1 | o3 | 2025-05 | [🌐](https://openai.com/index/introducing-o3-and-o4-mini/) | **<u>61.18</u>** | **<u>68.10</u>**  | **<u>59.54</u>** 
2 | GPT-5 (medium reasoning) | 2025-08 | [🌐](https://openai.com/index/introducing-gpt-5/) | 60.11 | 66.38 | 58.98
3 | Gemini 2.5-Pro | 2025-07 | [🌐](https://deepmind.google/models/gemini/pro/) | 59.11 | 65.02 | 58.14
4 | GPT-4o (few-shot) | 2025-03 | [🌐](https://openai.com/index/hello-gpt-4o/) | 55.05 | 63.33  | 52.88
5 | Deepseek-V3 (few-shot) | 2025-05 | [🌐](https://huggingface.co/deepseek-ai/DeepSeek-V3) | 55.04 | 62.31 | 53.37
6 | Claude 4-Opus | 2025-07 | [🌐](https://www.anthropic.com/news/claude-4) | 55.03 | 62.28 | 53.47
7 | o4-mini | 2025-04 | [🌐](https://openai.com/index/introducing-o3-and-o4-mini/) |  54.92 | 62.50 | 53.01
8 | Deepseek-R1 | 2025-04 | [🌐](https://huggingface.co/deepseek-ai/DeepSeek-R1) | 53.82 | 62.52 | 51.50
9 | Gemini 2.5-Flash | 2025-07 | [🌐](https://deepmind.google/models/gemini/flash/) | 52.01 | 58.10 | 50.60
10 | Llama 3.1-405B (few-shot) | 2025-03 | [🌐](https://huggingface.co/meta-llama/Llama-3.1-405B-Instruct) | 51.39 | 55.97 | 51.20
11 | o3-mini | 2025-04 | [🌐](https://openai.com/index/openai-o3-mini/) | 48.75 | 59.29 | 46.19
12 | GPT-4 Turbo (few-shot) | 2024-05 | [🌐](https://platform.openai.com/docs/models/gpt-4-turbo) | 48.58 | 56.26 | 46.81
13 | Qwen 2.5-72B (few-shot) | 2025-05 | [🌐](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) | 47.05 | 53.84 | 45.48
14 | Llama 3-70B (few-shot) | 2024-05 | [🌐](https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct) | 47.00 | 55.15 |  45.12
15 | Qwen 2-72B (few-shot) | 2024-07 | [🌐](https://huggingface.co/Qwen/Qwen2-7B-Instruct) | 43.92 | 50.80 | 42.89



