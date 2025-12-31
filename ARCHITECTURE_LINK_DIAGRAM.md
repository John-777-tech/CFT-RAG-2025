# 当前架构链接关系图

## 架构组件链接关系

### 1. Entity ↔ Chunk 链接关系

**关系**：**间接链接，通过Abstract连接**

```
Entity (实体)
    ↓ (文本匹配)
Abstract (摘要，pair_id)
    ↓ (chunk_ids字段)
Chunk (原文段落)
```

**实现方式**：
- Entity → Abstract: 通过文本匹配（`entity_lower in content_lower`）
  - 代码位置：`trag_tree/build.py:218-223`
  - 如果Abstract的内容中包含Entity名称，则建立映射
- Abstract → Chunk: 通过`chunk_ids`字段
  - 每个AbstractNode包含`chunk_ids: List[int]`
  - 通常每个Abstract对应2个chunks（pair_id = chunk_id // 2）

**注意**：Entity和Chunk之间**没有直接链接**，必须通过Abstract。

### 2. Chunk ↔ Abstract Tree 链接关系

**关系**：**直接链接，通过AbstractNode**

```
Chunk (原文段落，chunk_id)
    ↓ (通过pair_id = chunk_id // 2)
AbstractNode (摘要节点，pair_id)
    ↓ (父子关系)
AbstractTree (摘要树)
```

**实现方式**：
- Chunk → AbstractNode: 
  - 通过`pair_id = chunk_id // 2`计算
  - AbstractNode存储`chunk_ids: List[int]`
- AbstractNode → AbstractTree:
  - AbstractTree包含所有AbstractNode
  - AbstractNode之间有parent/children关系，形成树结构

**代码位置**：
- `trag_tree/abstract_node.py`: AbstractNode类定义
- `trag_tree/abstract_tree.py`: AbstractTree类定义
- `trag_tree/build.py:195-200`: 创建AbstractNode时设置chunk_ids

### 3. Abstract ↔ Cuckoo Filter 哈希对应关系

**关系**：**通过Entity间接对应，存储abstract_pair_id**

```
Entity (实体名称)
    ↓ (哈希到Cuckoo Filter)
Cuckoo Filter (Single Table + Buckets)
    ↓ (EntityInfo -> EntityAddr)
abstract_pair_id (Abstract的pair_id)
    ↓ (通过pair_id查找)
AbstractNode (在AbstractTree中)
```

**实现方式**：
- Entity → Cuckoo Filter:
  - Entity名称通过`EntityStruct`哈希到Cuckoo Filter
  - 存储在Single Table的Buckets中
  - 每个Bucket包含fingerprint和EntityInfo指针
- Cuckoo Filter → Abstract:
  - EntityInfo包含EntityAddr链表
  - EntityAddr存储`abstract_pair_id1/2/3`（Abstract的pair_id）
  - 通过`set_entity_abstract_addresses()`设置
- Abstract pair_id → AbstractNode:
  - 在Python层面，通过pair_id在AbstractTree中查找对应的AbstractNode

**代码位置**：
- `TRAG-cuckoofilter/src/node.h:44-58`: EntityAddr结构定义
- `TRAG-cuckoofilter/cuckoo_bind.cpp:16-57`: set_entity_abstract_addresses函数
- `trag_tree/set_cuckoo_abstract_addresses.py:60-83`: 批量更新Cuckoo Filter

## 完整数据流

### 构建阶段

```
1. 从向量数据库读取Abstracts
   ↓
2. 创建AbstractNode（包含pair_id, content, chunk_ids）
   ↓
3. 构建AbstractTree（建立父子关系）
   ↓
4. 建立Entity → Abstract映射（文本匹配）
   ↓
5. 更新Cuckoo Filter：Entity → abstract_pair_id
   (调用set_entity_abstract_addresses)
```

### 查询阶段

```
1. Query → 实体识别（Spacy NLP）
   ↓
2. Entity → Cuckoo Filter查找
   (cuckoo_extract返回abstract_pair_id列表)
   ↓
3. abstract_pair_id → AbstractTree查找AbstractNode
   ↓
4. AbstractNode → 获取content和chunk_ids
   ↓
5. chunk_ids → 从向量数据库获取原始Chunks
   ↓
6. 返回：Abstract内容 + 原始Chunks + 层次关系
```

## 关键数据结构

### EntityAddr (C++)

```cpp
struct EntityAddr {
    int abstract_pair_id1;  // Abstract的pair_id
    int abstract_pair_id2;
    int abstract_pair_id3;
    EntityAddr * next;
    // ... (向后兼容字段)
};
```

### AbstractNode (Python)

```python
class AbstractNode:
    def __init__(self, pair_id: int, content: str, chunk_ids: List[int]):
        self.pair_id = pair_id
        self.content = content
        self.chunk_ids = chunk_ids  # 链接到Chunks
        self.parent: Optional['AbstractNode'] = None
        self.children: List['AbstractNode'] = []
        self.entities: List[str] = []  # 反向索引：包含的Entities
```

### entity_to_abstract_map (Python)

```python
# dict: {entity_name: [AbstractNode, ...]}
entity_to_abstract_map = {
    "心脏病": [AbstractNode(pair_id=0), AbstractNode(pair_id=5)],
    "高血压": [AbstractNode(pair_id=1), AbstractNode(pair_id=3)],
    ...
}
```

## 总结

**链接关系**：
1. ✅ **Entity ↔ Chunk**: 间接链接，通过Abstract
2. ✅ **Chunk ↔ Abstract Tree**: 直接链接，通过AbstractNode的chunk_ids字段
3. ✅ **Abstract ↔ Cuckoo Filter**: 通过Entity间接对应，Cuckoo Filter存储abstract_pair_id

**关键点**：
- Entity和Chunk之间**没有直接链接**
- Abstract是中间层，连接Entity和Chunk
- Cuckoo Filter存储的是Entity到Abstract的映射（pair_id），而不是直接存储Abstract内容
- AbstractTree在Python层面维护，Cuckoo Filter在C++层面维护



