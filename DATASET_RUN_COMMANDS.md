# 运行数据集的命令示例

## 基本命令格式

### 1. 运行 Benchmark（使用 run_benchmark.py）

```bash
python benchmark/run_benchmark.py \
    --dataset <数据集路径> \
    --vec-db-key <数据库键名> \
    --entities-file-name <实体文件名> \
    --search-method <搜索方法> \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output <输出文件路径> \
    --checkpoint <断点续传文件路径> \
    --max-samples <最大样本数>
```

### 2. 评估结果（使用 evaluate_comprehensive.py）

```bash
python benchmark/evaluate_comprehensive.py \
    --results <benchmark结果文件> \
    --output <评估结果输出文件>
```

---

## 具体数据集示例

### AESLC 数据集

#### Baseline RAG (search_method=0)
```bash
# 运行benchmark
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 0 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output ./benchmark/results/aeslc_baseline.json \
    --checkpoint ./benchmark/results/aeslc_baseline.json \
    --max-samples 30

# 评估结果
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/aeslc_baseline.json \
    --output ./benchmark/results/aeslc_baseline_evaluation.json
```

#### Abstract RAG with Depth=2 (search_method=2)
```bash
# 运行benchmark
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 2 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --max-hierarchy-depth 2 \
    --output ./benchmark/results/aeslc_depth2.json \
    --checkpoint ./benchmark/results/aeslc_depth2.json \
    --max-samples 30

# 评估结果
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/aeslc_depth2.json \
    --output ./benchmark/results/aeslc_depth2_evaluation.json
```

### MedQA 数据集

```bash
# 运行benchmark
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/medqa.json \
    --vec-db-key medqa \
    --entities-file-name medqa_entities_file \
    --search-method 2 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --max-hierarchy-depth 2 \
    --output ./benchmark/results/medqa_depth2.json \
    --checkpoint ./benchmark/results/medqa_depth2.json \
    --max-samples 100

# 评估结果
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/medqa_depth2.json \
    --output ./benchmark/results/medqa_depth2_evaluation.json
```

### DART 数据集

```bash
# 运行benchmark
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/dart.json \
    --vec-db-key dart \
    --entities-file-name dart_entities_file \
    --search-method 2 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --max-hierarchy-depth 2 \
    --output ./benchmark/results/dart_depth2.json \
    --checkpoint ./benchmark/results/dart_depth2.json \
    --max-samples 100

# 评估结果
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/dart_depth2.json \
    --output ./benchmark/results/dart_depth2_evaluation.json
```

### TriviaQA 数据集

```bash
# 运行benchmark
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/triviaqa.json \
    --vec-db-key triviaqa \
    --entities-file-name triviaqa_entities_file \
    --search-method 2 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --max-hierarchy-depth 2 \
    --output ./benchmark/results/triviaqa_depth2.json \
    --checkpoint ./benchmark/results/triviaqa_depth2.json \
    --max-samples 100

# 评估结果
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/triviaqa_depth2.json \
    --output ./benchmark/results/triviaqa_depth2_evaluation.json
```

---

## Search Method 说明

- `--search-method 0`: Baseline RAG（仅使用向量数据库）
- `--search-method 1`: BFS搜索
- `--search-method 2`: BloomFilter搜索（Abstract RAG）
- `--search-method 5`: 改进的BloomFilter搜索
- `--search-method 7`: Cuckoo Filter搜索（需要cuckoo filter支持）
- `--search-method 8`: ANN-Tree
- `--search-method 9`: ANN-Graph

---

## 快速测试命令（30个样本）

```bash
# AESLC Baseline RAG 快速测试
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 0 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output ./benchmark/results/aeslc_baseline_quick30.json \
    --checkpoint ./benchmark/results/aeslc_baseline_quick30.json \
    --max-samples 30
```

---

## 使用 Shell 脚本（推荐）

项目中有现成的shell脚本，可以直接运行：

```bash
# AESLC Baseline RAG
./run_aeslc_baseline.sh

# 快速测试（30个样本）
./run_baseline_quick30.sh
```

---

## 环境变量设置

在运行前，确保设置以下环境变量（或在 `.env` 文件中配置）：

```bash
export HF_ENDPOINT=https://hf-mirror.com  # 如果使用HuggingFace镜像
export TOKENIZERS_PARALLELISM=false       # 避免tokenizer警告
```

---

## 注意事项

1. **首次运行会自动构建向量数据库**，这可能需要一些时间
2. **断点续传**：如果中断，可以重新运行相同命令，会自动从checkpoint恢复
3. **API密钥**：确保在 `.env` 文件中配置了 `OPENAI_API_KEY` 或 `ARK_API_KEY`
4. **数据集路径**：确保数据集文件存在于 `./datasets/processed/` 目录下

---

## 完整示例（包含环境设置）

```bash
# 激活conda环境（如果需要）
source ~/opt/anaconda3/etc/profile.d/conda.sh
conda activate python310_arm

# 设置环境变量
export HF_ENDPOINT=https://hf-mirror.com
export TOKENIZERS_PARALLELISM=false

# 进入项目目录
cd /path/to/CFT-RAG-2025-main

# 运行benchmark
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 2 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --max-hierarchy-depth 2 \
    --output ./benchmark/results/aeslc_depth2.json \
    --checkpoint ./benchmark/results/aeslc_depth2.json \
    --max-samples 30

# 评估结果
python benchmark/evaluate_comprehensive.py \
    --results ./benchmark/results/aeslc_depth2.json \
    --output ./benchmark/results/aeslc_depth2_evaluation.json
```



