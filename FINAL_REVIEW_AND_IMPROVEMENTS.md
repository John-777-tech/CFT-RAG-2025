# 最终检查与改进建议

## 发现的问题和改进建议

### 1. 小节标题需要修改（重要）

**问题位置**：Data Pre-processing部分
- 第42行：`\subsection{Entities Recognition}` 

**建议**：
虽然内容已经说明了entity recognition用于识别关键概念，但标题应该更一致。建议改为：
```latex
\subsection{Concept Identification}
```
或者
```latex
\subsection{Abstract Identification}
```

**理由**：与其他部分的abstract术语保持一致

---

### 2. Graph-RAG描述中的"entities"（可保持，但建议澄清）

**问题位置**：Related Work - Graph-RAG部分
- 第33行：`relationships between entities and concepts`

**分析**：
这里提到的"entities"是指"命名实体"（named entities），这是Graph-RAG的通用描述，不是我们方法的核心。**可以保持**，因为这是描述Graph-RAG的特性，不是我们方法的描述。

**可选改进**：
如果需要更清晰，可以在前面加上说明：
```latex
The key difference between traditional RAG and Graph-RAG is the use of a graph, such as a knowledge graph, to model relationships between named entities (e.g., person names, locations) and concepts, which can improve...
```

---

### 3. 算法描述可以更清晰（建议改进）

**问题位置**：算法1（Context Generation Algorithm）

**当前问题**：
- 算法中没有明确说明如何获取chunk信息
- 算法描述主要是抽象节点的关系，但没有明确提到chunk的访问

**建议改进**：
可以在算法注释或描述中说明：从block list中获取的地址包括abstract节点地址和对应的chunk地址。

**可选改进**：
在算法前添加说明：
```latex
The algorithm retrieves the context for a given abstract $x$ by first locating its fingerprint in the Cuckoo Filter, then traversing the block linked list to access both abstract node addresses and corresponding document chunk addresses stored in the tree structure.
```

---

### 4. Introduction部分可以加强abstract的定义（建议改进）

**当前状态**：
Introduction中已经说明了"each abstract node corresponds to multiple document chunks"，但可以更明确地定义什么是abstract。

**建议**：
在Tree-RAG描述之前或之后，添加一个更明确的定义：
```latex
In our approach, an abstract represents a semantic grouping of multiple document chunks, forming a higher-level knowledge unit that captures the relationship between related content pieces. Each abstract in the tree corresponds to a pair of consecutive document chunks (2:1 mapping), enabling hierarchical knowledge organization at the abstraction level.
```

---

### 5. Methodology部分可以更明确说明abstract的构建（建议改进）

**问题位置**：Storage Mode小节

**建议**：
在开始描述Cuckoo Filter之前，可以添加一句话说明abstract是如何构建的：
```latex
Abstracts are constructed by grouping multiple consecutive document chunks (typically two chunks per abstract) based on semantic similarity, forming a hierarchical knowledge structure where each abstract node contains the semantic summary of its constituent chunks.
```

---

### 6. Data Pre-processing部分开头的描述可以更精确（建议改进）

**当前**（第40行）：
```latex
It is important to recognize key concepts and construct hierarchical relationships (e.g., tree diagrams) between abstracts from datasets.
```

**建议**：
可以更明确说明abstract的构建过程：
```latex
It is important to identify key concepts and construct hierarchical abstract tree structures from datasets, where each abstract groups multiple document chunks and abstracts are organized hierarchically based on their semantic relationships.
```

---

## 优先级分类

### 高优先级（建议修改）

1. ✅ **小节标题**：`Entities Recognition` → `Concept Identification` 或 `Abstract Identification`
   - 理由：保持术语一致性

### 中优先级（可选改进）

2. ⚠️ **Introduction中添加abstract定义**：更明确地定义abstract是什么
   - 理由：帮助读者更好理解核心概念

3. ⚠️ **Methodology中添加abstract构建说明**：说明abstract如何从chunks构建
   - 理由：使方法更完整

### 低优先级（可选）

4. ⚪ **Graph-RAG中的entities说明**：可以保持原样，因为这是描述其他方法
   - 理由：这是描述Graph-RAG，不是我们的方法

5. ⚪ **算法描述增强**：添加chunk访问的说明
   - 理由：当前算法已经足够，但可以更详细

---

## 建议的修改版本

### 修改1：小节标题

```latex
\subsection{Concept Identification}
SpaCy is a Python library, and its entity recognition function is based on deep learning models (e.g., CNN and Transformer). It captures information by transforming the text into word vectors and feature vectors. The models are trained on a labeled corpus to recognize named entities in the text, such as names of people and places. We adopt the method in T-RAG by using the spaCy library to recognize and extract key concepts from a user's query~\citep{fatehkia2024t}. Note that entity recognition serves to identify key concepts in queries, which are then used to locate corresponding abstract nodes in the abstract tree, where each abstract represents a higher-level semantic concept that groups multiple document chunks.
```

### 修改2：Introduction中加强定义（可选）

在Tree-RAG描述之前添加：
```latex
In our approach, an abstract represents a semantic grouping of multiple document chunks (typically two consecutive chunks), forming a higher-level knowledge unit that captures the relationship between related content pieces. Abstracts are organized hierarchically in tree structures, enabling multi-level semantic retrieval.

Tree-RAG, an extension of RAG, improves on traditional RAG frameworks by using a hierarchical abstract tree structure to organize the retrieved knowledge...
```

### 修改3：Data Pre-processing开头（可选）

```latex
It is important to identify key concepts and construct hierarchical abstract tree structures from datasets, where each abstract groups multiple document chunks and abstracts are organized hierarchically based on their semantic relationships. It mainly involves the steps of concept identification, relationship extraction, abstract construction, and filtering.
```

---

## 最终建议

**必须修改**：
1. 小节标题：`Entities Recognition` → `Concept Identification`

**强烈建议修改**（如果篇幅允许）：
2. Introduction中添加abstract的明确定义
3. Methodology中说明abstract的构建方式

**可选修改**：
4. 算法描述中可以添加chunk访问的说明

---

## 检查清单

- [ ] 小节标题已修改
- [ ] Introduction中abstract定义清晰
- [ ] Methodology中说明了abstract的构建
- [ ] 全文术语一致性检查
- [ ] 算法描述清晰完整





