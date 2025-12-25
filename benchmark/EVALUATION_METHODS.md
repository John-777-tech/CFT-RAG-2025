# 评估方法对比与分析

## 1. 两个chunk对应一个abstract vs 一个chunk对应一个abstract

### 两个chunk对应一个abstract（当前实现）

**优点**：
- ✅ **减少存储开销**：更少的abstract节点（减少50%）
- ✅ **提供更丰富的上下文**：每个abstract涵盖两个chunk的内容，语义更完整
- ✅ **双重过滤机制**：dual-threshold同时检查chunk和summary相似度，过滤更精确
- ✅ **减少噪声**：不相关的chunks会被abstract级别的相似度过滤掉

**缺点**：
- ⚠️ **可能信息丢失**：如果两个chunk语义差异较大，合并的abstract可能不够精确
- ⚠️ **检索粒度变粗**：对于需要精确匹配单个chunk的场景可能不够准确

### 一个chunk对应一个abstract（原始方法）

**优点**：
- ✅ **精确匹配**：每个chunk都有对应的abstract，匹配更精确
- ✅ **粒度更细**：可以精确定位到单个chunk

**缺点**：
- ❌ **存储开销大**：abstract节点数量与chunk数量相同
- ❌ **可能过度细化**：对于语义相近的chunks，分别构建abstract可能冗余

### 建议

根据AESLC数据集的特点（邮件摘要任务，语义相对完整）：
- **推荐使用"两个chunk对应一个abstract"**，因为：
  1. 邮件内容通常语义完整，两个chunk合并后更能体现完整语义
  2. 摘要任务不需要精确到单个句子，而是需要整体理解
  3. 双重过滤机制可以提高检索质量

## 2. 数据集语言问题

**发现**：
- AESLC数据集是**英文**的（邮件正文全部是英文）
- 但我们的prompt包含中文"摘要以下邮件"，导致模型用中文回答
- 需要将prompt改为英文

**解决方案**：
```python
# 原来的prompt（中文）
prompt = f"摘要以下邮件: {subject}"

# 应该改为（英文）
prompt = f"Summarize the following email: {subject}"
```

## 3. 评估方法

### 3.1 LangSmith评估（论文使用）

**特点**：
- 使用LangSmith平台进行标准化评估
- 可以对LLM回答内容进行评分
- 需要LangSmith账号和API key

**优点**：
- ✅ 标准化评估流程
- ✅ 可以与论文结果对比
- ✅ 支持多种评估指标

**缺点**：
- ❌ 需要外部平台依赖
- ❌ 可能需要API调用费用

### 3.2 ROUGE指标（推荐用于摘要任务）

**ROUGE (Recall-Oriented Understudy for Gisting Evaluation)**：
- **ROUGE-1**：基于unigram的召回率
- **ROUGE-2**：基于bigram的召回率
- **ROUGE-L**：基于最长公共子序列（LCS）

**优点**：
- ✅ 专门用于摘要任务评估
- ✅ 不依赖外部服务
- ✅ 计算速度快
- ✅ 广泛使用的标准指标

**实现**：
```python
from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
scores = scorer.score(reference, prediction)
```

### 3.3 BLEU指标

**BLEU (Bilingual Evaluation Understudy)**：
- 基于n-gram精确度的评估
- 主要用于机器翻译，也可用于摘要

**优点**：
- ✅ 标准评估指标
- ✅ 易于实现

**缺点**：
- ❌ 对摘要任务不如ROUGE准确
- ❌ 主要关注精确度，不关注召回率

### 3.4 METEOR指标

**METEOR (Metric for Evaluation of Translation with Explicit ORdering)**：
- 考虑同义词和词序的评估指标

**优点**：
- ✅ 比BLEU更准确
- ✅ 考虑同义词匹配

**缺点**：
- ❌ 计算复杂度较高

### 3.5 语义相似度（BERTScore）

**BERTScore**：
- 使用BERT embedding计算语义相似度

**优点**：
- ✅ 考虑语义相似度，不只是词汇匹配
- ✅ 对摘要任务效果好

**实现**：
```python
from bert_score import score

P, R, F1 = score(predictions, references, lang='en', verbose=True)
```

### 3.6 自定义LLM评估（项目中使用的方法）

**项目中的`custom_score_match`**：
- 使用LLM评估prediction和reference的相似度
- 给出0-100的分数

**优点**：
- ✅ 可以理解语义
- ✅ 灵活性强

**缺点**：
- ❌ 需要API调用，成本高
- ❌ 结果可能不稳定

## 4. 推荐评估方案

对于AESLC数据集（邮件摘要任务），推荐使用：

1. **主要指标**：ROUGE-L（最适合摘要任务）
2. **辅助指标**：ROUGE-1, ROUGE-2
3. **可选指标**：BERTScore（如果可用）

这样可以：
- 与学术标准一致
- 不需要外部依赖
- 计算速度快
- 结果可复现


