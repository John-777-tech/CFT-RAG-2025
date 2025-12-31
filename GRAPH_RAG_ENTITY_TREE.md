# Graph RAG 实体树使用说明

## 答案：不需要重建实体树

**Graph RAG (search_method=9) 会复用已经构建的实体树（forest）中的节点，不需要重建。**

## 工作原理

### 1. 执行顺序

在 `main.py` 和 `benchmark/run_benchmark.py` 中，执行顺序是：

```python
# 步骤1: 先构建实体树（forest）
forest, nlp = build.build_forest(
    tree_num_max, entities_file_name, search_method, node_num_max
)

# 步骤2: 如果 search_method == 9，构建图结构
if search_method in [9]:
    build_graph(entities_file_name)  # 复用 forest 中的节点
```

### 2. 节点复用机制

在 `grag_graph/graph.py` 的 `build_graph` 函数中：

```python
def build_graph(entities_file_name):
    # 读取实体关系文件
    with open(entities_file_name+".csv", "r", encoding='utf-8') as csvfile:
        # ... 读取关系数据 ...
    
    for edge in data:
        entity_1 = edge[0]
        entity_2 = edge[1]
        
        # ✅ 关键：检查节点是否已经在 hash.node_hash 中存在
        if entity_1 in hash.node_hash:
            # 复用已有的节点（来自 forest）
            e1 = hash.node_hash[entity_1][0]
        else:
            # 只有在不存在时才创建新节点
            e1 = EntityNode(entity_1)
            hash.node_hash[entity_1] = [e1]
        
        # 同样的逻辑处理 entity_2
        if entity_2 in hash.node_hash:
            e2 = hash.node_hash[entity_2][0]
        else:
            e2 = EntityNode(entity_2)
            hash.node_hash[entity_2] = [e2]
        
        # 添加图边（neighbor关系）
        e1.add_neighbor(e2)
        e2.add_neighbor(e1)
```

### 3. hash.node_hash 的填充

`hash.node_hash` 在构建实体树（forest）时就已经被填充了：

- 在 `trag_tree/tree.py` 的 `EntityTree` 构建过程中，所有节点都会被添加到 `hash.node_hash`
- 这样 Graph RAG 就可以直接复用这些节点，而不需要重新创建

## 总结

### ✅ 使用已构建的实体树

- Graph RAG **复用** `build_forest` 创建的实体树节点
- 通过 `hash.node_hash` 共享节点引用
- **不需要重建**实体树，只需要在已有节点上添加图边（neighbor关系）

### 📝 运行 Graph RAG 的步骤

1. **确保实体树已构建**：
   ```python
   forest, nlp = build.build_forest(...)  # 这一步会填充 hash.node_hash
   ```

2. **构建图结构**：
   ```python
   if search_method == 9:
       build_graph(entities_file_name)  # 复用已有节点，添加图边
   ```

3. **构建ANN索引**（如果需要）：
   ```python
   if search_method in [8, 9]:
       build_ann()  # 构建近似最近邻索引
   ```

## 实际运行示例

### 运行 Graph RAG benchmark

```bash
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key aeslc \
    --entities-file-name aeslc_entities_file \
    --search-method 9 \
    --tree-num-max 50 \
    --node-num-max 2000000 \
    --output ./benchmark/results/aeslc_graph_rag.json \
    --checkpoint ./benchmark/results/aeslc_graph_rag.json \
    --max-samples 30
```

### 执行流程

1. ✅ `build_forest` 构建实体树，填充 `hash.node_hash`
2. ✅ `build_graph` 复用已有节点，构建图结构（添加neighbor关系）
3. ✅ `build_ann` 构建ANN索引（用于加速检索）

## 注意事项

1. **实体文件必须一致**：
   - Graph RAG 和 Tree RAG 使用相同的 `entities_file_name+".csv"` 文件
   - 确保文件存在且格式正确

2. **节点共享**：
   - Graph RAG 和 Tree RAG 共享相同的节点对象（通过 `hash.node_hash`）
   - 这意味着图结构是在树结构的基础上添加的，而不是替换

3. **缓存机制**：
   - 如果实体树已缓存（`entity_forest_cache/`），会直接加载
   - Graph RAG 仍然可以复用缓存中的节点

## 结论

**Graph RAG 不需要重建实体树，它会自动复用已经构建的实体树节点。** 你只需要：

1. 确保实体树已构建（通过 `build_forest`）
2. 使用 `search_method=9` 运行
3. 系统会自动复用已有节点并构建图结构



