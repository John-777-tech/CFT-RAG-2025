# 双重相似度过滤机制详解

## 📋 核心概念

### 1. 两个Chunk对应一个Abstract的结构

```
Chunk 0 (chunk_id=0) ──┐
                        ├──> Abstract 0 (pair_id=0) = Chunk 0 + Chunk 1
Chunk 1 (chunk_id=1) ──┘

Chunk 2 (chunk_id=2) ──┐
                        ├──> Abstract 1 (pair_id=1) = Chunk 2 + Chunk 3
Chunk 3 (chunk_id=3) ──┘

Chunk 4 (chunk_id=4) ──┐
                        ├──> Abstract 2 (pair_id=2) = Chunk 4 + Chunk 5
Chunk 5 (chunk_id=5) ──┘
```

**连接规则**：
- `pair_id = chunk_id // 2` （整数除法）
- Chunk 0 和 Chunk 1 → pair_id = 0
- Chunk 2 和 Chunk 3 → pair_id = 1
- Chunk 4 和 Chunk 5 → pair_id = 2

## 🔍 双重相似度过滤（Dual-Similarity Filtering）

### 工作原理

对于每个检索到的chunk，需要**同时满足两个条件**才能被保留：

1. **Chunk相似度**：`sim(query, chunk) >= threshold_chunk` (默认0.7)
2. **Summary相似度**：`sim(query, abstract) >= threshold_summary` (默认0.7)

### 代码实现

```python
def filter_contexts_by_dual_threshold(
    results: list,
    query_embedding: list[float],
    threshold_chunk: float = 0.7,
    threshold_summary: float = 0.7,
):
    """
    保留chunk的条件：
    1) sim(query, chunk) >= threshold_chunk
    2) sim(query, corresponding summary) >= threshold_summary
    """
    filtered = []
    for r in results:
        # 计算query与chunk的相似度
        sim_chunk = cosine_similarity(query_embedding, r["embedding"])
        
        # 计算query与abstract的相似度
        sim_summary = cosine_similarity(query_embedding, r["summary_embedding"])
        
        # 两个相似度都要高才保留
        if sim_chunk >= threshold_chunk and sim_summary >= threshold_summary:
            filtered.append(r)
    
    return filtered
```

## 🔄 完整流程

### 步骤1：构建索引（build_index.py）

```python
def expand_chunks_to_tree_nodes(chunks: list[str]):
    items = []
    
    # 1. 保存所有原始chunks
    for idx, chunk in enumerate(chunks):
        items.append({
            "text": chunk,
            "meta": {
                "type": "raw_chunk",
                "chunk_id": idx,  # 0, 1, 2, 3, ...
            }
        })
    
    # 2. 每两个chunk创建一个abstract
    pair_id = 0
    for i in range(0, len(chunks), 2):
        merged_text = chunks[i]
        if i + 1 < len(chunks):
            merged_text = chunks[i] + "\n" + chunks[i + 1]
        
        items.append({
            "text": merged_text,  # 两个chunk合并的文本
            "meta": {
                "type": "tree_node",
                "pair_id": pair_id,  # 0, 1, 2, ...
                "chunk_ids": [i, i+1],  # 关联的chunk IDs
            }
        })
        pair_id += 1
```

### 步骤2：检索（augment_prompt）

1. **向量数据库搜索**：检索top-k个最相似的chunks和abstracts
2. **关联chunk和abstract**：通过`enrich_results_with_summary_embeddings`函数

```python
def enrich_results_with_summary_embeddings(results, db, embed_model, query_embedding):
    for r in results:
        if r.get("type") == "raw_chunk":
            chunk_id = r.get("chunk_id")
            # 计算对应的pair_id
            pair_id = chunk_id // 2  # 两个chunk共享一个abstract
            
            # 找到对应的abstract embedding
            if pair_id in tree_node_map:
                r["summary_embedding"] = tree_node_map[pair_id]
            else:
                # 如果abstract不在结果中，合并两个chunk创建abstract
                chunk_ids = [pair_id * 2, pair_id * 2 + 1]
                merged_text = merge_chunks(chunk_ids)
                r["summary_embedding"] = embed_model.encode(merged_text)
```

### 步骤3：双重相似度过滤

```python
# 在augment_prompt中调用
enriched_results = enrich_results_with_summary_embeddings(results, db, embed_model, input_embedding)

# 双重相似度过滤
filtered_results = filter_contexts_by_dual_threshold(
    enriched_results,
    input_embedding,
    threshold_chunk=0.7,
    threshold_summary=0.7
)
```

## 💡 为什么需要双重相似度？

### 优势

1. **更精确的检索**：
   - 只检查chunk相似度可能误检（chunk包含无关信息）
   - 只检查abstract相似度可能漏检（abstract太概括）
   - **两者都高** → 确保chunk既相关又准确

2. **利用层次结构**：
   - Chunk：细粒度信息
   - Abstract：粗粒度概括
   - 两者结合：既保证细节相关，又保证整体主题匹配

3. **减少噪声**：
   - 如果chunk相似度高但abstract相似度低 → 可能是局部匹配，整体不相关
   - 如果abstract相似度高但chunk相似度低 → 可能是概括匹配，细节不相关
   - **两者都高** → 确保整体和细节都相关

## 📊 示例

假设query = "邮件摘要：费用报告审批"

### 场景1：两个相似度都高 ✅

- Chunk: "费用报告等待您的审批，请尽快处理"
- Abstract: "费用报告审批相关邮件内容"
- sim(query, chunk) = 0.85
- sim(query, abstract) = 0.80
- **结果：保留** ✅

### 场景2：只有chunk相似度高 ❌

- Chunk: "费用报告等待您的审批"
- Abstract: "系统维护通知和技术更新"
- sim(query, chunk) = 0.90
- sim(query, abstract) = 0.50
- **结果：过滤掉** ❌（abstract不相关，说明chunk可能是误匹配）

### 场景3：只有abstract相似度高 ❌

- Chunk: "系统维护时间安排"
- Abstract: "费用报告审批相关邮件"
- sim(query, chunk) = 0.40
- sim(query, abstract) = 0.85
- **结果：过滤掉** ❌（chunk不相关，虽然abstract相关）

## 🎯 总结

**连接方式**：
- 通过 `pair_id = chunk_id // 2` 连接两个chunk到一个abstract
- Chunk 0,1 → Abstract 0
- Chunk 2,3 → Abstract 1
- ...

**过滤条件**：
- **必须同时满足**：
  1. `sim(query, chunk) >= 0.7`
  2. `sim(query, abstract) >= 0.7`
- 这样可以确保检索到的chunk既在细节上相关，又在整体主题上匹配


