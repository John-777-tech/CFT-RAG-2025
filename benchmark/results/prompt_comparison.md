# Depth=1 vs Depth=2 Prompt 对比

生成时间: 2025-12-30

## Prompt 格式说明

根据代码分析（`rag_base/rag_complete.py`），对于 **search_method=7 (Cuckoo Filter)** 的prompt格式如下：

---

## 基本 Prompt 模板

### 当有 Abstract 信息时：

#### 英文查询（包含 'summarize', 'email', 'summary' 关键字）：
```
Answer the question using the provided information.

Information:
{source_knowledge}

Abstracts:
{abstract_knowledge}

Question: 
{query}
```

#### 中文查询（其他情况）：
```
请回答问题，可以使用我提供的信息（不保证信息是有用的），在回答中不要有分析我提供信息的内容，直接说答案，答案要简略。

信息:
{source_knowledge}

摘要：
{abstract_knowledge}

问题: 
{query}
```

### 当没有 Abstract 信息时：

#### 英文查询：
```
Answer the question using the provided information.

Information:
{source_knowledge}

Question: 
{query}
```

#### 中文查询：
```
请回答问题，可以使用我提供的信息（不保证信息是有用的），在回答中不要有分析我提供信息的内容，直接说答案，答案要简略。

信息:
{source_knowledge}

问题: 
{query}
```

---

## Depth=1 vs Depth=2 的区别

### ⚠️ 重要发现：

从代码分析来看，**`max_hierarchy_depth` 参数在当前实现中并不会改变 prompt 的格式**。

`max_hierarchy_depth` 参数的作用在于：

1. **影响 Abstract Tree 的构建深度**：
   - Depth=1: 只构建一层 abstract tree（每个 abstract 对应 2 个 chunks）
   - Depth=2: 构建两层 abstract tree（abstract 的 abstract）

2. **影响检索到的 Abstract 内容**：
   - Depth=1: 只检索到第一层 abstract（直接对应的 abstract）
   - Depth=2: 可能检索到更深层的 abstract（abstract 的 abstract）

3. **Prompt 格式保持一致**：
   - 无论 depth=1 还是 depth=2，prompt 的格式都是相同的
   - 区别在于 `{source_knowledge}` 和 `{abstract_knowledge}` 中的**内容质量**和**抽象层次**

---

## 具体差异分析

### Depth=1 的检索流程：

1. 从 query 中提取实体（使用 Spacy）
2. 在 Cuckoo Filter 中查找实体对应的 abstract pair_ids（第一层）
3. 通过 pair_id 找到对应的 2 个 chunks
4. 计算 query 和 chunks 的余弦相似度，选 top-k chunks
5. 获取选中 chunks 对应的第一层 abstract
6. 构建 prompt：
   - `source_knowledge`: top-k chunks 的内容
   - `abstract_knowledge`: 对应的第一层 abstract 内容

### Depth=2 的检索流程：

1. 从 query 中提取实体（使用 Spacy）
2. 在 Cuckoo Filter 中查找实体对应的 abstract pair_ids（可能包括第一层和第二层）
3. 通过 pair_id 找到对应的 chunks（可能来自不同层级）
4. 计算 query 和 chunks 的余弦相似度，选 top-k chunks
5. 获取选中 chunks 对应的 abstract（可能包括第一层和第二层）
6. 构建 prompt：
   - `source_knowledge`: top-k chunks 的内容（可能来自不同层级）
   - `abstract_knowledge`: 对应的 abstract 内容（可能包括多层 abstract）

---

## 为什么 Depth=2 表现更差？

根据评估结果，Depth=2 在所有数据集上的评估分数都显著下降。可能的原因：

1. **信息噪音增加**：
   - Depth=2 检索到的 abstract 可能包含更多的抽象信息
   - 这些抽象信息可能与 query 的相关性较低
   - 导致 LLM 接收到的上下文质量下降

2. **检索精度下降**：
   - 更深层的 abstract 可能丢失了原始 chunk 的详细信息
   - 增加了检索到不相关内容的风险
   - Cuckoo Filter 在多层级检索时的准确性可能下降

3. **Prompt 长度增加**：
   - Depth=2 可能检索到更多的 abstract
   - 导致 `abstract_knowledge` 部分过长
   - 可能分散了 LLM 对核心信息的注意力

4. **层次结构复杂性**：
   - 多层 abstract 的结构可能不够清晰
   - LLM 可能难以理解多层抽象之间的关系
   - 导致答案质量下降

---

## 代码位置

- Prompt 构建逻辑: `rag_base/rag_complete.py` 第 631-651 行
- Abstract 检索逻辑: `rag_base/rag_complete.py` 第 272-501 行（search_method=7）
- Abstract Tree 构建: `trag_tree/build.py`

---

## 建议

1. **继续使用 Depth=1**：
   - 当前配置下表现更好
   - Prompt 格式简洁清晰
   - 检索质量更高

2. **如果需要改进 Depth=2**：
   - 优化多层 abstract 的构建逻辑
   - 改进多层级检索的准确性
   - 考虑对 abstract_knowledge 进行更严格的过滤
   - 调整 prompt 格式以更好地利用多层信息

3. **进一步分析**：
   - 对比 depth=1 和 depth=2 检索到的具体内容
   - 分析 abstract_knowledge 的差异
   - 找出 depth=2 引入噪音的具体原因

