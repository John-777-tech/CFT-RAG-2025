# Baseline New Prompt 完整评估报告

**生成时间**: 2025-12-28  
**配置**: search_method=0 (Baseline RAG), depth=0, 新Prompt（与Cuckoo Filter Abstract Tree保持一致）  
**样本数**: 每个数据集 100 个样本

## 1. 评估分数汇总

| 数据集 | ROUGE-1 | ROUGE-2 | ROUGE-L | BLEU | BERTScore |
|--------|---------|---------|---------|------|-----------|
| **MedQA** | 0.3010 | 0.2069 | 0.2985 | 0.1156 | 0.8615 |
| **DART** | 0.7275 | 0.5197 | 0.5859 | 0.3569 | 0.9336 |
| **TriviaQA** | 0.6998 | 0.2971 | 0.6998 | 0.1545 | 0.9325 |

## 2. 时间性能汇总

| 数据集 | 平均总耗时(秒) | 总耗时(分钟) | 平均检索时间(秒) | 平均生成时间(秒) |
|--------|---------------|-------------|----------------|----------------|
| **MedQA** | 23.55 | 39.26 | 0.085 | 23.528 |
| **DART** | 6.15 | 10.25 | 0.137 | 6.126 |
| **TriviaQA** | 9.49 | 15.81 | 5.323 | 9.459 |

## 3. 详细分析

### MedQA
- **评估分数**: ROUGE-L=0.2985, BLEU=0.1156, BERTScore=0.8615
- **时间性能**: 平均23.55秒/样本，检索时间0.085秒（非常快），生成时间23.528秒
- **特点**: 生成时间占主导，检索效率高，BERTScore较高（0.8615）

### DART
- **评估分数**: ROUGE-L=0.5859, BLEU=0.3569（最高）, BERTScore=0.9336（最高）
- **时间性能**: 平均6.15秒/样本，检索时间0.137秒，生成时间6.126秒
- **特点**: 所有评估分数最高，时间性能最好，BERTScore接近0.93

### TriviaQA
- **评估分数**: ROUGE-L=0.6998, BLEU=0.1545, BERTScore=0.9325
- **时间性能**: 平均9.49秒/样本，检索时间5.323秒（相对较慢），生成时间9.459秒
- **特点**: ROUGE-1和ROUGE-L分数最高，BERTScore也很高（0.9325），但检索时间较长

## 4. 结果文件

- `benchmark/results/medqa_baseline_new_prompt_100.json`
- `benchmark/results/dart_baseline_new_prompt_100.json`
- `benchmark/results/triviaqa_baseline_new_prompt_100.json`
- `benchmark/results/medqa_baseline_new_prompt_100_evaluation.json`
- `benchmark/results/dart_baseline_new_prompt_100_evaluation.json`
- `benchmark/results/triviaqa_baseline_new_prompt_100_evaluation.json`

## 5. 评估指标说明

- **ROUGE**: 基于n-gram重叠的摘要评估指标，值越高表示重叠度越高
- **BLEU**: 基于n-gram精确匹配的翻译/摘要评估指标，值越高表示精确匹配度越高
- **BERTScore**: 基于BERT语义相似度的评估指标，值在0-1之间，值越高表示语义相似度越高
  - BERTScore通常比ROUGE和BLEU更能反映语义相似性，因为它基于预训练的BERT模型
  - 本报告中BERTScore使用roberta-large模型计算

## 6. 对比说明

本报告使用新Prompt（与Cuckoo Filter Abstract Tree保持一致），相比之前的baseline结果：
- Prompt更简洁，要求直接回答
- 答案长度更短（平均答案长度显著减少）
- 生成时间可能有所变化
- **BERTScore评估**: 所有数据集的BERTScore都较高（0.86-0.93），表明生成的答案在语义上与参考答案高度相似

