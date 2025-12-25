# 论文术语替换对照表

本文档提供从"实体（Entity）"到"抽象（Abstract）"的详细术语替换对照，方便在修改论文时查找和替换。

## 一、核心术语替换

### 1.1 基本概念

| 英文原术语 | 中文原术语 | 英文新术语 | 中文新术语 | 使用场景 |
|-----------|----------|-----------|----------|---------|
| Entity | 实体 | Abstract | 抽象 | 核心概念 |
| Entity Tree | 实体树 | Abstract Tree | 抽象树 | 数据结构 |
| Entity Node | 实体节点 | Abstract Node | 抽象节点 | 树节点 |
| Entity Forest | 实体森林 | Abstract Forest | 抽象森林 | 多棵树 |

### 1.2 操作相关术语

| 英文原术语 | 中文原术语 | 英文新术语 | 中文新术语 | 使用场景 |
|-----------|----------|-----------|----------|---------|
| Entity Localization | 实体定位 | Abstract Localization | 抽象定位 | 检索过程 |
| Entity Retrieval | 实体检索 | Abstract Retrieval | 抽象检索 | 检索方法 |
| Entity Extraction | 实体提取 | Abstract Generation / Abstract Construction | 抽象生成 / 抽象构建 | 知识构建 |
| Entity Recognition | 实体识别 | Abstract Identification | 抽象识别 | 识别过程 |
| Entity Matching | 实体匹配 | Abstract Matching | 抽象匹配 | 匹配过程 |

### 1.3 关系和结构术语

| 英文原术语 | 中文原术语 | 英文新术语 | 中文新术语 | 使用场景 |
|-----------|----------|-----------|----------|---------|
| Entity Relationship | 实体关系 | Abstract Relationship | 抽象关系 | 关系描述 |
| Entity Hierarchy | 实体层次结构 | Abstract Hierarchy | 抽象层次结构 | 层次结构 |
| Entity Structure | 实体结构 | Abstract Structure | 抽象结构 | 结构描述 |
| Entity Context | 实体上下文 | Abstract Context | 抽象上下文 | 上下文信息 |

### 1.4 Cuckoo Filter相关术语

| 英文原术语 | 中文原术语 | 英文新术语 | 中文新术语 | 使用场景 |
|-----------|----------|-----------|----------|---------|
| Entity Fingerprint | 实体指纹 | Abstract Fingerprint | 抽象指纹 | Cuckoo Filter存储 |
| Entity Address | 实体地址 | Abstract Address / Chunk Address | 抽象地址 / Chunk地址 | 地址存储 |
| Entity Temperature | 实体温度 | Abstract Temperature | 抽象温度 | 访问频率 |

## 二、句子模式替换

### 2.1 描述层次结构

| 原表述 | 新表述 |
|--------|--------|
| entities are arranged hierarchically | abstracts are arranged hierarchically, where each abstract groups multiple document chunks |
| hierarchical tree structure to organize entities | hierarchical tree structure to organize abstracts, with chunk-to-abstract mapping |
| entities are organized through tree structure | abstracts are organized through tree structure, enabling multi-level semantic retrieval |

### 2.2 描述检索过程

| 原表述 | 新表述 |
|--------|--------|
| retrieve relevant entities | retrieve relevant abstracts and their corresponding chunks |
| locate entities in the hierarchical structure | locate abstracts in the hierarchical structure |
| search for entities in entity trees | search for abstracts in abstract trees |
| entity retrieval process | abstract retrieval process |

### 2.3 描述Cuckoo Filter操作

| 原表述 | 新表述 |
|--------|--------|
| store entity fingerprints | store abstract fingerprints along with chunk addresses |
| query whether an entity exists | query whether an abstract exists |
| entity insertion into Cuckoo Filter | abstract insertion into Cuckoo Filter |
| entity eviction from Cuckoo Filter | abstract eviction from Cuckoo Filter |

### 2.4 描述知识组织

| 原表述 | 新表述 |
|--------|--------|
| organize entities through hierarchical structure | organize knowledge through abstract hierarchy, where multiple chunks map to one abstract |
| entity-based knowledge organization | abstract-based knowledge organization |
| entity knowledge base | abstract-enhanced knowledge base |

## 三、论文标题和摘要替换示例

### 3.1 标题

**原**：
```
CFT-RAG: An Entity Tree Based Retrieval Augmented Generation Algorithm With Cuckoo Filter
```

**新**：
```
CFT-RAG: An Abstract Tree Based Retrieval Augmented Generation Algorithm With Cuckoo Filter
```

或：

```
CFT-RAG: A Hierarchical Abstract-based Retrieval Augmented Generation Algorithm With Cuckoo Filter
```

### 3.2 摘要关键句子替换

| 原句子 | 新句子 |
|--------|--------|
| optimizes entity localization during the retrieval process | optimizes abstract localization during the retrieval process |
| Tree-RAG effectively organizes entities through the introduction of a hierarchical tree structure | Tree-RAG effectively organizes knowledge through hierarchical abstract tree structures, where each abstract corresponds to multiple document chunks |
| Cuckoo Filter stores entity fingerprints | Cuckoo Filter stores abstract fingerprints and maintains chunk-to-abstract mappings |

## 四、算法描述中的术语替换

### 4.1 算法输入输出

| 原表述 | 新表述 |
|--------|--------|
| Input: entity x | Input: abstract x |
| Output: entity addresses | Output: abstract addresses and corresponding chunk addresses |
| entity information | abstract information and related chunk information |

### 4.2 算法步骤描述

| 原表述 | 新表述 |
|--------|--------|
| insert entity x into Cuckoo Filter | insert abstract x into Cuckoo Filter |
| check if entity exists | check if abstract exists |
| retrieve entity context | retrieve abstract context and corresponding chunks |
| entity eviction mechanism | abstract eviction mechanism |

## 五、实验部分术语替换

### 5.1 实验设计描述

| 原表述 | 新表述 |
|--------|--------|
| entity retrieval time | abstract retrieval time |
| entity extraction from queries | abstract identification from queries |
| entity matching accuracy | abstract matching accuracy |
| rare entities | rare / key abstract concepts |

### 5.2 结果描述

| 原表述 | 新表述 |
|--------|--------|
| Retrieved entities: entity1, entity2 | Retrieved abstracts: Abstract_1 (covers chunks about X), Abstract_2 (covers chunks about Y) |
| Entity relations: A - B | Abstract relationships: Abstract_A - Abstract_B, where Abstract_A covers chunks [chunk_ids] |
| entity-based retrieval | abstract-based retrieval |

### 5.3 Use Case描述替换

**原格式**：
```
- Rare Entity: ocular_sympathetic_nerves
- Relation: Horner - ocular sympathetic nerves
```

**新格式**：
```
- Key Abstract: [Abstract containing information about ocular sympathetic nerves]
- Retrieved Abstracts: Abstract_Horner_syndrome (covers 2 chunks about syndrome definition and nerve pathways)
- Abstract Relationship: Abstract_Horner - Abstract_nerve_pathways
```

## 六、代码注释替换（如需要在论文中引用）

| 原注释 | 新注释 |
|--------|--------|
| # Search for entities in the tree | # Search for abstracts in the abstract tree |
| # Entity extraction using SpaCy | # Abstract identification from query |
| # Entity tree construction | # Abstract tree construction with chunk-to-abstract mapping |
| # Entity retrieval using Cuckoo Filter | # Abstract retrieval using Cuckoo Filter |

## 七、特殊情况处理

### 7.1 保留"Entity"的情况

在某些上下文中，"entity"可能指代其他概念，需要根据语境判断：

- 如果指的是"命名实体"（Named Entity），可以保留，但需要说明这不同于论文中的"Abstract"
- 如果指的是代码中的变量名或类名（为了向后兼容），可以在论文中说明这是实现细节

### 7.2 混合使用的情况

在某些描述中，可能需要同时提到实体和抽象：

**示例**：
```
While traditional methods extract named entities (e.g., person names, locations) from text, our approach constructs semantic abstracts that group multiple document chunks, providing richer contextual information than individual entities.
```

### 7.3 Chunk相关术语

由于新方法强调chunk到abstract的映射，需要引入chunk相关术语：

| 术语 | 中文 | 说明 |
|------|------|------|
| Document Chunk | 文档块 | 原始文档片段 |
| Chunk-to-Abstract Mapping | Chunk到抽象的映射 | 描述chunk和abstract的对应关系 |
| Abstract Coverage | 抽象覆盖度 | 抽象覆盖的chunk数量或内容范围 |

## 八、完整句子替换示例

### 示例1：Introduction部分

**原**：
```
Tree-RAG effectively organizes entities through the introduction of a hierarchical tree structure, allowing the retrieval process to more effectively traverse related entities at multiple levels.
```

**新**：
```
Tree-RAG effectively organizes knowledge through hierarchical abstract tree structures, where each abstract node corresponds to multiple document chunks, allowing the retrieval process to more effectively traverse related abstracts at multiple levels and access their corresponding chunks.
```

### 示例2：Methodology部分

**原**：
```
Key entities are then identified from entity trees by applying SpaCy and hierarchical tree searches.
```

**新**：
```
Key semantic concepts are identified from queries and used to locate relevant abstracts in abstract trees through hierarchical tree searches, where each abstract represents a semantic grouping of multiple document chunks.
```

### 示例3：实验描述

**原**：
```
The experiment results of time ratio show that the entity retrieval time accounts for 10% to 72% of the total response time.
```

**新**：
```
The experiment results of time ratio show that the abstract retrieval time accounts for 10% to 72% of the total response time.
```

## 九、检查清单

在完成术语替换后，请检查：

- [ ] 所有方法描述中的"entity"已改为"abstract"
- [ ] 保持了术语的一致性（同一个概念使用同一个术语）
- [ ] 在首次出现新术语时提供了定义或说明
- [ ] Chunk-to-Abstract映射关系得到了清晰说明
- [ ] 代码中的命名（如果需要引用）已说明是为了兼容性
- [ ] 没有误将其他概念的"entity"替换（如Named Entity Recognition中的entity）

## 十、建议的术语使用策略

1. **核心概念**：统一使用"Abstract"
2. **数据结构**：Abstract Tree, Abstract Node
3. **操作**：Abstract Retrieval, Abstract Localization
4. **实现细节**：如果代码中使用Entity命名，在论文中可以说明"为了保持与代码的一致性，实现中使用了Entity命名，但实际表示的是Abstract概念"

---

**使用提示**：
- 在Word中使用"查找和替换"功能时，注意使用"全字匹配"选项，避免误替换
- 建议分批次替换，每次替换一个术语，检查无误后再进行下一个
- 替换后仔细检查上下文，确保语义正确


