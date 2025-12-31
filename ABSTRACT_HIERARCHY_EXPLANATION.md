# AbstractTree 层次关系与上下层级追溯详解

## 1. 什么是 AbstractTree 的层次结构？

### 1.1 基本概念

- **AbstractNode（摘要节点）**：代表一个abstract，每2个chunks对应1个abstract
- **层次关系**：AbstractNode之间有父子关系，形成树状结构
- **Forest（森林）**：多个AbstractTree组成，每个文件对应一个AbstractTree

### 1.2 层次结构示例

```
AbstractTree（一个文件的所有abstracts）
│
└── Root (Abstract0: "心血管疾病的概述")
    ├── Abstract1 (Abstract0的子节点: "心脏病的基础知识")
    │   ├── Abstract5 (Abstract1的子节点: "心肌梗死的诊断")
    │   └── Abstract6 (Abstract1的子节点: "心绞痛的分类")
    ├── Abstract2 (Abstract0的子节点: "高血压的治疗")
    │   ├── Abstract7 (Abstract2的子节点: "药物治疗方案")
    │   └── Abstract8 (Abstract2的子节点: "生活方式干预")
    └── Abstract3 (Abstract0的子节点: "心律失常")
```

## 2. 层次关系是如何建立的？

### 2.1 方式1: LLM建立（默认方式）

**流程：**
1. 将所有abstracts的内容发送给LLM
2. LLM分析所有abstracts的语义关系
3. LLM返回父子关系，例如：
   ```
   Abstract0 -> root
   Abstract1 -> Abstract0
   Abstract2 -> Abstract0
   Abstract5 -> Abstract1
   Abstract6 -> Abstract1
   ```
4. 解析LLM返回的结果，建立父子关系

**优点：**
- 根据语义关系建立，更加合理
- 能够理解abstract之间的抽象-具体关系

**缺点：**
- 需要调用LLM API，有成本
- 可能不够稳定

### 2.2 方式2: 简单策略（fallback）

**流程：**
- 第一个abstract作为root
- 每4个abstracts形成一个层次
- 例如：0是root，1-4是level1，5-8是level2...

**优点：**
- 快速，不需要LLM

**缺点：**
- 层次关系可能不合理
- 没有考虑语义关系

## 3. 上下层级追溯的工作原理

### 3.1 向上追溯（get_ancestors()）

**代码实现：**
```python
def get_ancestors(self) -> List['AbstractNode']:
    """获取所有祖先节点"""
    ancestors = []
    ancestor = self.parent
    while ancestor is not None:
        ancestors.append(ancestor)
        ancestor = ancestor.parent
    return ancestors
```

**示例：**
```
假设层次结构：
Abstract0 (root)
└── Abstract1
    └── Abstract5

Abstract5.get_ancestors() 的追溯过程：
1. ancestor = Abstract5.parent → Abstract1
2. ancestors.append(Abstract1)
3. ancestor = Abstract1.parent → Abstract0
4. ancestors.append(Abstract0)
5. ancestor = Abstract0.parent → None
6. 返回 [Abstract1, Abstract0]
```

**可视化：**
```
Abstract5 向上追溯：
Abstract5 → Abstract1 → Abstract0 → None
          ↑         ↑
      ancestors[0]  ancestors[1]
```

### 3.2 向下追溯（get_all_descendants()）

**代码实现：**
```python
def get_all_descendants(self) -> List['AbstractNode']:
    """递归获取所有后代节点"""
    descendants = []
    for child in self.children:
        descendants.append(child)
        descendants.extend(child.get_all_descendants())  # 递归
    return descendants
```

**示例：**
```
假设层次结构：
Abstract1
├── Abstract5
│   ├── Abstract9
│   └── Abstract10
└── Abstract6

Abstract1.get_all_descendants() 的追溯过程：
1. 遍历children: [Abstract5, Abstract6]
2. descendants.append(Abstract5)
3. 递归调用 Abstract5.get_all_descendants()
   - descendants.append(Abstract9)
   - descendants.append(Abstract10)
4. descendants.append(Abstract6)
5. 返回 [Abstract5, Abstract9, Abstract10, Abstract6]
```

**可视化：**
```
Abstract1 向下追溯：
Abstract1
├── Abstract5 (direct child)
│   ├── Abstract9 (descendant)
│   └── Abstract10 (descendant)
└── Abstract6 (direct child)

所有后代：Abstract5, Abstract9, Abstract10, Abstract6
```

## 4. Depth=1 vs Depth=2 应该如何使用？

### 4.1 理想实现：Depth=1

**逻辑：**
```
查询找到的abstracts: [Abstract5, Abstract8]
返回的abstracts: [Abstract5, Abstract8]  # 只返回直接匹配的
```

**代码示例：**
```python
# 当前代码的行为（depth=1应该这样）
selected_pair_ids = {5, 8}  # 直接匹配的abstracts
abstract_contents = [get_abstract_content(pid) for pid in selected_pair_ids]
```

### 4.2 理想实现：Depth=2

**逻辑（向上追溯）：**
```
查询找到的abstracts: [Abstract5, Abstract8]

Depth=2（向上追溯1层）：
1. Abstract5 → 获取其父节点 Abstract1
2. Abstract8 → 获取其父节点 Abstract2
3. 返回的abstracts: [Abstract5, Abstract8, Abstract1, Abstract2]
```

**代码示例（应该这样实现但没实现）：**
```python
selected_pair_ids = {5, 8}
expanded_pair_ids = set(selected_pair_ids)

# 如果depth=2，向上追溯1层
if max_hierarchy_depth == 2:
    for pair_id in selected_pair_ids:
        # 在AbstractForest中找到对应的AbstractNode
        node = find_node_in_forest(pair_id)
        if node and node.get_parent():
            expanded_pair_ids.add(node.get_parent().pair_id)

abstract_contents = [get_abstract_content(pid) for pid in expanded_pair_ids]
```

**逻辑（向下追溯，另一种可能）：**
```
查询找到的abstracts: [Abstract1]

Depth=2（向下追溯1层）：
1. Abstract1 → 获取其子节点 [Abstract5, Abstract6]
2. 返回的abstracts: [Abstract1, Abstract5, Abstract6]
```

## 5. 当前代码的问题

### 5.1 问题1: 没有使用AbstractForest

**当前代码（rag_complete.py 第466-493行）：**
```python
# 直接从向量数据库提取，通过pair_id匹配
all_data_abstracts = db.extract_data(table_name)
for vec_data, metadata in all_data_abstracts:
    result = dict(metadata)
    if result.get("type") == "tree_node":
        pair_id = int(result.get("pair_id", ""))
        if pair_id in selected_pair_ids:  # 只匹配pair_id
            abstract_contents.append(result.get("content"))
```

**问题：**
- 没有从AbstractForest中查找AbstractNode
- 无法调用`get_ancestors()`或`get_descendants()`
- `max_hierarchy_depth`参数完全没有使用

### 5.2 问题2: Depth=1和Depth=2行为完全相同

**当前行为：**
- Depth=1: 只返回直接匹配的abstracts
- Depth=2: **也是**只返回直接匹配的abstracts（因为没实现扩展逻辑）

**应该的行为：**
- Depth=1: 只返回直接匹配的abstracts ✓（正确）
- Depth=2: 返回直接匹配的 + 父节点的abstracts ✗（未实现）

## 6. 为什么Depth=2可能表现更差？

如果正确实现了Depth=2，可能的问题：

### 6.1 引入噪音
```
查询: "心肌梗死的症状"
匹配到: Abstract5 ("心肌梗死的诊断")

Depth=1: 返回 Abstract5 ✓ 精确相关
Depth=2: 返回 Abstract5 + Abstract1 ("心脏病的基础知识") 
         → Abstract1可能包含太多不相关信息
```

### 6.2 层次关系可能不合理
- LLM建立的层次关系可能不够准确
- 父节点的内容可能并不比子节点更相关

### 6.3 信息冗余
- 父节点内容可能是对子节点的概括
- 增加的信息量有限，但可能带来噪音

## 7. 如何修复代码以实现Depth=2？

需要在`rag_complete.py`的`augment_prompt`函数中：

1. **访问AbstractForest**：
   ```python
   # 从模块级变量获取
   from rag_base import rag_complete as rag_module
   abstract_forest = rag_module._abstract_forest
   ```

2. **根据depth扩展pair_ids**：
   ```python
   expanded_pair_ids = set(selected_pair_ids)
   if max_hierarchy_depth == 2:
       for tree in abstract_forest:
           for pair_id in selected_pair_ids:
               node = tree.find_node_by_pair_id(pair_id)
               if node and node.get_parent():
                   expanded_pair_ids.add(node.get_parent().pair_id)
   ```

3. **使用扩展后的pair_ids**：
   ```python
   abstract_contents = [get_abstract_content(pid) for pid in expanded_pair_ids]
   ```

## 8. 总结

1. **层次关系已建立**：AbstractTree通过LLM或简单策略建立了父子关系 ✓
2. **追溯方法已实现**：`get_ancestors()`和`get_descendants()`可以正常工作 ✓
3. **查询时未使用**：检索代码没有利用这些层次关系 ✗
4. **Depth参数未生效**：`max_hierarchy_depth`参数被传递但没有实际作用 ✗
5. **Depth=2表现差的原因**：可能因为没有正确实现，或者实现后引入了噪音

