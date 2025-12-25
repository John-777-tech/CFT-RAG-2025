# 运行Baseline RAG Benchmark指南

## 当前评估结果（仅BLEU）

由于缺少ROUGE和BERTScore依赖，当前只能计算BLEU指标：

- **总样本数**: 1714
- **BLEU**: 0.0100 (1.00%)

结果文件：`benchmark/results/aeslc_baseline_evaluation.json`

## 完整评估步骤

### 1. 安装依赖

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# 安装评估指标依赖
pip install rouge-score nltk bert-score

# 如果使用conda环境
conda install -c conda-forge rouge-score nltk
pip install bert-score
```

### 2. 运行Baseline Benchmark

```bash
# 方法1: 使用脚本（推荐）
bash run_baseline_benchmark.sh

# 方法2: 手动运行
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 0 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output ./benchmark/results/aeslc_baseline_results.json \
    --checkpoint ./benchmark/results/aeslc_baseline_results.json \
    --max-samples 36
```

### 3. 运行完整评估（ROUGE + BLEU + BERTScore）

```bash
# 完整评估（包含BERTScore，首次运行需要下载模型，较慢）
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/aeslc_baseline_results.json \
    --output ./benchmark/results/aeslc_baseline_evaluation.json

# 如果BERTScore下载失败，可以跳过BERTScore
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/aeslc_baseline_results.json \
    --output ./benchmark/results/aeslc_baseline_evaluation.json \
    --skip-bertscore
```

### 4. 查看评估结果

```bash
python -c "
import json
with open('./benchmark/results/aeslc_baseline_evaluation.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'总样本数: {data[\"total_samples\"]}')
print(f'\n平均分数:')
for key, value in data['average_scores'].items():
    print(f'  {key.upper()}: {value:.4f}')
"
```

## 评估指标说明

- **ROUGE-1, ROUGE-2, ROUGE-L**: 基于n-gram重叠的摘要评估指标
- **BLEU**: 基于n-gram精确匹配的翻译/摘要评估指标  
- **BERTScore**: 基于BERT语义相似度的评估指标

## 注意事项

1. **BERTScore首次运行**：需要下载roberta-large模型（约1.3GB），可能需要10-20分钟
2. **网络问题**：如果下载慢，可以设置镜像：
   ```bash
   export HF_ENDPOINT=https://hf-mirror.com
   ```
3. **现有结果**：如果已有benchmark结果文件，可以直接运行评估步骤，无需重新运行benchmark

## 当前状态

- ✅ BLEU评估：已完成（0.0100）
- ❌ ROUGE评估：需要安装 `rouge-score`
- ❌ BERTScore评估：需要安装 `bert-score`


