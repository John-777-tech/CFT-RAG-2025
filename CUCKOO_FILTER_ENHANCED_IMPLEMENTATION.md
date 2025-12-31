# Cuckoo Filter增强实现说明

## 概述

本次实现增强了Cuckoo Filter的检索逻辑，使其能够：
1. 通过实体识别找到查询中的实体
2. 在Cuckoo Filter中查询实体，获取对应的摘要（abstract/tree_node）
3. 从向量数据库中检索摘要对应的原文段落（top k）
4. 向上/下追溯层次结构（1-2层）获取父节点和子节点的摘要及原文
5. 将所有信息整合到context中用于RAG

## 实现细节

### 1. 新增函数：`search_entity_info_cuckoofilter_enhanced`

位置：`entity/ruler.py`

**功能流程**：

#### Step 1: 实体识别
- 使用Spacy NLP模型识别查询中的实体（标签为'EXTRA'）

#### Step 2: Cuckoo Filter查询
- 对每个识别出的实体，调用`hash.cuckoo_extract(entity_text)`
- 获取实体对应的摘要层级信息（包含父节点、子节点关系）

#### Step 3: 向量数据库检索
- 使用查询embedding在向量数据库中搜索
- 分别收集`tree_node`（摘要）和`raw_chunk`（原文段落）结果

#### Step 4: 实体到摘要的映射
- 对于每个实体，在`tree_node_results`中查找包含该实体的摘要
- 提取摘要的`chunk_ids`（该摘要对应的原文段落ID列表）
- 建立映射：`entity -> list of (tree_node, chunk_ids, abstract_content)`

#### Step 5: 获取原文段落
- 从`raw_chunk_results`中提取`chunk_id -> content`的映射
- 为每个摘要找到对应的原文段落内容

#### Step 6: 构建上下文
- 对于每个实体，组合以下信息：
  - 实体名称
  - Cuckoo Filter返回的层级关系信息
  - 摘要内容（abstract）
  - 对应的原文段落（original text chunks）

#### Step 7: 层次遍历（可选增强）
- 如果提供了`forest`（实体树森林），进行层次遍历：
  - 在forest中找到实体对应的`EntityNode`
  - 向上追溯父节点（最多`max_hierarchy_depth`层）
  - 向下追溯子节点（最多`max_hierarchy_depth`层）
  - 对于每个父/子节点，查找其对应的摘要和原文段落
  - 将这些相关信息也添加到context中

### 2. 辅助函数：`_find_node_by_entity_name`

- 在EntityTree中通过BFS搜索找到指定实体名的节点
- 优先使用EntityTree的`bfs_search`方法（如果存在）
- 否则手动实现BFS遍历

### 3. 集成到RAG流程

在`rag_base/rag_complete.py`的`augment_prompt`函数中：

```python
elif search_method == 7:
    # Enhanced Cuckoo Filter search with hierarchical abstract retrieval
    try:
        search_context = ruler.search_entity_info_cuckoofilter_enhanced(
            nlp, 
            query,
            db,  # Vector database for retrieving chunks
            embed_model,  # Embedding model
            forest,  # Entity forest for hierarchy traversal
            k=k,  # Number of chunks per abstract
            max_hierarchy_depth=2  # Traverse 1-2 levels up/down
        )
        node_list = [search_context] if search_context else []
    except Exception as e:
        # Fallback to original Cuckoo Filter search if enhanced version fails
        print(f"Warning: Enhanced Cuckoo Filter search failed, falling back to original: {e}")
        search_context = ruler.search_entity_info_cuckoofilter(nlp, query)
        node_list = [search_context] if search_context else []
```

## 数据结构

### 摘要节点（tree_node）的metadata结构
```python
{
    "type": "tree_node",
    "pair_id": "0",  # 摘要ID（两个chunk对应一个摘要）
    "chunk_ids": "[0, 1]",  # 该摘要对应的原文段落ID列表
    "content": "...",  # 摘要内容
    "title": "..."
}
```

### 原文段落（raw_chunk）的metadata结构
```python
{
    "type": "raw_chunk",
    "chunk_id": "0",  # 段落ID
    "content": "...",  # 段落内容
    "title": "..."
}
```

## 关键设计决策

1. **实体到摘要的映射策略**：
   - 通过检查实体名称是否出现在摘要的content或title中来匹配
   - 这是一个简化的方法，实际应用中可能需要更精确的映射

2. **层次遍历深度**：
   - 默认`max_hierarchy_depth=2`，可以向上/下追溯1-2层
   - 可配置，避免检索过多不相关的内容

3. **Fallback机制**：
   - 如果增强版本失败，自动回退到原始的Cuckoo Filter搜索
   - 确保系统的鲁棒性

4. **上下文组合**：
   - 按照实体分组组织上下文
   - 每个实体包含：层级信息、摘要、原文段落
   - 如果进行了层次遍历，还包含父/子节点的相关信息

## 使用示例

```python
# 在benchmark测试中使用
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/medqa.json \
    --vec-db-key medqa \
    --entities-file-name medqa_entities_file \
    --search-method 7 \  # 使用增强的Cuckoo Filter
    --tree-num-max 50 \
    --output ./benchmark/results/medqa_cuckoo_enhanced.json
```

## 注意事项

1. **Cuckoo Filter编译**：
   - 需要确保`TRAG-cuckoofilter`已经正确编译
   - `cuckoo_filter_module`可以正常导入

2. **实体识别**：
   - 依赖Spacy模型（`zh_core_web_sm`）
   - 实体标签必须是'EXTRA'

3. **向量数据库**：
   - 需要确保向量数据库已经构建，包含`tree_node`和`raw_chunk`两种类型的数据
   - `chunk_ids`需要正确存储在metadata中

4. **性能考虑**：
   - 层次遍历可能增加检索时间
   - 建议根据实际需求调整`k`和`max_hierarchy_depth`参数

## 未来改进方向

1. **更精确的实体-摘要映射**：
   - 使用embedding相似度而不是简单的字符串匹配
   - 建立实体到摘要的显式映射表

2. **层次遍历优化**：
   - 缓存层次关系查询结果
   - 限制层次遍历的范围（只遍历相关的分支）

3. **上下文去重**：
   - 避免重复的原文段落出现在context中
   - 使用相似度阈值去除高度重复的内容

4. **摘要质量提升**：
   - 对多个chunk的合并摘要进行优化
   - 使用更先进的摘要生成方法





