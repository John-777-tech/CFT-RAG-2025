# 论文修改快速指南

## 核心转变

**从**：基于实体（Entity）的树结构 → **到**：基于抽象（Abstract）的树结构

**关键区别**：
- **实体（Entity）**：从文本提取的命名实体（人名、地名等）
- **抽象（Abstract）**：多个文档chunk的语义摘要，每2个chunk对应1个abstract

## 必须修改的核心术语

1. **Entity → Abstract**（在所有方法描述中）
2. **Entity Tree → Abstract Tree**
3. **Entity Node → Abstract Node**
4. **Entity Retrieval → Abstract Retrieval**
5. **Entity Localization → Abstract Localization**

## 论文各部分修改重点

### 1. 标题
```
原：CFT-RAG: An Entity Tree Based...
新：CFT-RAG: An Abstract Tree Based...
```

### 2. 摘要
- 将"entity localization"改为"abstract localization"
- 强调abstract包含更丰富的语义信息
- 说明chunk-to-abstract的对应关系（2:1映射）

### 3. Introduction
- 重新定义Tree-RAG：使用抽象树组织知识
- 说明abstract相比entity的优势
- 问题陈述：抽象检索的效率挑战

### 4. Methodology
- **工作流程**：识别关键抽象概念 → 从抽象树检索
- **Cuckoo Filter**：存储抽象指纹和chunk地址
- **温度变量**：记录抽象访问频率
- **块链表**：存储抽象地址和对应chunk地址

### 5. 算法
- 算法1：抽象插入（而非实体插入）
- 算法2：抽象删除
- 算法3：抽象驱逐

### 6. 实验
- **评估指标**：强调"抽象检索时间"
- **Use Cases**：
  - "Rare Entity" → "Key Abstract"
  - "Relation: A - B" → "Abstract Relationship: Abstract_A - Abstract_B"
  - 说明检索到的abstract对应的chunks

## 关键句子模板替换

### 描述层次结构
```
原：entities are arranged hierarchically
新：abstracts are arranged hierarchically, where each abstract groups multiple document chunks
```

### 描述检索
```
原：retrieve relevant entities
新：retrieve relevant abstracts and their corresponding chunks
```

### 描述Cuckoo Filter
```
原：store entity fingerprints
新：store abstract fingerprints along with chunk addresses
```

## 三个关键文档

1. **PAPER_REVISION_GUIDE.md** - 详细的修改指南（推荐先读）
2. **TERM_REPLACEMENT_TABLE.md** - 完整的术语替换对照表
3. **QUICK_START_REVISION.md** - 本文档（快速参考）

## 快速检查清单

- [ ] 标题已更新
- [ ] 摘要中entity→abstract
- [ ] Introduction重新表述
- [ ] Methodology部分更新工作流程描述
- [ ] 算法描述更新术语
- [ ] 实验部分使用abstract术语
- [ ] Use Cases重新表述
- [ ] 所有图表已更新（如有）

## 注意事项

1. **保持一致性**：确保全文使用统一的术语
2. **首次定义**：在首次出现新术语时提供清晰定义
3. **说明映射**：明确说明2个chunk对应1个abstract的关系
4. **代码兼容**：如果代码中使用Entity命名，可在论文中说明是为了向后兼容

## 常见问题

**Q: 是否所有"entity"都要改？**
A: 方法描述中的都要改。如果指"命名实体"（Named Entity）的概念，可以保留但需要说明区别。

**Q: 如何描述chunk和abstract的关系？**
A: 强调"每两个连续的document chunks对应一个abstract，形成语义层次的抽象"

**Q: 实验结果需要重新跑吗？**
A: 如果代码已经支持abstract（从代码看已经支持），实验结果可以保持不变，但描述需要更新为"abstract retrieval"。

---

**开始修改**：建议按照 PAPER_REVISION_GUIDE.md 中的章节顺序逐部分修改。


