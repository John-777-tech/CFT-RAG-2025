# RAG代码逻辑详细分析

## 整体流程概览

### 1. **augment_prompt函数**（主函数）

这是核心函数，负责检索和构建prompt。主要步骤：

#### Step 1: 初始化Embedding模型和Query Embedding
```python
embed_model = get_embed_model()
input_embedding = embed_model.encode([query])[0].tolist()
```
- 获取embedding模型
- 将查询转换为embedding向量

#### Step 2: 向量数据库检索
```python
search_results = db.search(table_name, input_embedding, k * 3)
```
- 检索 `k * 3` 个候选结果（k默认为3，所以检索9个）
- 使用余弦相似度在向量数据库中搜索

#### Step 3: 结果处理和过滤（两种路径）

**路径A: Baseline RAG (search_method=0)**
- 直接取top k个结果
- 无需额外的抽象/过滤处理

**路径B: Abstract RAG (search_method != 0)**
- **Step 3.1**: 丰富结果（`enrich_results_with_summary_embeddings`）
  - 为每个raw_chunk找到对应的tree_node（抽象）
  - 两个chunks共享一个abstract（pair_id = chunk_id // 2）
  - 添加summary_embedding到每个结果中

- **Step 3.2**: 双阈值过滤（`filter_contexts_by_dual_threshold`）
  - 要求同时满足：
    - `sim(query, chunk) >= threshold_chunk` (默认0.6)
    - `sim(query, summary) >= threshold_summary` (默认0.6)
  - 如果过滤后结果为空，回退到未过滤的top k

- **Step 3.3**: 取top k
  - 最终只保留k个结果

#### Step 4: 构建source_knowledge
```python
source_knowledge = "\n".join([x["content"] for x in results])
```
- 将选中的chunks内容拼接

#### Step 5: 实体检索和层次上下文（仅Abstract RAG）

对于search_method != 0 且 != 7:
- 调用 `ruler.search_entity_info` 检索实体信息
- 获得实体树节点列表

对于search_method == 7（Cuckoo Filter Abstract RAG）:
- 调用 `ruler.search_entity_info_cuckoofilter_enhanced`
- 这个函数内部会：
  - 使用Cuckoo Filter找到相关实体
  - 根据max_hierarchy_depth回溯层次（向上/向下）
  - 检索层次相关的chunks

#### Step 6: 对实体上下文进行排序和去重
```python
node_list = rank_contexts(query, node_list, ruler.entity_number)
```
- 使用SentenceTransformer计算相似度
- 按相似度排序
- 去除高度相似的项（相似度>0.9）

#### Step 7: 构建tree_knowledge并截断
```python
tree_knowledge = "\n---\n".join(node_list)
source_knowledge = truncate_to_fit(source_knowledge, max_allowed_tokens, model_name)
tree_knowledge = truncate_to_fit(tree_knowledge, max_allowed_tokens, model_name)
```
- 将实体上下文拼接
- 分别截断source_knowledge和tree_knowledge到约7942 tokens

#### Step 8: 构建最终prompt
- 将source_knowledge和tree_knowledge组合成最终prompt

---

## 余弦相似度计算详解

### 1. **filter_contexts_by_dual_threshold函数**

```python
def filter_contexts_by_dual_threshold(
    results: list,
    query_embedding: list[float],
    threshold_chunk: float = 0.7,
    threshold_summary: float = 0.7,
):
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

**计算逻辑**：
1. 使用`util.pytorch_cos_sim`计算余弦相似度
2. `util.pytorch_cos_sim(A, B)`返回一个tensor，需要取`[0].item()`得到标量值
3. **两个条件必须同时满足**：chunk相似度和summary相似度都要达到阈值

**潜在问题检查**：

✅ **维度匹配**：
- `query_embedding`: list[float] → 转换为tensor后是1D向量
- `r["embedding"]`: list[float] → 转换为tensor后是1D向量
- `util.pytorch_cos_sim`接受两个1D向量，返回一个标量（在tensor中）

⚠️ **归一化问题**：
- 代码假设embeddings已经归一化
- 检查`embed_model.encode()`时是否使用了`normalize_embeddings=True`
- 如果没有归一化，余弦相似度计算可能不准确

### 2. **rank_contexts函数**

```python
def rank_contexts(query: str, contexts: list, rank_k: int) -> list:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(query, convert_to_tensor=True)
    context_embeddings = model.encode(contexts, convert_to_tensor=True)
    
    similarities = util.pytorch_cos_sim(query_embedding, context_embeddings)[0]
    
    # 排序并去重
    top_indices = similarities.argsort(descending=True).tolist()
    for idx in top_indices:
        # 去除高度相似的项
        if any(util.pytorch_cos_sim(context_embedding, emb) > 0.9 for emb in seen_embeddings):
            continue
```

**注意**：
1. 这里使用了**不同的embedding模型**（`all-MiniLM-L6-v2`）
2. 与主流程中的embed_model可能不同
3. 这可能导致相似度计算不一致

### 3. **embed_model的使用**

需要检查`get_embed_model()`返回的模型：
- 是否使用`normalize_embeddings=True`？
- 模型类型是什么？
- 与rank_contexts中的模型是否一致？

---

## 关键发现和潜在问题

### ✅ 正确的地方

1. **双阈值过滤逻辑**：同时检查chunk和summary相似度，确保检索到的内容既与query相关，又符合抽象结构
2. **回退机制**：如果过滤后结果为空，回退到未过滤的结果
3. **去重机制**：在rank_contexts中去除高度相似的项

### ⚠️ 潜在问题

#### 1. **Embedding归一化不一致**

**问题**：
- `enrich_results_with_summary_embeddings`中使用`normalize_embeddings=True`
- 但需要检查`get_embed_model()`是否也归一化
- `rank_contexts`中使用的是不同的模型

**影响**：
- 如果embeddings没有归一化，余弦相似度的值域可能不在[-1, 1]
- 可能导致阈值判断不准确

#### 2. **Embedding模型不一致**

**问题**：
- 主流程使用`get_embed_model()`
- `rank_contexts`使用`SentenceTransformer('all-MiniLM-L6-v2')`
- 两个模型的embedding空间不同

**影响**：
- 相似度计算的语义空间不同
- 可能导致排序结果不准确

#### 3. **维度检查不足**

**问题**：
- 代码中缺少对embedding维度的显式检查
- 如果query_embedding和chunk_embedding维度不同，可能会报错或产生错误结果

#### 4. **阈值使用不一致**

**问题**：
- `filter_contexts_by_dual_threshold`默认阈值是0.7
- 但在`augment_prompt`中调用时使用0.6
- 文档说明是0.7，实际代码是0.6

---

## 余弦相似度计算验证

### util.pytorch_cos_sim的实现

`util.pytorch_cos_sim(A, B)`计算：
- 如果A和B都是1D向量，返回`cos(A, B)`
- 如果A是1D，B是2D矩阵，返回每行的相似度
- 公式：`cos(θ) = (A · B) / (||A|| * ||B||)`

### 归一化的重要性

如果embeddings已经归一化（L2 norm = 1），则：
- `cos(θ) = A · B`（点积即可）
- 值域在[-1, 1]之间

如果embeddings未归一化，需要显式计算：
- `cos(θ) = (A · B) / (||A|| * ||B||)`

---

## 建议的修复

1. **统一embedding模型**：确保所有地方使用相同的embedding模型
2. **显式归一化检查**：在所有encode调用中使用`normalize_embeddings=True`
3. **添加维度验证**：在相似度计算前检查维度匹配
4. **统一阈值**：明确阈值的选择理由
5. **添加调试信息**：记录相似度值，便于调试



