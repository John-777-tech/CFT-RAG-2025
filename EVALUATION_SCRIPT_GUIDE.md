# 评估脚本使用指南

## 评估脚本位置

**主要评估脚本**：`benchmark/evaluate_comprehensive.py`

这是你项目中使用的综合评估脚本，支持以下指标：
- **ROUGE-1, ROUGE-2, ROUGE-L**：基于n-gram重叠的摘要评估指标
- **BLEU**：基于n-gram精确匹配的翻译/摘要评估指标
- **BERTScore F1**：基于BERT语义相似度的评估指标

## 如果想让别人用你的评估逻辑评估其他RAG

### 需要分享的文件

只需要分享 **一个文件**：

```
benchmark/evaluate_comprehensive.py
```

这个脚本是**完全独立的**，不依赖项目中的其他代码，可以直接用于评估任何RAG系统的结果。

### 输入数据格式

评估脚本期望的输入JSON格式：

```json
[
  {
    "question": "用户的问题",
    "answer": "RAG系统生成的答案",
    "expected_answer": "标准答案/参考答案",
    "time": 1.23,
    "answer_length": 100
  },
  ...
]
```

**必需字段**：
- `answer`: RAG系统生成的答案
- `expected_answer`: 标准答案/参考答案

**可选字段**：
- `question`: 问题（用于显示）
- `time`: 响应时间
- `answer_length`: 答案长度

### 使用方法

#### 1. 安装依赖

```bash
pip install rouge-score nltk bert-score
```

#### 2. 运行评估

```bash
python evaluate_comprehensive.py \
    --results <结果JSON文件路径> \
    --output <评估结果输出路径> \
    --skip-bertscore  # 可选：跳过BERTScore（首次运行需要下载模型，较慢）
```

#### 3. 示例

```bash
# 评估结果
python evaluate_comprehensive.py \
    --results my_rag_results.json \
    --output my_rag_evaluation.json

# 跳过BERTScore（如果网络有问题或想快速评估）
python evaluate_comprehensive.py \
    --results my_rag_results.json \
    --output my_rag_evaluation.json \
    --skip-bertscore
```

### 输出格式

评估脚本会生成一个JSON文件，包含：

```json
{
  "average_scores": {
    "rouge1": 0.2280,
    "rouge2": 0.0784,
    "rougeL": 0.1541,
    "bleu": 0.0536,
    "bertscore": 0.8248
  },
  "total_samples": 30,
  "detailed_results": [
    {
      "question": "问题示例...",
      "rouge1": 0.25,
      "rouge2": 0.10,
      "rougeL": 0.20,
      "bleu": 0.05,
      "bertscore": 0.85
    },
    ...
  ]
}
```

### 环境变量（可选）

如果需要使用HuggingFace镜像（加速BERTScore模型下载）：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### 完整示例：评估其他RAG系统

假设你有一个其他RAG系统的结果文件 `other_rag_results.json`：

```json
[
  {
    "question": "What is RAG?",
    "answer": "RAG stands for Retrieval Augmented Generation...",
    "expected_answer": "Retrieval Augmented Generation (RAG) is a technique..."
  },
  ...
]
```

运行评估：

```bash
# 1. 复制评估脚本
cp benchmark/evaluate_comprehensive.py /path/to/other/project/

# 2. 安装依赖
pip install rouge-score nltk bert-score

# 3. 运行评估
python evaluate_comprehensive.py \
    --results other_rag_results.json \
    --output other_rag_evaluation.json
```

### 注意事项

1. **BERTScore首次运行**：需要下载roberta-large模型（约1.3GB），可能需要10-20分钟
2. **网络问题**：如果下载失败，可以：
   - 设置 `HF_ENDPOINT=https://hf-mirror.com` 使用镜像
   - 或使用 `--skip-bertscore` 跳过BERTScore评估
3. **NLTK数据**：脚本会自动下载punkt tokenizer，如果失败可以手动下载：
   ```python
   import nltk
   nltk.download('punkt')
   ```

### 依赖包版本建议

```bash
rouge-score>=0.1.2
nltk>=3.8
bert-score>=0.3.13
```

### 快速分享清单

如果你想分享评估脚本给别人，只需要：

1. ✅ **一个文件**：`benchmark/evaluate_comprehensive.py`
2. ✅ **使用说明**：告诉他们输入格式和运行命令
3. ✅ **依赖列表**：`rouge-score`, `nltk`, `bert-score`

**不需要**：
- ❌ 整个项目代码
- ❌ 向量数据库
- ❌ 其他配置文件

### 验证脚本独立性

评估脚本是完全独立的，你可以这样验证：

```bash
# 在一个新目录测试
mkdir test_evaluation
cd test_evaluation

# 只复制评估脚本
cp /path/to/CFT-RAG-2025-main/benchmark/evaluate_comprehensive.py .

# 创建测试数据
cat > test_results.json << EOF
[
  {
    "question": "Test question",
    "answer": "This is a test answer.",
    "expected_answer": "This is the expected answer."
  }
]
EOF

# 运行评估（应该能正常工作）
python evaluate_comprehensive.py --results test_results.json --output test_eval.json
```



