# 代码结构澄清和图的修改建议

## 当前代码的实际结构

### 1. Chunks（原始数据）
- **来源**：从数据集构建（如MedQA、DART、TriviaQA）
- **存储**：向量数据库（VecDB）中，类型为 `raw_chunk`
- **标识**：每个chunk有唯一的 `chunk_id`（0, 1, 2, 3, ...）
- **特点**：这是最底层的原始文本块

### 2. Abstracts（Tree Nodes）
- **创建规则**：**每两个连续的chunks共享一个abstract**
  - chunk 0 和 chunk 1 → pair_id = 0 的 abstract
  - chunk 2 和 chunk 3 → pair_id = 1 的 abstract
  - chunk 4 和 chunk 5 → pair_id = 2 的 abstract
  - ...
- **计算方式**：`pair_id = chunk_id // 2`
- **存储**：向量数据库中，类型为 `tree_node`
- **内容**：对应两个chunks的合并文本
- **标识**：`pair_id` 和 `chunk_ids`（包含2个chunk_id）

### 3. Entities（实体）
- **识别方式**：通过Spacy NLP从query中提取
- **存储方式1**：Cuckoo Filter中（用于快速查找）
- **存储方式2**：EntityTree/Forest中（用于层次关系）
- **关联方式**：通过查找abstracts（tree_nodes）中包含该entity的内容

## 映射关系

```
Entity
  ↓ (通过查找abstract中包含entity)
Abstract(s) (可能有多个abstracts包含同一个entity)
  ↓ (通过abstract的chunk_ids)
Chunk(s) (每个abstract对应2个chunks)
```

## 图的修改建议

基于你提供的图，需要做以下修改：

### 修改1：澄清Chunk和Abstract的关系

**当前图中的问题**：
- 图显示"每个item对应多个blocks"，但实际代码是"每两个chunks对应一个abstract"

**应该修改为**：
- **Bucket中的Item**应该表示**Abstract（tree_node）**
- 每个Item（Abstract）应该链接到**2个Chunks**（而不是3个blocks）
- Blocks中的"Addr1, Addr2, Addr3"应该改为"Addr1, Addr2"（对应2个chunks）

### 修改2：Forest部分表示Entity关系

**当前图已经正确**：
- Forest部分表示Entity的层次关系（父子关系）
- 这对应于代码中的`EntityTree`结构

**需要澄清**：
- Forest中的节点是**Entity节点**（不是Abstract）
- Entity节点通过`EntityAddr`链接到Abstracts
- 每个Entity可能有多个Abstracts（因为一个entity可能出现在多个abstracts中）

### 修改3：数据流方向

**检索流程**：
1. **Query → Entity识别**（Spacy NLP）
2. **Entity → Cuckoo Filter查找**（快速定位entity）
3. **Entity → 查找包含该entity的Abstracts**（在vector DB中搜索tree_nodes）
4. **Abstract → 获取对应的Chunks**（通过chunk_ids，每个abstract对应2个chunks）
5. **Entity → Forest遍历**（获取层次关系，parent/child entities）

## 修改后的图结构建议

### 第一部分：Entities（保持不变）
- 实体集合
- 使用h₁(x)和h₂(x)哈希函数定位到Bucket

### 第二部分：Single Table和Bucket（修改）
- **Bucket中的Item现在表示Abstract（tree_node）**
- 每个Item有：
  - `pair_id`（标识abstract）
  - `temperature`（使用频率）
  - `chunk_ids`（包含2个chunk_id）
  - `content`（两个chunks的合并文本）

### 第三部分：Block Linked List（修改）
- **每个Block现在有2个地址（Addr1, Addr2）**，对应2个chunks
- **不再是3个地址**
- Addr1和Addr2指向Chunk存储位置

### 第四部分：Chunk存储（新增）
- **直接存储原始chunks**（从数据集构建）
- 每个chunk有：
  - `chunk_id`
  - `content`（原始文本）
  - `embedding`（向量表示）

### 第五部分：Forest（保持，但需澄清）
- 表示**Entity之间的层次关系**
- Entity节点通过EntityAddr链接到多个Abstracts
- 可以通过层次遍历（向上/向下）找到相关entities

## 数据流示意

```
Query
  ↓ (Spacy NLP)
Entities [x, y, z]
  ↓ (Cuckoo Filter: h₁(x), h₂(x))
Bucket [找到包含entity的items]
  ↓ (Item = Abstract, 通过chunk_ids)
Block Linked List [Addr1 → Chunk₁, Addr2 → Chunk₂]
  ↓ (获取原始chunks)
Chunks [chunk_id=0, chunk_id=1]
  ↓ (同时)
Forest [遍历entity的层次关系]
  → Parent entities
  → Child entities
  → 这些entities也链接到各自的Abstracts → Chunks
```

## 关键修改点总结

1. ✅ **Bucket中的Item = Abstract（tree_node）**，不是chunk
2. ✅ **每个Abstract对应2个Chunks**（不是3个blocks）
3. ✅ **Block Linked List中的地址数 = 2**（Addr1, Addr2）
4. ✅ **Chunks是独立的存储层**（从数据集直接构建）
5. ✅ **Forest表示Entity层次关系**（通过EntityAddr链接到Abstracts）



