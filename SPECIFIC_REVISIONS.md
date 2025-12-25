# 论文具体修改位置清单

## 一、Abstract部分（必须修改）

### 原文位置：
```latex
which optimizes entity localization during the retrieval process
```
**改为**：
```latex
which optimizes abstract localization during the retrieval process
```

### 原文位置：
```latex
Tree-RAG effectively organizes entities through the introduction of a hierarchical tree structure
```
**改为**：
```latex
Tree-RAG effectively organizes knowledge through hierarchical abstract tree structures, where each abstract corresponds to multiple document chunks
```

---

## 二、Introduction部分（必须修改）

### 位置1：Figure说明
```latex
Key entities are then identified from entity trees by applying SpaCy and hierarchical tree searches.
```
**改为**：
```latex
Key semantic concepts are identified from queries and used to locate relevant abstracts in abstract trees through hierarchical tree searches, where each abstract represents a semantic grouping of multiple document chunks.
```

### 位置2：
```latex
Tree-RAG, an extension of RAG, improves on traditional RAG frameworks by using a hierarchical tree structure to organize the retrieved knowledge, thus providing richer context and capturing complex relationships among entities.
```
**改为**：
```latex
Tree-RAG, an extension of RAG, improves on traditional RAG frameworks by using a hierarchical abstract tree structure to organize the retrieved knowledge, thus providing richer context and capturing complex relationships among abstracts at multiple semantic levels.
```

### 位置3：
```latex
In Tree-RAG, entities are arranged hierarchically, allowing the retrieval process to more effectively traverse related entities at multiple levels.
```
**改为**：
```latex
In Tree-RAG, abstracts are arranged hierarchically, where each abstract node corresponds to multiple document chunks, allowing the retrieval process to more effectively traverse related abstracts at multiple levels.
```

### 位置4：
```latex
the time required to locate and retrieve relevant entities within the hierarchical structure significantly increases
```
**改为**：
```latex
the time required to locate and retrieve relevant abstracts within the hierarchical structure significantly increases
```

### 位置5：
```latex
Theoretically, the time complexity of Cuckoo Filter for searching entities is O(1)
```
**改为**：
```latex
Theoretically, the time complexity of Cuckoo Filter for searching abstracts is O(1)
```

### 位置6：
```latex
From a spatial point of view, entities are stored in the Cuckoo Filter in the form of fingerprints (12-bit)
```
**改为**：
```latex
From a spatial point of view, abstracts are stored in the Cuckoo Filter in the form of fingerprints (12-bit)
```

### 位置7：
```latex
with each entity stored in the Cuckoo Filter maintaining an additional variable called temperature. The variable is used to record the frequency of the entity being accessed. The Cuckoo Filter sorts the entities according to the frequency, and the entities with the highest temperature are placed in the front of the bucket
```
**改为**：
```latex
with each abstract stored in the Cuckoo Filter maintaining an additional variable called temperature. The variable is used to record the frequency of the abstract being accessed. The Cuckoo Filter sorts the abstracts according to the frequency, and the abstracts with the highest temperature are placed in the front of the bucket
```

### 位置8：
```latex
where Cuckoo Filter stores the addresses of entities at different locations in the tree
```
**改为**：
```latex
where Cuckoo Filter stores the addresses of abstracts at different locations in the tree, along with the addresses of corresponding document chunks
```

---

## 三、Related Work部分（需要修改）

### Tree-RAG描述：
```latex
The algorithmic process of Tree-RAG consists of the following steps: first, the input query is parsed to identify relevant entities and the retrieval of relevant entities is performed in the constructed forest.
```
**改为**：
```latex
The algorithmic process of Tree-RAG consists of the following steps: first, the input query is parsed to identify key semantic concepts and the retrieval of relevant abstracts is performed in the constructed abstract forest.
```

### Tree-RAG描述：
```latex
However, T-RAG runs inefficiently due to the time-consuming nature of finding all the locations of related entities in a forest with a large amount of data.
```
**改为**：
```latex
However, T-RAG runs inefficiently due to the time-consuming nature of finding all the locations of related abstracts in a forest with a large amount of data.
```

---

## 四、Data Pre-processing部分（需要重新解释）

### 需要添加说明：
在这个部分的开头添加一段，说明：
- 实体识别只是第一步，用于识别关键概念
- 然后这些概念被映射到抽象树中的抽象节点
- 强调抽象和实体的区别

**建议添加**：
```latex
\subsection{Abstract Construction}
While entity recognition identifies key concepts from text, our approach constructs semantic abstracts that group multiple document chunks. Each abstract represents a higher-level semantic concept that encompasses multiple related chunks, forming a hierarchical knowledge organization structure. The entity recognition step serves to identify key concepts in queries, which are then used to locate corresponding abstract nodes in the abstract tree.
```

---

## 五、Methodology部分（必须大量修改）

### 位置1：Figure 2说明
```latex
The workflow of CFT-RAG when query contains entity x. The entity with high temperature will be placed ahead of which with low temperature in the bucket. All the addresses in different trees of the entity are linked by the block linked list.
```
**改为**：
```latex
The workflow of CFT-RAG when query contains abstract x. The abstract with high temperature will be placed ahead of which with low temperature in the bucket. All the addresses in different trees of the abstract, along with corresponding chunk addresses, are linked by the block linked list.
```

### 位置2：Storage Mode小节
```latex
In addition to entity trees, we set up an additional Cuckoo Filter to store some entities to improve retrieval efficiency.
```
**改为**：
```latex
In addition to abstract trees, we set up an additional Cuckoo Filter to store abstracts to improve retrieval efficiency.
```

### 位置3：
```latex
We first find out all locations of each entity in the forest and then store these addresses in a block linked list.
```
**改为**：
```latex
We first find out all locations of each abstract in the forest and then store these addresses, along with the addresses of corresponding document chunks, in a block linked list.
```

### 位置4：
```latex
The temperature variable records how often each entity is accessed
```
**改为**：
```latex
The temperature variable records how often each abstract is accessed
```

### 位置5：
```latex
In summary, in each entry of the bucket, an entity's fingerprint, its temperature, and head pointer of its block linked list are stored.
```
**改为**：
```latex
In summary, in each entry of the bucket, an abstract's fingerprint, its temperature, and head pointer of its block linked list (containing abstract and chunk addresses) are stored.
```

### 位置6：Context Generation小节
```latex
After the fingerprint of the target entity is found, the temperature of the entity is added by one
```
**改为**：
```latex
After the fingerprint of the target abstract is found, the temperature of the abstract is added by one
```

### 位置7：
```latex
From this pointer, the location of the entity node in different trees including multi-level parent nodes, child nodes, etc. can be accessed through the address stored in the block list.
```
**改为**：
```latex
From this pointer, the location of the abstract node in different trees including multi-level parent nodes, child nodes, and corresponding document chunks can be accessed through the addresses stored in the block list.
```

### 位置8：
```latex
For the queried entity and its parent and child nodes in different trees, we form a context between the entity and its relevant nodes based on the set template.
```
**改为**：
```latex
For the queried abstract and its parent and child nodes in different trees, along with corresponding chunks, we form a context between the abstract and its relevant nodes based on the set template.
```

### 位置9：算法1（Context Generation Algorithm）
```latex
\KwIn{$x$: Input entity}
```
**改为**：
```latex
\KwIn{$x$: Input abstract}
```

算法中的所有"entity $x$"改为"abstract $x$"

---

## 六、Experiments部分（必须修改）

### 位置1：Baseline描述
```latex
This basic implementation of T-RAG does not include any filtering optimizations. The method constructs an entity tree using entities extracted from the dataset
```
**改为**：
```latex
This basic implementation of T-RAG does not include any filtering optimizations. The method constructs an abstract tree using abstracts constructed from the dataset
```

### 位置2：ANN Graph RAG描述
```latex
This model integrates approximate nearest neighbor (ANN) search with a graph-based entity structure to accelerate retrieval while maintaining semantic relevance. Entities and their relationships are organized into a directed graph
```
**改为**：
```latex
This model integrates approximate nearest neighbor (ANN) search with a graph-based abstract structure to accelerate retrieval while maintaining semantic relevance. Abstracts and their relationships are organized into a directed graph
```

### 位置3：ANN Tree-RAG描述
```latex
In this variant, Approximate Nearest Neighbor (ANN) search is employed to accelerate document retrieval in the entity tree structure.
```
**改为**：
```latex
In this variant, Approximate Nearest Neighbor (ANN) search is employed to accelerate document retrieval in the abstract tree structure.
```

### 位置4：CFT-RAG描述
```latex
The CFT-RAG method stores the individual nodes of the entity in the forest in each bucket of the Cuckoo Filter
```
**改为**：
```latex
The CFT-RAG method stores the individual nodes of the abstract in the forest in each bucket of the Cuckoo Filter
```

### 位置5：
```latex
After the entity tree is generated, the nodes with the same entity details in each tree are concatenated into a block list
```
**改为**：
```latex
After the abstract tree is generated, the nodes with the same abstract details in each tree are concatenated into a block list
```

### 位置6：
```latex
An improved CFT-RAG is to maintain access popularity of each entity, called temperature, at the head node of each block list, and raise the level of temperature corresponding to the hit entity during retrieval.
```
**改为**：
```latex
An improved CFT-RAG is to maintain access popularity of each abstract, called temperature, at the head node of each block list, and raise the level of temperature corresponding to the hit abstract during retrieval.
```

### 位置7：
```latex
the fingerprints and block list header pointers in the bucket can be sorted according to temperature, and the fingerprints with higher access popularity are placed at the front of the bucket, which can take advantage of the locality of the entities contained in the user questions
```
**改为**：
```latex
the fingerprints and block list header pointers in the bucket can be sorted according to temperature, and the fingerprints with higher access popularity are placed at the front of the bucket, which can take advantage of the locality of the abstracts contained in the user queries
```

### 位置8：Datasets and Entity Forest
```latex
\subsection{Datasets and Entity Forest}
```
**改为**：
```latex
\subsection{Datasets and Abstract Forest}
```

### 位置9：
```latex
We leverage dependency parsing models to extract entities and relationships among them and construct the entity forest based on these extracted entities and relationships.
```
**改为**：
```latex
We leverage dependency parsing models to identify key concepts and construct abstract trees based on semantic relationships, forming an abstract forest where each abstract node corresponds to multiple document chunks.
```

### 位置10：Results and Evaluations
```latex
the error rate of our method in the process of searching entities is very low
```
**改为**：
```latex
the error rate of our method in the process of searching abstracts is very low
```

### 位置11：
```latex
In the experimental datasets, there are thousands of entities that can be extracted
```
**改为**：
```latex
In the experimental datasets, there are thousands of abstracts that can be constructed
```

### 位置12：
```latex
showing that the number of entities causing the lookup error is 0 to 1 out of 1024 buckets for thousands of entities.
```
**改为**：
```latex
showing that the number of abstracts causing the lookup error is 0 to 1 out of 1024 buckets for thousands of abstracts.
```

### 位置13：Ablation Experiment
```latex
which is eminently useful when the query given by the user contains a large number of entities.
```
**改为**：
```latex
which is eminently useful when the query given by the user requires retrieving a large number of abstracts.
```

### 位置14：
```latex
This sorting design allows the 'hot' entities to be found more quickly in subsequent queries.
```
**改为**：
```latex
This sorting design allows the 'hot' abstracts to be found more quickly in subsequent queries.
```

### 位置15：Figure 3说明
```latex
We record the search time per round of query with different number of trees and entities. Each round represents a search in the entities forest
```
**改为**：
```latex
We record the search time per round of query with different number of trees and abstracts. Each round represents a search in the abstract forest
```

---

## 七、Conclusion部分（需要修改）

### 位置1：
```latex
However, its performance is hindered by the computational inefficiencies of retrieving and organizing large-scale knowledge within complex tree structures.
```
这个可以保持，因为说的是知识，不是实体。

### 位置2：
```latex
Future work could explore further optimizations, such as adapting the method for different knowledge structures
```
这个可以保持。

---

## 八、Appendix部分（如果存在，需要检查）

需要检查Appendix中是否有算法描述，如果有，也需要将entity改为abstract。

特别是：
- Algorithm 1: Entity Insertion → Abstract Insertion
- Algorithm 2: Entity Deletion → Abstract Deletion  
- Algorithm 3: Entity Eviction → Abstract Eviction

---

## 修改优先级

### 高优先级（必须修改）：
1. Abstract中的所有entity→abstract
2. Introduction中的核心描述
3. Methodology部分的Storage Mode和Context Generation
4. 算法描述中的术语
5. Experiments部分的CFT-RAG描述

### 中优先级（建议修改）：
1. Related Work中的描述
2. Data Pre-processing部分添加抽象说明
3. Baseline方法描述

### 低优先级（可选）：
1. Conclusion部分（如果提到实体，需要改）
2. 图表说明中的细节

---

## 特别注意事项

1. **保持一致性**：确保全文使用统一的术语
2. **首次定义**：在Introduction或Methodology中首次出现"abstract"时，要给出清晰的定义
3. **概念区分**：如果需要提到"named entity"（命名实体，如人名、地名），要说明这与"abstract"的区别
4. **技术细节**：如果代码中使用Entity命名，可以在技术细节部分说明是为了兼容性


