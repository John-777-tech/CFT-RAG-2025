# Baseline vs Cuckoo Filter Depth=1 对比报告

**生成时间**: 2025-12-28  
**配置**: 
- Baseline: search_method=0, Prompt: `Answer the question using the provided information.`
- Cuckoo Filter: search_method=7, depth=1, Prompt: `Answer the question using the provided information.` + Abstracts（相同的基础prompt）
**样本数**: 每个数据集 100 个样本

## 1. 评估分数对比

| 数据集 | 方法 | ROUGE-1 | ROUGE-2 | ROUGE-L | BLEU | BERTScore |
|--------|------|---------|---------|---------|------|-----------|
| **MedQA** | Baseline | 0.0364 | 0.0198 | 0.0346 | 0.0069 | 0.7890 |
| **MedQA** | Cuckoo D1 | 0.2826 | 0.1963 | 0.2813 | 0.1016 | 0.8588 |
| **DART** | Baseline | 0.4825 | 0.3635 | 0.4189 | 0.2319 | 0.9040 |
| **DART** | Cuckoo D1 | 0.7068 | 0.5004 | 0.5751 | 0.3457 | 0.9299 |
| **TriviaQA** | Baseline | 0.0334 | 0.0094 | 0.0334 | 0.0036 | 0.8072 |
| **TriviaQA** | Cuckoo D1 | 0.7018 | 0.2970 | 0.7018 | 0.1529 | 0.9343 |

## 2. 时间性能对比

| 数据集 | 方法 | 平均总耗时(秒) | 总耗时(分钟) | 平均检索时间(秒) | 平均生成时间(秒) |
|--------|------|---------------|-------------|----------------|----------------|
| **MedQA** | Baseline | 48.04 | 80.07 | 0.059 | 48.022 |
| **MedQA** | Cuckoo D1 | 15.30 | 25.49 | 0.000 | 15.278 |
| **DART** | Baseline | 34.92 | 58.21 | 0.084 | 34.903 |
| **DART** | Cuckoo D1 | 6.83 | 11.38 | 0.000 | 6.810 |
| **TriviaQA** | Baseline | 34.55 | 57.58 | 2.708 | 34.524 |
| **TriviaQA** | Cuckoo D1 | 9.76 | 16.26 | 0.000 | 9.736 |

## 3. 详细分析

### MedQA
- **Baseline**: ROUGE-L=0.0346, BLEU=0.0069, BERTScore=0.7890, 平均耗时=48.04秒/样本
- **Cuckoo Filter Depth=1**: ROUGE-L=0.2813, BLEU=0.1016, BERTScore=0.8588, 平均耗时=15.30秒/样本
- **改进**: ROUGE-L提升713.9%, 时间减少68.2%

### DART
- **Baseline**: ROUGE-L=0.4189, BLEU=0.2319, BERTScore=0.9040, 平均耗时=34.92秒/样本
- **Cuckoo Filter Depth=1**: ROUGE-L=0.5751, BLEU=0.3457, BERTScore=0.9299, 平均耗时=6.83秒/样本
- **改进**: ROUGE-L提升37.3%, 时间减少80.5%

### TriviaQA
- **Baseline**: ROUGE-L=0.0334, BLEU=0.0036, BERTScore=0.8072, 平均耗时=34.55秒/样本
- **Cuckoo Filter Depth=1**: ROUGE-L=0.7018, BLEU=0.1529, BERTScore=0.9343, 平均耗时=9.76秒/样本
- **改进**: ROUGE-L提升1999.8%, 时间减少71.8%

## 4. 结果文件

### Baseline
- `benchmark/results/medqa_baseline_simple_prompt_100.json`
- `benchmark/results/medqa_baseline_simple_prompt_100_evaluation.json`
- `benchmark/results/dart_baseline_simple_prompt_100.json`
- `benchmark/results/dart_baseline_simple_prompt_100_evaluation.json`
- `benchmark/results/triviaqa_baseline_simple_prompt_100.json`
- `benchmark/results/triviaqa_baseline_simple_prompt_100_evaluation.json`

### Cuckoo Filter Depth=1
- `benchmark/results/medqa_cuckoo_depth1_100.json`
- `benchmark/results/medqa_cuckoo_depth1_100_evaluation.json`
- `benchmark/results/dart_cuckoo_depth1_100.json`
- `benchmark/results/dart_cuckoo_depth1_100_evaluation.json`
- `benchmark/results/triviaqa_cuckoo_depth1_100.json`
- `benchmark/results/triviaqa_cuckoo_depth1_100_evaluation.json`