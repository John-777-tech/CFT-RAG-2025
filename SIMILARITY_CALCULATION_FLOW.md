# Query相似度计算流程详解

## ❓ 问题

**Query进去之后，是否和chunk以及每一个摘要都计算相似度？**

## ✅ 答案

**不是！** 不是暴力计算所有相似度，而是采用**两阶段检索+过滤**的策略：

1. **第一阶段**：向量数据库快速检索top-k个最相似的结果
2. **第二阶段**：只对检索到的结果进行双重相似度过滤

## 🔄 完整流程

### 步骤1：Query编码

```python
# 将query编码成embedding
input_embedding = embed_model.encode([query])[0].tolist()
```

### 步骤2：向量数据库检索（高效检索，不是暴力计算）

```python
# 向量数据库内部使用近似最近邻搜索（ANN）
# 只返回top k*3个最相似的结果（包括chunks和abstracts）
search_results = db.search(table_name, input_embedding, k * 3)
```

**关键点**：
- 向量数据库使用**索引结构**（如HNSW、IVF等）进行快速检索
- **不是**遍历所有chunk和abstract计算相似度
- 只返回最相似的 `k*3` 个候选结果
- 这是**近似最近邻搜索**，速度很快

### 步骤3：关联Chunk和Abstract

```python
# 为每个检索到的chunk找到对应的abstract embedding
results = enrich_results_with_summary_embeddings(results, db, embed_model, input_embedding)
```

### 步骤4：双重相似度过滤（只对检索到的结果计算）

```python
# 只对检索到的k*3个结果进行双重相似度计算
results = filter_contexts_by_dual_threshold(
    results,
    input_embedding,
    threshold_chunk=0.7,
    threshold_summary=0.7,
)
```

**这里才真正计算相似度**：
- 对每个检索到的chunk计算：`sim(query, chunk)`
- 对每个chunk对应的abstract计算：`sim(query, abstract)`
- 只保留两个相似度都 >= 0.7 的结果

### 步骤5：取Top-K

```python
# 最终只保留top k个结果
results = results[:k]
```

## 📊 性能对比

### 暴力方法（如果对所有计算）

假设有：
- 1000个chunks
- 500个abstracts（两个chunk对应一个abstract）
- 总共1500个向量

**暴力计算**：
- 需要计算1500次相似度
- 时间复杂度：O(n)，n=1500

### 当前方法（向量数据库检索）

**向量数据库检索**：
- 使用ANN索引（如HNSW），时间复杂度：O(log n)
- 只检索top k*3个结果（例如k=3，则检索9个）
- 然后只对这9个结果计算双重相似度
- 总计算量：9次相似度计算（而不是1500次）

**性能提升**：约 **150倍** 速度提升！

## 🔍 代码位置

### 向量数据库检索（高效检索）

```python
# rag_base/rag_complete.py, line 225
search_results = db.search(table_name, input_embedding, k * 3)
```

### 双重相似度过滤（精确计算）

```python
# rag_base/rag_complete.py, line 174-182
sim_chunk = util.pytorch_cos_sim(
    util.tensor(query_embedding),
    util.tensor(r["embedding"])
)[0].item()

sim_summary = util.pytorch_cos_sim(
    util.tensor(query_embedding),
    util.tensor(r["summary_embedding"])
)[0].item()
```

## 💡 设计优势

1. **高效**：向量数据库使用索引结构，避免暴力计算
2. **精确**：对候选结果进行双重相似度过滤，确保质量
3. **可扩展**：即使有百万级向量，检索速度仍然很快

## 📝 总结

**不是暴力计算所有相似度**，而是：
1. ✅ 向量数据库快速检索top-k候选（使用索引，不暴力计算）
2. ✅ 只对候选结果进行双重相似度过滤（精确计算）
3. ✅ 最终返回top-k个高质量结果

这样既保证了效率，又保证了检索质量！





