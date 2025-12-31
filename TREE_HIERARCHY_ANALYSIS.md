# AbstractTree层次结构问题分析

## 问题发现

### 1. 使用了Simple Hierarchy Strategy而不是LLM

**发现：**
- 构建AbstractTree时，如果没有API key，系统会使用`_build_hierarchy_simple`策略
- 输出显示：`Warning: No API key found, using simple hierarchy strategy`

**Simple策略的实现（abstract_tree.py 第43-74行）：**
```python
def _build_hierarchy_simple(self, nodes: List[AbstractNode]):
    """简单策略：基于pair_id的顺序建立层次"""
    # 第一个abstract作为root
    self.root = nodes[0]
    
    # 按照pair_id排序
    sorted_nodes = sorted(nodes, key=lambda x: x.pair_id)
    
    # 构建层次关系：每4个abstracts形成一个层次
    level_size = 4
    parent_idx = (idx - 1) // level_size  # 父节点选择
```

**问题：**
- 层次关系完全基于`pair_id`的顺序，而不是内容的语义关系
- 例如：Abstract5的父节点可能是Abstract0，但它们可能完全不相关
- 父节点和子节点之间没有语义联系，只是数字上的分组

### 2. Depth=2追溯父节点时引入了噪音

**当前追溯逻辑（rag_complete.py 第478-489行）：**
```python
for pair_id in selected_pair_ids:
    for tree in abstract_forest:
        node = tree.find_node_by_pair_id(pair_id)
        if node:
            parent = node.get_parent()
            if parent:
                expanded_pair_ids.add(parent.pair_id)  # 直接添加父节点
```

**问题：**
1. **父节点可能完全不相关**：因为层次关系是基于顺序，不是语义
2. **没有相似度过滤**：直接添加父节点，不检查其内容是否与query相关
3. **引入噪音**：父节点的abstract可能包含不相关信息，导致检索质量下降

### 3. 理论 vs 实际

**理论上：**
- 父节点应该是对子节点的概括，包含更抽象的信息
- 追溯父节点应该能提供更广泛的上下文

**实际上：**
- Simple策略建立的层次关系没有语义基础
- 父节点可能只是数字上的分组，内容完全不相关
- 追溯父节点引入了噪音，导致评估分数下降（MedQA下降90%+，DART下降34-60%）

## 建树方式确认

**当前实现（build.py 第172-244行）：**
1. 按`source_file`字段分组abstracts
2. 每个文件构建一个AbstractTree
3. 所有AbstractTree组成AbstractForest（Forest = [Tree1, Tree2, ...]）

**发现：**
- DART数据集只有1个Tree（所有abstracts在一个'default'文件中）
- MedQA和TriviaQA可能也有类似情况

## 解决方案

### 方案1: 使用LLM建立层次关系（推荐）

**步骤：**
1. 设置API key：`export ARK_API_KEY=xxx` 或 `export OPENAI_API_KEY=xxx`
2. 重新构建AbstractTree，使用LLM建立语义相关的层次关系
3. 这样追溯父节点时，父节点和子节点之间会有语义联系

**优点：**
- 层次关系基于语义，更合理
- 父节点真正是对子节点的概括
- 追溯父节点可能提供有价值的上下文

**缺点：**
- 需要API key和额外的API调用成本
- 对于大量abstracts，可能需要优化prompt

### 方案2: 改进追溯逻辑，添加相似度过滤

**步骤：**
1. 不直接添加父节点
2. 计算父节点的abstract内容与query的相似度
3. 只添加相似度超过阈值的父节点

**优点：**
- 不需要重新建树
- 可以过滤掉不相关的父节点

**缺点：**
- 仍然可能遗漏有价值的父节点（如果simple策略建立的层次不合理）
- 需要额外的相似度计算

### 方案3: 追溯子节点而不是父节点

**步骤：**
1. 修改追溯逻辑，获取子节点而不是父节点
2. 子节点可能更具体，内容更相关

**优点：**
- 子节点通常是对父节点的细化，可能更相关

**缺点：**
- 如果simple策略建立的层次不合理，子节点也可能不相关
- 可能无法提供更广泛的上下文

### 方案4: 同时追溯父节点和子节点，但都经过相似度过滤

**步骤：**
1. 获取父节点和所有子节点
2. 计算它们与query的相似度
3. 只添加相似度超过阈值的节点

**优点：**
- 结合了父节点（上下文）和子节点（细节）
- 通过相似度过滤，避免引入噪音

**缺点：**
- 需要更多的相似度计算
- 可能增加检索时间

## 建议

**立即行动：**
1. **检查是否有API key设置**：`echo $ARK_API_KEY` 或 `echo $OPENAI_API_KEY`
2. **如果有API key，重新构建AbstractTree**：使用LLM建立层次关系
3. **如果没有API key，使用方案2或4**：添加相似度过滤，避免引入噪音

**长期优化：**
1. 使用LLM建立层次关系（方案1）
2. 在追溯时添加相似度过滤（方案2或4）
3. 考虑同时追溯父节点和子节点，但都经过过滤

