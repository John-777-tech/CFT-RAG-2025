# 论文修改指南：从实体对应到抽象对应

本文档提供将CFT-RAG论文从基于**实体（Entity）**的对应关系改为基于**抽象（Abstract）**的对应关系的详细修改建议。

## 一、核心概念转变

### 1.1 术语替换对照表

| 原术语（Entity-based） | 新术语（Abstract-based） | 说明 |
|---------------------|----------------------|------|
| Entity Tree | Abstract Tree | 树结构现在组织的是抽象而不是实体 |
| Entity Node | Abstract Node | 树节点存储抽象信息 |
| Entity Localization | Abstract Localization | 定位抽象而非实体 |
| Entity Retrieval | Abstract Retrieval | 检索抽象信息 |
| Entity Relationship | Abstract Relationship | 抽象之间的关系 |
| Entity Extraction | Abstract Generation | 从文本生成抽象 |

### 1.2 核心概念重新定义

**原来的定义**：
- **实体（Entity）**：从文本中提取的命名实体（如人名、地名、医学概念等）
- **实体树（Entity Tree）**：以实体为节点，实体间关系为边的层次树结构

**新的定义**：
- **抽象（Abstract）**：多个文档chunk的语义摘要，包含更高级的语义信息
- **抽象树（Abstract Tree）**：以抽象为节点，抽象间语义关系为边的层次树结构
- **抽象对应关系**：每两个原始chunk对应一个抽象（tree_node），形成层次化知识组织

## 二、论文各部分修改建议

### 2.1 标题和摘要修改

**原标题**：
```
CFT-RAG: An Entity Tree Based Retrieval Augmented Generation Algorithm With Cuckoo Filter
```

**新标题建议**：
```
CFT-RAG: An Abstract Tree Based Retrieval Augmented Generation Algorithm With Cuckoo Filter
```

或者更具体：
```
CFT-RAG: A Hierarchical Abstract-based Retrieval Augmented Generation Algorithm With Cuckoo Filter
```

**摘要修改要点**：
- 将"实体定位（entity localization）"改为"抽象定位（abstract localization）"
- 将"实体层次结构（hierarchical entity structures）"改为"抽象层次结构（hierarchical abstract structures）"
- 强调抽象的优势：能够捕获文档的语义层次，而不仅仅是实体关系
- 说明每两个chunk对应一个abstract的对应关系

**修改后的摘要片段示例**：
```
Although retrieval-augmented generation(RAG) significantly improves generation quality by retrieving external knowledge bases and integrating generated content, it faces computational efficiency bottlenecks, particularly in knowledge retrieval tasks involving hierarchical structures for Tree-RAG. This paper proposes a Tree-RAG acceleration method based on the improved Cuckoo Filter, which optimizes abstract localization during the retrieval process to achieve significant performance improvements. Tree-RAG effectively organizes knowledge through the introduction of a hierarchical abstract tree structure, where each abstract node corresponds to multiple document chunks, enabling multi-level semantic retrieval. The Cuckoo Filter serves as an efficient data structure that supports rapid membership queries and dynamic updates for abstract-level knowledge...
```

### 2.2 Introduction部分修改

**关键修改点**：

1. **知识库类型描述**：
   - 强调基于抽象的知识库能够更好地组织语义层次信息
   - 说明抽象相比实体的优势：抽象包含更丰富的语义信息，能够连接多个相关的文档片段

2. **Tree-RAG描述**：
   - 将"entities are arranged hierarchically"改为"abstracts are arranged hierarchically"
   - 说明抽象树结构如何维护chunk到abstract的对应关系（每两个chunk对应一个abstract）

3. **问题陈述**：
   - 将"locate and retrieve relevant entities"改为"locate and retrieve relevant abstracts"
   - 强调随着抽象树深度增长，检索效率的挑战

**修改建议片段**：
```
Tree-RAG, an extension of RAG, improves on traditional RAG frameworks by using a hierarchical abstract tree structure to organize the retrieved knowledge. In this structure, multiple document chunks are grouped into abstract nodes, with each abstract corresponding to two consecutive chunks. This hierarchical organization provides richer semantic context and captures complex relationships among abstracts at multiple levels, thus enhancing response accuracy and coherence. However, a critical limitation of Tree-RAG lies in its computational inefficiency: as the datasets and abstract tree depth grow, the time required to locate and retrieve relevant abstracts within the hierarchical structure significantly increases...
```

### 2.3 Methodology部分修改

#### 2.3.1 系统架构描述

**关键修改**：

1. **工作流程描述**（对应Figure 1）：
   - 步骤1：用户查询 → 向量搜索检索相关文档
   - 步骤2：**从查询中识别关键概念，然后从抽象树中定位相关抽象**（而不是"识别实体"）
   - 步骤3：Cuckoo Filter快速过滤和检索抽象信息
   - 步骤4：将检索到的抽象及其对应的chunks整合到prompt中

2. **抽象树的构建**：
   - 说明如何从文档chunks生成抽象
   - 描述chunk到abstract的对应关系（2:1映射）
   - 解释抽象树的层次结构如何反映语义层次

**修改建议**：
```
The workflow of CFT-RAG begins with a user query, which undergoes vector search to retrieve relevant document chunks. Key semantic concepts are then identified from the query and used to locate relevant abstracts in the abstract tree hierarchy. Each abstract node in the tree corresponds to two consecutive document chunks, forming a semantic grouping that captures the relationship between related content. Context information related to these abstracts is retrieved and filtered efficiently by applying the Cuckoo Filter. The retrieved context, including both the abstract-level information and the corresponding document chunks, are integrated into a comprehensive prompt...
```

#### 2.3.2 Cuckoo Filter的应用

**关键修改**：

1. **存储内容**：
   - 原来：存储实体及其地址
   - 现在：存储抽象及其对应的chunk地址
   - 强调抽象指纹（abstract fingerprint）的存储

2. **温度变量（Temperature Variable）**：
   - 说明温度变量记录的是**抽象被访问的频率**，而不是实体被访问的频率
   - 根据抽象访问频率排序，将高频抽象放在bucket前面

3. **块链表（Block Linked List）**：
   - 说明存储的是**抽象在树中不同位置的地址**，以及抽象对应的chunk地址

**修改建议**：
```
The first design introduces a temperature variable, with each abstract stored in the Cuckoo Filter maintaining an additional variable called temperature. This variable records the frequency of the abstract being accessed. The Cuckoo Filter sorts the abstracts according to their access frequency, placing the abstracts with the highest temperature at the front of the bucket, thus speeding up retrieval. The second design introduces a block linked list, where the Cuckoo Filter stores the addresses of abstracts at different locations in the tree, as well as the addresses of the corresponding document chunks...
```

### 2.4 算法描述修改

#### 算法1：抽象插入算法

需要修改的术语：
- `entity x` → `abstract x`
- `entity addresses` → `abstract addresses and corresponding chunk addresses`
- 算法注释中的"实体"全部改为"抽象"

#### 算法2：抽象删除算法

类似的术语替换，说明删除的是抽象及其相关信息。

#### 算法3：抽象驱逐算法

说明驱逐机制处理的是抽象，强调维护抽象到chunk的对应关系。

### 2.5 实验部分修改

#### 实验设计

1. **数据集描述**：
   - 说明如何从原始文本生成抽象
   - 描述抽象树的构建过程

2. **评估指标**：
   - 保持相同的指标（检索时间、时间比率、准确率）
   - 但在描述时强调是"抽象检索"而不是"实体检索"

3. **基线方法比较**：
   - 更新方法名称，明确比较的是抽象检索能力
   - 说明CFT-RAG在抽象检索上的优势

#### 结果分析

**Use Case部分的修改**：

- **1-Hop + Easy Question**：
  - 将"Rare Entity"改为"Rare Abstract"或"Key Abstract Concept"
  - 说明检索到的是相关抽象及其对应的chunks

- **Relation描述**：
  - 原：`Horner - ocular sympathetic nerves`
  - 新：描述为抽象之间的关系，例如：
    ```
    Abstract: [Horner's syndrome concept] - [ocular sympathetic nerves concept]
    Corresponding chunks: [chunk about Horner's syndrome], [chunk about nerve pathways]
    ```

**修改示例**：
```
### A. 1-Hop + Easy Question

- Question: What causes Horner's syndrome?
- Key Answer: Paralysis of ocular sympathetic nerves.
- Key Abstract: [Abstract containing information about Horner's syndrome and nerve pathways]

#### Cuckoo Filter Tree-RAG

| Retrieval Time | Response Time | Time Ratio | Accuracy |
| -------------- | ------------- | ---------- | -------- |
| 4.72s          | 21.54s        | 21.92%     | 66%      |

- Retrieved Abstracts: Abstract_Horner_syndrome (covers 2 chunks about syndrome definition and nerve pathways)
- Question: What causes Horner's syndrome?
- Answer: Horner's syndrome is caused by paralysis of the ocular sympathetic nerves...
```

### 2.6 Related Work部分修改

1. **Tree-RAG相关工作**：
   - 强调基于抽象的Tree-RAG相比基于实体的优势
   - 说明抽象能够更好地捕获语义层次

2. **Cuckoo Filter相关工作**：
   - 保持基本不变，但强调在抽象检索场景中的应用

### 2.7 讨论和结论

**关键修改点**：

1. **贡献总结**：
   - 强调提出的是基于抽象的检索加速方法
   - 说明抽象层次结构的优势

2. **未来工作**：
   - 可以讨论更复杂的抽象生成方法
   - 探讨不同抽象粒度的影响

## 三、代码和实现层面的修改建议

### 3.1 代码注释修改

虽然代码实现可能不需要大改（因为已经支持abstract），但建议更新注释：

1. `entity/ruler.py`：
   - 函数名可以考虑重命名为更通用的名称（如果确实改为抽象检索）
   - 注释更新：说明检索的是抽象而不是实体

2. `trag_tree/tree.py` 和 `trag_tree/node.py`：
   - 类名和变量名保持不变（为了向后兼容），但注释应说明现在用于抽象树
   - 或者在新的抽象树实现中使用新命名

3. `rag_base/rag_complete.py`：
   - `enrich_results_with_summary_embeddings` 函数的注释已经说明了abstract的概念
   - 确保所有相关注释都一致使用"abstract"或"summary"术语

### 3.2 变量和函数命名建议

如果进行代码重构，建议：
- `EntityTree` → `AbstractTree`（可选，保持兼容性）
- `EntityNode` → `AbstractNode`（可选）
- `search_entity_info` → `search_abstract_info`（可选）
- 添加注释说明entity/abstract的对应关系

## 四、图片和图示修改

### Figure 1修改建议

1. **工作流程图**：
   - 将"Key entities"改为"Key abstract concepts"
   - 将"Entity trees"改为"Abstract trees"
   - 说明抽象树中chunk到abstract的映射关系

2. **添加新的图示**：
   - 可以考虑添加一个说明chunk-abstract对应关系的图
   - 展示抽象树的层次结构示例

## 五、关键表述修改清单

### 必须修改的术语

- ✅ Entity → Abstract（在方法描述中）
- ✅ Entity Tree → Abstract Tree
- ✅ Entity Node → Abstract Node
- ✅ Entity Localization → Abstract Localization
- ✅ Entity Retrieval → Abstract Retrieval
- ✅ Entity Extraction → Abstract Generation（或Abstract Construction）

### 需要重新表述的句子类型

1. **描述层次结构时**：
   - ❌ "entities are arranged hierarchically"
   - ✅ "abstracts are arranged hierarchically, where each abstract groups multiple document chunks"

2. **描述检索过程时**：
   - ❌ "retrieve relevant entities"
   - ✅ "retrieve relevant abstracts and their corresponding chunks"

3. **描述Cuckoo Filter时**：
   - ❌ "store entity fingerprints"
   - ✅ "store abstract fingerprints along with chunk addresses"

## 六、实验重新设计的考虑

### 6.1 抽象生成方法

需要在论文中说明：
1. 如何从文档chunks生成抽象
2. 当前实现：两个连续chunk合并为一个abstract
3. 是否使用LLM生成抽象，还是简单的文本合并

### 6.2 抽象质量评估

可以考虑添加：
1. 抽象覆盖度（abstract coverage）：抽象是否很好地涵盖了对应chunks的内容
2. 抽象相关性（abstract relevance）：检索到的抽象与查询的相关性

### 6.3 基线方法更新

确保所有基线方法都基于抽象检索进行评估，保持公平比较。

## 七、论文结构建议

建议在Introduction后、Methodology前添加一个小节：

**2. Abstract-based Knowledge Organization**
- 解释什么是抽象（Abstract）
- 说明chunk到abstract的对应关系
- 对比基于实体和基于抽象的组织方式的区别
- 说明抽象树的构建方法

## 八、常见问题解答（FAQ）

### Q1: 抽象和实体有什么区别？
**A**: 实体是从文本中提取的命名实体（如人名、地名），而抽象是对多个文档chunks的语义摘要，包含更丰富的语义信息。

### Q2: 为什么选择2:1的chunk-abstract映射？
**A**: 这是一个平衡语义覆盖和检索效率的选择。可以 experimentation不同的映射比例。

### Q3: 抽象是如何生成的？
**A**: 当前实现将两个连续chunk合并为一个abstract。未来可以考虑使用LLM生成更高质量的抽象。

## 九、检查清单

在提交前，请检查：

- [ ] 所有"entity"相关的术语都已改为"abstract"（在方法描述中）
- [ ] 工作流程图已更新
- [ ] 算法描述中的术语已更新
- [ ] 实验部分强调抽象检索
- [ ] 结果分析中使用抽象的表述
- [ ] 代码注释（如果包含）已更新
- [ ] 摘要准确反映了基于抽象的创新点
- [ ] 引言清楚地说明了从实体到抽象的转变动机

## 十、参考文献更新

检查是否有需要引用的关于抽象生成或语义层次组织的最新工作。

---

**注意**：这个修改指南基于当前代码实现和对PDF论文内容的理解。建议根据实际研究重点和审稿意见进行适当调整。


