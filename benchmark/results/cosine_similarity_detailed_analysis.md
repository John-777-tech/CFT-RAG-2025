# 余弦相似度计算详细分析和问题检查

## 代码逻辑梳理

### 整体流程

```
用户Query
    ↓
[1] embed_model.encode([query]) → query_embedding
    ↓
[2] db.search(query_embedding, k*3) → 检索9个候选chunks
    ↓
[3] enrich_results_with_summary_embeddings()
    - 为每个chunk找到对应的abstract（tree_node）
    - 两个chunks共享一个abstract（pair_id = chunk_id // 2）
    - 添加summary_embedding到每个结果
    ↓
[4] filter_contexts_by_dual_threshold()
    - 计算 sim(query, chunk) 
    - 计算 sim(query, summary)
    - 必须同时 >= 阈值（0.6）才保留
    ↓
[5] 取top k（通常k=3）
    ↓
[6] 实体检索和层次上下文构建（search_method=7时）
    ↓
[7] rank_contexts() - 对实体上下文排序
    ↓
[8] 构建最终prompt
```

---

## 余弦相似度计算详解

### 1. filter_contexts_by_dual_threshold 函数

**位置**：`rag_complete.py:171-205`

**代码**：
```python
def filter_contexts_by_dual_threshold(
    results: list,
    query_embedding: list[float],
    threshold_chunk: float = 0.7,
    threshold_summary: float = 0.7,
):
    for r in results:
        sim_chunk = util.pytorch_cos_sim(
            util.tensor(query_embedding),
            util.tensor(r["embedding"])
        )[0].item()
        
        sim_summary = util.pytorch_cos_sim(
            util.tensor(query_embedding),
            util.tensor(r["summary_embedding"])
        )[0].item()
        
        if sim_chunk >= threshold_chunk and sim_summary >= threshold_summary:
            filtered.append(r)
```

**分析**：

✅ **计算方式正确**：
- `util.pytorch_cos_sim(A, B)` 计算两个向量的余弦相似度
- 返回 `cos(θ) = (A · B) / (||A|| * ||B||)`
- `[0].item()` 从tensor中提取标量值

⚠️ **关键问题 - 归一化检查**：
- 代码中**没有显式检查embedding是否归一化**
- `util.pytorch_cos_sim`会**自动归一化**（如果向量未归一化，会先归一化再计算）
- 但为了性能，最好确保embeddings已经归一化

⚠️ **实际使用的阈值**：
- 函数默认阈值是0.7
- 但调用时传入的是0.6：
  ```python
  results = filter_contexts_by_dual_threshold(
      results,
      input_embedding,
      threshold_chunk=0.6,  # 实际使用0.6
      threshold_summary=0.6,
  )
  ```

---

### 2. enrich_results_with_summary_embeddings 函数

**位置**：`rag_complete.py:86-168`

**关键代码**：
```python
# 对于tree_node，计算embedding
tree_embedding = embed_model.encode([tree_text], normalize_embeddings=True)[0].tolist()

# 对于缺失abstract的情况，合并两个chunks
merged_text = "\n".join(merged_text_parts)
r["summary_embedding"] = embed_model.encode([merged_text], normalize_embeddings=True)[0].tolist()
```

**分析**：

✅ **正确使用归一化**：
- 代码中使用了 `normalize_embeddings=True`
- 这确保了summary_embedding已经归一化

❓ **需要检查**：
- `query_embedding` 的生成是否也使用了归一化？
- `r["embedding"]`（chunk embedding）是否归一化？

---

### 3. query_embedding 的生成

**位置**：`rag_complete.py:225`

**代码**：
```python
input_embedding: list[float] = embed_model.encode([query])[0].tolist()
```

⚠️ **问题发现**：
- **没有使用 `normalize_embeddings=True`**
- 这意味着query_embedding可能没有归一化
- 但chunk_embedding和summary_embedding可能已经归一化（取决于数据库中的存储方式）

**影响**：
- 如果只有query_embedding未归一化，余弦相似度计算仍然正确（`util.pytorch_cos_sim`会处理）
- 但可能导致性能下降（每次计算都需要归一化）

---

### 4. rank_contexts 函数

**位置**：`rag_complete.py:50-83`

**代码**：
```python
def rank_contexts(query: str, contexts: list, rank_k: int) -> list:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(query, convert_to_tensor=True)
    context_embeddings = model.encode(contexts, convert_to_tensor=True)
    
    similarities = util.pytorch_cos_sim(query_embedding, context_embeddings)[0]
```

**问题**：

⚠️ **使用不同的embedding模型**：
- 主流程使用 `get_embed_model()` → `sentence-transformers/all-MiniLM-L6-v2`
- 这里硬编码使用 `SentenceTransformer('all-MiniLM-L6-v2')`
- 虽然看起来是同一个模型，但**可能使用不同的实例或配置**

⚠️ **归一化问题**：
- 没有显式使用 `normalize_embeddings=True`
- 默认情况下，SentenceTransformer可能不归一化

⚠️ **语义空间不一致**：
- 即使模型相同，如果编码方式不同（归一化vs非归一化），可能导致排序结果不准确

---

## 发现的问题总结

### ❌ 问题1：Query Embedding未归一化

**位置**：`rag_complete.py:225`

**代码**：
```python
input_embedding: list[float] = embed_model.encode([query])[0].tolist()
```

**应该改为**：
```python
input_embedding: list[float] = embed_model.encode([query], normalize_embeddings=True)[0].tolist()
```

### ⚠️ 问题2：rank_contexts使用不一致的编码方式

**位置**：`rag_complete.py:50-83`

**问题**：
- 使用不同的模型实例（虽然可能是同一个模型）
- 没有显式归一化

**建议修复**：
```python
def rank_contexts(query: str, contexts: list, rank_k: int, embed_model=None) -> list:
    if embed_model is None:
        embed_model = get_embed_model()  # 使用统一的模型
    
    query_embedding = embed_model.encode([query], normalize_embeddings=True, convert_to_tensor=True)
    context_embeddings = embed_model.encode(contexts, normalize_embeddings=True, convert_to_tensor=True)
    # ...
```

### ⚠️ 问题3：Chunk Embedding的归一化状态未知

**问题**：
- 代码中从数据库检索的chunk embedding（`r["embedding"]`）可能已经归一化，也可能没有
- 取决于构建索引时的处理方式

**建议**：
- 检查 `build_index.py` 中存储embedding时是否归一化
- 或者在检索后显式归一化

---

## 余弦相似度计算验证

### util.pytorch_cos_sim 的实现原理

`sentence_transformers.util.pytorch_cos_sim` 的实现：

```python
def pytorch_cos_sim(a, b):
    """
    计算余弦相似度
    如果向量未归一化，会先归一化再计算
    """
    a_norm = F.normalize(a, p=2, dim=-1)
    b_norm = F.normalize(b, p=2, dim=-1)
    return torch.mm(a_norm, b_norm.t())
```

**特点**：
- **会自动归一化**：即使输入向量未归一化，也会先归一化再计算
- **因此，即使embedding未归一化，计算也是正确的**
- 但**性能可能受影响**（每次都要归一化）

### 相似度值域

- **归一化的embedding**：相似度值域在 [-1, 1]
- **未归一化的embedding**：通过pytorch_cos_sim计算后，值域也在 [-1, 1]
- **实际使用中**：相似度通常在 [0, 1] 之间（对于正常的文本embedding）

---

## 实际运行中的行为分析

### 双阈值过滤的实际效果

```python
if sim_chunk >= 0.6 and sim_summary >= 0.6:
    # 保留这个chunk
```

**分析**：
1. 必须同时满足两个条件
2. 阈值0.6相对较低（对于归一化的embedding，0.6表示中等相似度）
3. 如果过滤后结果为空，会回退到未过滤的top k

**可能的问题**：
- 如果summary_embedding计算不准确，可能导致大量chunks被过滤掉
- Depth=1时，可能检索到的chunks相关性较低，两个相似度都达不到0.6，导致过滤后结果很少

---

## 建议的修复方案

### 修复1：确保所有embedding归一化

```python
# rag_complete.py:225
input_embedding: list[float] = embed_model.encode(
    [query], 
    normalize_embeddings=True  # 添加归一化
)[0].tolist()
```

### 修复2：统一rank_contexts的模型

```python
def rank_contexts(query: str, contexts: list, rank_k: int, embed_model=None) -> list:
    if embed_model is None:
        from rag_base.embed_model import get_embed_model
        embed_model = get_embed_model()
    
    query_embedding = embed_model.encode(
        [query], 
        normalize_embeddings=True, 
        convert_to_tensor=True
    )
    context_embeddings = embed_model.encode(
        contexts, 
        normalize_embeddings=True, 
        convert_to_tensor=True
    )
    # ...
```

### 修复3：添加调试信息

```python
def filter_contexts_by_dual_threshold(...):
    if debug:
        print(f"Filtering {len(results)} results")
        print(f"Thresholds: chunk={threshold_chunk}, summary={threshold_summary}")
    
    for r in results:
        sim_chunk = ...
        sim_summary = ...
        
        if debug:
            print(f"Chunk sim={sim_chunk:.4f}, Summary sim={sim_summary:.4f}")
        
        if sim_chunk >= threshold_chunk and sim_summary >= threshold_summary:
            filtered.append(r)
    
    if debug:
        print(f"Filtered to {len(filtered)} results")
    
    return filtered
```

---

## 结论

### ✅ 正确的地方

1. **余弦相似度计算本身是正确的**：`util.pytorch_cos_sim`会自动处理归一化
2. **双阈值过滤逻辑合理**：同时检查chunk和summary相似度
3. **回退机制完善**：过滤后为空时回退到未过滤结果

### ❌ 需要修复的问题

1. **Query embedding未归一化**：应该添加`normalize_embeddings=True`
2. **rank_contexts使用不同的模型实例**：应该使用统一的embed_model
3. **缺少归一化的显式检查**：虽然会自动处理，但显式归一化更清晰

### ⚠️ 潜在问题

1. **阈值0.6可能过低或过高**：需要根据实际数据调整
2. **Depth=1时过滤可能过于严格**：如果检索到的chunks相关性低，可能被大量过滤



