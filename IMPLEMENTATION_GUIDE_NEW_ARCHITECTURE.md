# 新架构实现指南

## 架构变更概述

**当前架构**：
- Forest存储Entity（EntityNode）
- Cuckoo Filter存储Entity，EntityAddr指向EntityNode
- Abstract存储在向量数据库中，通过文本匹配找到

**新架构**：
- Forest存储Abstract（AbstractNode）
- Cuckoo Filter存储Entity，EntityAddr指向AbstractNode
- 通过地址直接从Forest获取Abstract

## 实现步骤

### 阶段1：创建Python层面的AbstractNode和AbstractTree ✅

已完成：
- `trag_tree/abstract_node.py` - AbstractNode类
- `trag_tree/abstract_tree.py` - AbstractTree类

### 阶段2：修改C++代码（需要重新编译）

需要修改 `TRAG-cuckoofilter/src/node.h`：

1. **添加AbstractNode类**：
```cpp
class AbstractNode {
private:
    int pair_id;
    std::string content;
    std::vector<int> chunk_ids;
    AbstractNode * parent;
    std::vector<AbstractNode*> children;
    
public:
    AbstractNode(int pair_id, std::string content, std::vector<int> chunk_ids);
    // ... 其他方法
};
```

2. **修改EntityAddr结构**：
```cpp
struct EntityAddr {
    AbstractNode * addr1;  // 改为指向AbstractNode
    AbstractNode * addr2;
    AbstractNode * addr3;
    EntityAddr * next;
};
```

3. **创建AbstractTree类**：
```cpp
class AbstractTree {
private:
    AbstractNode * root;
    std::map<int, AbstractNode*> nodes;
    
public:
    AbstractTree(std::vector<AbstractNode*> nodes);
    AbstractNode* find_node_by_pair_id(int pair_id);
    // ... 其他方法
};
```

### 阶段3：修改Python构建逻辑

需要修改 `trag_tree/build.py`：

1. **创建AbstractTree而不是EntityTree**：
   - 从向量数据库读取所有abstracts（tree_nodes）
   - 为每个abstract创建AbstractNode
   - 构建AbstractTree（建立层次关系）
   - 建立Entity到Abstract的映射

2. **修改Cuckoo Filter构建**：
   - 当Entity出现时，找到包含该Entity的所有Abstracts
   - 将这些Abstract的地址（AbstractNode*）存储在EntityAddr中

### 阶段4：修改查询逻辑

需要修改 `entity/ruler.py` 中的 `search_entity_info_cuckoofilter_enhanced`：

**当前逻辑**：
```python
# Step 2: 从Cuckoo Filter获取entity的层次信息
cuckoo_result = hash.cuckoo_extract(entity_text)

# Step 3-4: 在向量数据库中搜索abstracts
search_results = vec_db.search(...)
# 文本匹配找到abstracts
```

**新逻辑**：
```python
# Step 2: 从Cuckoo Filter获取Abstract地址
cuckoo_result = hash.cuckoo_extract(entity_text)
# cuckoo_result现在返回的是AbstractNode的地址

# Step 3: 直接从Forest中获取Abstract
abstract_nodes = extract_abstract_nodes_from_cuckoo_result(cuckoo_result, forest)
# 不再需要向量数据库搜索和文本匹配！
```

## 关键修改点

### 1. 如何建立Entity到Abstract的映射？

**构建时的映射建立**：

```python
# 在build_forest或新的build_abstract_forest中

# 1. 从向量数据库读取所有abstracts
abstracts = vec_db.get_all_tree_nodes()  # 需要添加这个API

# 2. 为每个abstract创建AbstractNode
abstract_nodes = []
for abstract in abstracts:
    node = AbstractNode(
        pair_id=abstract['pair_id'],
        content=abstract['content'],
        chunk_ids=abstract['chunk_ids']
    )
    abstract_nodes.append(node)

# 3. 构建AbstractTree
abstract_tree = AbstractTree(abstract_nodes)

# 4. 建立Entity到Abstract的映射
entity_abstract_map = {}
for entity in entities:
    entity_abstract_map[entity] = []
    for node in abstract_nodes:
        # 检查entity是否出现在abstract的内容中
        if entity.lower() in node.get_content().lower():
            node.add_entity(entity)
            entity_abstract_map[entity].append(node)

# 5. 将映射存储到Cuckoo Filter
for entity, abstract_nodes in entity_abstract_map.items():
    # 创建EntityInfo和EntityAddr
    # EntityAddr指向这些AbstractNodes
    # 插入到Cuckoo Filter
```

### 2. 如何修改C++代码？

由于C++代码需要重新编译，建议：

1. **方案A**：完全修改C++代码（需要重新编译）
   - 修改node.h添加AbstractNode
   - 修改EntityAddr指向AbstractNode
   - 重新编译cuckoo_filter_module

2. **方案B**：在Python层面做适配（更快，但效率可能略低）
   - 保持C++代码不变（仍然存储EntityNode指针）
   - 在Python中维护一个映射：EntityNode指针 → AbstractNode
   - 查询时先获取EntityNode，再通过映射找到AbstractNode

3. **方案C**：混合方案
   - 先实现Python层面的AbstractNode和AbstractTree
   - 在Python中建立Entity→Abstract映射
   - 暂时使用Python的字典/映射来存储
   - 后续再迁移到C++以提高性能

## 建议的实现顺序

### 第一步：Python层面实现（当前）

1. ✅ 创建AbstractNode和AbstractTree类
2. 修改build_forest创建AbstractTree
3. 修改查询逻辑使用AbstractTree
4. 测试功能是否正常

### 第二步：优化（可选）

如果需要更好的性能，再修改C++代码。

## 需要用户确认的问题

1. **是否保留EntityTree？**
   - 选项A：完全替换为AbstractTree
   - 选项B：同时保留两者（EntityTree用于层次关系，AbstractTree用于存储Abstract）

2. **Abstract的层次关系如何定义？**
   - 当前实现：基于pair_id的顺序
   - 其他选项：基于内容相似度、基于chunk的邻近性等

3. **是否立即修改C++代码？**
   - 建议先完成Python层面的实现和测试
   - 确认功能正确后再优化C++代码

## 下一步行动

1. 修改`build_forest`以构建AbstractTree
2. 修改查询逻辑使用新的架构
3. 测试验证功能



