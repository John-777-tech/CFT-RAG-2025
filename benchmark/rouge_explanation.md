# ROUGE评估指标详解

## 什么是ROUGE？

ROUGE（Recall-Oriented Understudy for Gisting Evaluation）是专门用于评估**自动摘要**质量的标准指标，由Lin在2004年提出。

## 三种ROUGE指标的区别

### 1. ROUGE-1（基于单词级别的重叠）

**定义**: 计算参考摘要和生成摘要之间的**单个单词（unigram）重叠度**

**计算公式**:
```
ROUGE-1 = (参考摘要和生成摘要中重叠的单词数) / (参考摘要中的总单词数)
```

**特点**:
- 关注**词级别的匹配**
- 简单直接，计算快速
- 适合评估基本内容覆盖度

**示例**:
- 参考摘要: "The cat sat on the mat"
- 生成摘要: "A cat sits on a mat"
- 重叠单词: cat, on, mat → ROUGE-1较高

---

### 2. ROUGE-2（基于二元组级别的重叠）

**定义**: 计算参考摘要和生成摘要之间的**两个连续单词（bigram）重叠度**

**计算公式**:
```
ROUGE-2 = (参考摘要和生成摘要中重叠的二元组数) / (参考摘要中的总二元组数)
```

**特点**:
- 关注**短语级别的匹配**
- 更能反映**语义连贯性**
- 对词序更敏感，质量要求更高

**示例**:
- 参考摘要: "The cat sat on the mat"
- 生成摘要: "The cat sat on the floor"
- 重叠二元组: "The cat", "cat sat", "sat on", "on the" → ROUGE-2中等
- 如果词序被打乱，ROUGE-2会显著下降

---

### 3. ROUGE-L（基于最长公共子序列）

**定义**: 计算参考摘要和生成摘要之间的**最长公共子序列（Longest Common Subsequence, LCS）**

**计算公式**:
```
ROUGE-L = LCS长度 / (参考摘要长度 + 生成摘要长度 - LCS长度)
```

**特点**:
- **不需要连续匹配**，只要保持顺序即可
- 更能容忍**词序变化**
- 关注**句子级别的结构相似度**
- 适合评估摘要的流畅性和连贯性

**示例**:
- 参考摘要: "The cat sat on the mat"
- 生成摘要: "The cat was sitting on a mat"
- LCS: "The cat ... on ... mat"（不要求连续）

---

## 评估指标：Precision、Recall、F-measure

ROUGE实际上计算三个指标：

### Precision（精确率）
```
Precision = 重叠部分 / 生成摘要的总长度
```
**含义**: 生成摘要中有多少是"对的"（在参考摘要中出现）

### Recall（召回率）
```
Recall = 重叠部分 / 参考摘要的总长度
```
**含义**: 参考摘要中有多少被"找到"了（在生成摘要中出现）

### F-measure（F值）
```
F-measure = 2 × (Precision × Recall) / (Precision + Recall)
```
**含义**: 精确率和召回率的**调和平均**，综合考虑两者

**通常使用F-measure作为最终得分**

---

## 实际评估过程

以我们的benchmark为例：

```python
from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

reference = "The following reports have been waiting for your approval for more than 4 days."
prediction = "The email informs that expense reports are awaiting your approval."

scores = scorer.score(reference, prediction)
# scores['rouge1'].fmeasure  # ROUGE-1的F值
# scores['rouge2'].fmeasure  # ROUGE-2的F值
# scores['rougeL'].fmeasure  # ROUGE-L的F值
```

---

## 为什么我们的结果ROUGE-L最高？

在我们的结果中：
- **改进版本**: ROUGE-L = 0.1345 (13.45%)
- **原始版本**: ROUGE-L = 0.0744 (7.44%)

### ROUGE-L较高的原因：

1. **改进版本的回答更详细**（200字符 vs 68字符）
   - 更多内容意味着有更多机会匹配参考摘要
   - 更长的摘要通常能覆盖更多参考摘要的内容

2. **两个chunk对应一个abstract的方法**：
   - 提供了更丰富的上下文信息
   - 生成的摘要更接近完整的参考答案
   - LCS算法能够找到更多的公共子序列

3. **回答质量更好**：
   - 改进版本的回答虽然不一定完全准确，但包含了更多相关关键词
   - 词序更接近参考摘要，使得LCS长度更长

---

## 指标选择建议

- **ROUGE-1**: 适合评估基本内容覆盖度，简单直接
- **ROUGE-2**: 适合评估语义连贯性和短语匹配质量
- **ROUGE-L**: 适合评估整体摘要质量，是最常用的指标
  - 对词序变化不敏感
  - 更能反映摘要的流畅性和完整性
  - **在摘要任务中，ROUGE-L是最重要的指标**

---

## 我们的评估结果解读

### 改进版本（两个chunk对应一个abstract）
- ROUGE-1: 0.1695 (16.95%) - 词级别匹配较好
- ROUGE-2: 0.0264 (2.64%) - 短语级别匹配较低（说明生成摘要和参考摘要的短语结构差异较大）
- **ROUGE-L: 0.1345 (13.45%)** ⭐ - 整体质量较好

### 原始版本（没有abstract）
- ROUGE-1: 0.0786 (7.86%) - 词级别匹配一般
- ROUGE-2: 0.0242 (2.42%) - 短语级别匹配很低
- **ROUGE-L: 0.0744 (7.44%)** - 整体质量较差

**结论**: 改进版本在所有指标上都优于原始版本，特别是ROUGE-L提升了约80.8%，说明两个chunk对应一个abstract的方法显著提升了摘要质量。

