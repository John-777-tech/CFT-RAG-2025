# 论文修改摘要

## 已完成的修改

已创建修改后的完整LaTeX文件：`paper_revised.tex`

### 主要修改内容

#### 1. Abstract部分
- ✅ `entity localization` → `abstract localization`
- ✅ `organizes entities` → `organizes knowledge through hierarchical abstract tree structures`
- ✅ 添加了"each abstract corresponds to multiple document chunks"说明

#### 2. Introduction部分
- ✅ Figure 1说明：`Key entities` → `Key semantic concepts`，`entity trees` → `abstract trees`
- ✅ Tree-RAG描述：所有`entities`改为`abstracts`，添加了"each abstract node corresponds to multiple document chunks"
- ✅ Cuckoo Filter描述：`searching entities` → `searching abstracts`
- ✅ 温度变量描述：`each entity` → `each abstract`，`entities` → `abstracts`
- ✅ 块链表描述：添加了"along with the addresses of corresponding document chunks"

#### 3. Related Work - Tree-RAG部分
- ✅ `hierarchy of entities` → `hierarchy of semantic concepts`
- ✅ `identify relevant entities` → `identify key semantic concepts`
- ✅ `retrieval of relevant entities` → `retrieval of relevant abstracts`
- ✅ `abstract forest`，`abstract nodes`，添加了`corresponding document chunks`

#### 4. Data Pre-processing部分
- ✅ 小节标题说明改为"concepts"和"abstracts"
- ✅ Entities Recognition小节添加了说明：entity recognition用于识别关键概念，然后定位到abstract nodes
- ✅ Relationship Extraction中：`group entities` → `group concepts`

#### 5. Methodology部分
- ✅ Figure 2说明：`entity x` → `abstract x`，添加了"along with corresponding chunk addresses"
- ✅ Storage Mode：所有`entity`改为`abstract`，添加了chunk地址说明
- ✅ Context Generation：所有`entity`改为`abstract`，添加了chunk访问说明
- ✅ 算法1：输入从`Input entity`改为`Input abstract`，所有`entity x`改为`abstract x`

#### 6. Experiments部分
- ✅ Naive T-RAG：`entity tree` → `abstract tree`，`entity lookup` → `abstract lookup`
- ✅ Text-based RAG：`entity relationships` → `abstract relationships`
- ✅ ANN Graph RAG：`entity structure` → `abstract structure`，`entities` → `abstracts`
- ✅ ANN Tree-RAG：`entity tree structure` → `abstract tree structure`，`each entity` → `each abstract`
- ✅ CFT-RAG：所有`entity`改为`abstract`
- ✅ 小节标题：`Datasets and Entity Forest` → `Datasets and Abstract Forest`
- ✅ 数据集描述：`extract entities` → `identify key concepts`，`entity forest` → `abstract forest`
- ✅ 结果评估：`searching entities` → `searching abstracts`，`thousands of entities` → `thousands of abstracts`
- ✅ Figure 3说明：`entities` → `abstracts`，`entities forest` → `abstract forest`
- ✅ Ablation Experiment：`large number of entities` → `large number of abstracts`，`entities` → `abstracts`

### 保持不变的部分

- ✅ Conclusion部分（没有提到具体entity/abstract，保持原样）
- ✅ 表格数据（实验数据不变）
- ✅ 算法逻辑（只改了术语，逻辑不变）
- ✅ 参考文献引用（保持不变）

### 关键术语统一

全文统一使用了以下术语：
- `abstract` / `abstracts`（抽象）
- `abstract tree` / `abstract trees`（抽象树）
- `abstract forest`（抽象森林）
- `abstract node` / `abstract nodes`（抽象节点）
- `abstract retrieval`（抽象检索）
- `abstract localization`（抽象定位）

### 新增的说明

在关键位置添加了以下说明：
1. Abstract中说明"each abstract corresponds to multiple document chunks"
2. Introduction中说明"each abstract node corresponds to multiple document chunks"
3. Data Pre-processing中说明entity recognition用于识别概念，然后定位到abstract nodes
4. 多处添加了"along with corresponding document chunks"或"corresponding chunk addresses"说明

## 使用说明

1. 文件位置：`paper_revised.tex`
2. 直接替换原LaTeX文件中的相应部分即可
3. 如果还有Appendix部分，请检查Appendix中的算法描述（Entity Insertion/Deletion/Eviction）是否也需要改为Abstract

## 注意事项

1. **检查Appendix**：如果论文有Appendix部分（特别是算法2、算法3等），需要检查是否也需要修改
2. **一致性检查**：建议全文搜索"entity"确认没有遗漏（除了"named entity"等特殊情况）
3. **图表检查**：确认所有图表说明都已更新

## 修改统计

- 总计修改位置：约50+处
- 主要涉及：Abstract, Introduction, Methodology, Experiments部分
- 修改类型：术语替换 + 概念说明增强
