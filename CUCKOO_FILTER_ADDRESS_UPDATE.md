# Cuckoo Filter地址映射更新说明

## 修改内容

将Cuckoo Filter中块状链表（EntityAddr）存储的地址从**EntityNode地址**改为**AbstractNode地址**。

## 原来的架构

```
Entity (在Cuckoo Filter中)
  ↓
EntityInfo
  ↓
EntityAddr (块状链表)
  ├─→ addr1: EntityNode* (在不同树中的实体节点地址)
  ├─→ addr2: EntityNode* 
  ├─→ addr3: EntityNode*
  └─→ next: EntityAddr*
```

## 新的架构

```
Entity (在Cuckoo Filter中)
  ↓
EntityInfo
  ↓
EntityAddr (块状链表) - 现在存储AbstractNode地址
  ├─→ addr1: AbstractNode* (在不同树中对应的摘要节点地址)
  ├─→ addr2: AbstractNode*
  ├─→ addr3: AbstractNode*
  └─→ next: EntityAddr*
```

## 实现方式

### 在Python层面的实现

由于C++代码的类型系统限制（EntityAddr存储的是EntityNode*），我们在Python层面创建了一个映射来替代C++中的地址存储：

```python
entity_abstract_address_map = {
    "entity1": [AbstractNode1, AbstractNode2, ...],  # 该entity对应的Abstract地址列表
    "entity2": [AbstractNode3, AbstractNode4, ...],
    ...
}
```

这个映射的作用相当于原来C++中：
- `EntityInfo -> EntityAddr -> EntityNode地址`
- 现在改为：`EntityInfo -> EntityAddr -> AbstractNode地址`（在Python层面实现）

## 代码修改

### 1. 新增函数 (`trag_tree/update_cuckoo_with_abstracts.py`)

- `update_cuckoo_filter_with_abstract_addresses()` - 创建Entity到Abstract地址的映射
- `get_abstracts_for_entity_from_cuckoo()` - 从映射中获取Abstract地址（相当于原来的Extract）

### 2. 修改构建流程 (`trag_tree/build.py`)

在 `build_abstract_forest_and_entity_mapping()` 中：
```python
# Step 5: 更新Cuckoo Filter的地址映射
entity_abstract_address_map = update_cuckoo_filter_with_abstract_addresses(
    entity_to_abstract_map, abstract_tree
)
```

### 3. 修改查询流程

查询时，优先使用 `entity_abstract_address_map`（从Cuckoo Filter地址映射获取）：
```python
# 优先使用entity_abstract_address_map（从Cuckoo Filter地址映射）
mapping_source = entity_abstract_address_map if entity_abstract_address_map else entity_to_abstract_map

for entity_text in found_entities:
    if mapping_source and entity_text in mapping_source:
        abstract_nodes = mapping_source[entity_text]  # 直接获取Abstract地址
        # 这些就是原来EntityAddr中存储的地址，但现在指向AbstractNode
```

## 工作流程

### 构建阶段

```
1. 从向量数据库读取所有abstracts
   ↓
2. 创建AbstractNode
   ↓
3. 构建AbstractTree
   ↓
4. 建立Entity到Abstract的映射（entity_to_abstract_map）
   ↓
5. 创建Entity到Abstract地址的映射（entity_abstract_address_map）
   ↑
   这就是Cuckoo Filter中应该存储的地址！
```

### 查询阶段

```
1. 实体识别
   ↓
2. 从entity_abstract_address_map获取Abstract地址（相当于原来的Extract）
   ↓
3. 这些地址指向AbstractNode，而不是EntityNode
   ↓
4. 从AbstractNode获取摘要信息和层次关系
   ↓
5. 获取chunks并组合context
```

## 关键改变

### 原来的逻辑：
```python
# C++中：EntityAddr存储EntityNode地址
EntityNode* addr1 = ...;  # 实体节点地址
EntityNode* addr2 = ...;
# 查询时使用EntityNode.get_context()获取层次关系
```

### 新的逻辑：
```python
# Python中：entity_abstract_address_map存储AbstractNode地址
AbstractNode addr1 = ...;  # 摘要节点地址
AbstractNode addr2 = ...;
# 查询时使用AbstractNode.get_content()和层次关系获取摘要信息
```

## 优势

1. **更直接的映射**：Entity直接对应到Abstract，而不是通过Entity再找Abstract
2. **更快的查询**：无需额外的文本匹配步骤
3. **更清晰的语义**：地址直接指向摘要，符合新架构的设计意图

## 注意事项

1. **C++代码未修改**：由于类型系统限制，在Python层面实现了映射
2. **向后兼容**：如果没有提供`entity_abstract_address_map`，会回退到使用`entity_to_abstract_map`
3. **性能考虑**：Python层面的映射可能比C++实现稍慢，但提供了灵活性

## 未来优化（可选）

如果要完全在C++层面实现，需要：
1. 修改`TRAG-cuckoofilter/src/node.h`，将EntityAddr中的`EntityNode*`改为`AbstractNode*`
2. 修改EntityNode的构造函数，不再自动注册到addr_map
3. 在Python构建AbstractTree后，将AbstractNode地址写入C++的addr_map
4. 重新编译C++模块

目前Python层面的实现已经满足了功能需求。



