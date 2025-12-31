# 架构重新设计计划

## 目标

将架构从：
- **当前**：Forest存储Entity，Abstract在向量数据库，通过文本匹配映射

改为：
- **新架构**：Forest存储Abstract，Cuckoo Filter存储Entity→Abstract地址映射

## 当前架构

```
Cuckoo Filter
  └─→ Entity fingerprint
      └─→ EntityInfo
          └─→ EntityAddr → Forest中的EntityNode（实体）

Forest
  └─→ EntityNode（实体节点）
      ├─→ entity: "心脏病"
      ├─→ parent: EntityNode("疾病")
      └─→ children: [EntityNode("冠心病")]

向量数据库
  └─→ Abstract (tree_node)
      └─→ content, chunk_ids
```

## 新架构设计

```
Cuckoo Filter
  └─→ Entity fingerprint
      └─→ EntityInfo
          └─→ AbstractAddr → Forest中的AbstractNode（摘要）

Forest
  └─→ AbstractNode（摘要节点）
      ├─→ abstract_id/pair_id
      ├─→ content: "两个chunks的合并文本"
      ├─→ chunk_ids: [0, 1]
      ├─→ parent: AbstractNode（更抽象的摘要）
      └─→ children: [AbstractNode（更具体的摘要）]

向量数据库
  └─→ Abstract (tree_node) - 仍然存储，用于向量搜索
  └─→ Chunk (raw_chunk)
```

## 需要修改的文件

1. **创建新类**：
   - `trag_tree/abstract_node.py` - AbstractNode类
   - `trag_tree/abstract_tree.py` - AbstractTree类

2. **修改C++代码**：
   - `TRAG-cuckoofilter/src/node.h` - 添加AbstractNode，修改EntityAddr指向AbstractNode

3. **修改Python代码**：
   - `trag_tree/build.py` - 修改build_forest构建AbstractTree
   - `entity/ruler.py` - 修改查询逻辑
   - `rag_base/build_index.py` - 可能需要调整

4. **需要重新设计**：
   - Abstract之间的层次关系如何建立？（上下层关系）
   - Abstract的父子关系如何定义？

## 关键问题

1. **Abstract的层次关系**：
   - 当前Abstract之间没有明确的层次关系
   - 需要定义：哪些Abstract是父子关系？
   - 可能的方案：基于chunk的顺序或相关性建立层次

2. **兼容性**：
   - 是否保留原有的EntityTree？
   - 还是完全替换？

3. **构建过程**：
   - 何时构建AbstractTree？
   - 如何在构建时建立层次关系？

## 建议的实现步骤

### 阶段1：设计AbstractNode和AbstractTree
### 阶段2：修改Cuckoo Filter存储Abstract地址
### 阶段3：修改查询逻辑
### 阶段4：测试和验证



