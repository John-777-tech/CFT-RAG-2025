# 论文修改后的关键部分

## 一、修改后的Abstract

```latex
\begin{abstract}
Although retrieval-augmented generation(RAG) significantly improves generation quality by retrieving external knowledge bases and integrating generated content, it faces computational efficiency bottlenecks, particularly in knowledge retrieval tasks involving hierarchical structures for Tree-RAG. This paper proposes a Tree-RAG acceleration method based on the improved Cuckoo Filter, which optimizes abstract localization during the retrieval process to achieve significant performance improvements. Tree-RAG effectively organizes knowledge through hierarchical abstract tree structures, where each abstract corresponds to multiple document chunks, enabling multi-level semantic retrieval. The Cuckoo Filter serves as an efficient data structure that supports rapid membership queries and dynamic updates for abstract-level knowledge. The experiment results demonstrate that our method is much faster than baseline methods while maintaining high levels of generative quality. For instance, our method is more than 800\% faster than naive Tree-RAG on DART dataset. Our work is available at \href{https://github.com/TUPYP7180/CFT-RAG-2025}{https://github.com/TUPYP7180/CFT-RAG-2025}.
\end{abstract}
```

---

## 二、修改后的Figure 1说明（Introduction部分）

```latex
    \caption{The workflow of CFT-RAG begins with a user query, which undergoes vector search to retrieve relevant documents. Key semantic concepts are identified from queries and used to locate relevant abstracts in abstract trees through hierarchical tree searches, where each abstract represents a semantic grouping of multiple document chunks. Context information related to these abstracts is retrieved and filtered efficiently by applying Cuckoo Filter. The retrieved context, including both abstract-level information and corresponding document chunks, are integrated into a comprehensive prompt, which is fed into an augmented large language model (LLM). The LLM processes this enriched prompt to generate a context-aware and accurate response to the user query.}
```

---

## 三、修改后的Introduction关键段落

### 段落1：Tree-RAG描述

```latex
Tree-RAG, an extension of RAG, improves on traditional RAG frameworks by using a hierarchical abstract tree structure to organize the retrieved knowledge, thus providing richer context and capturing complex relationships among abstracts at multiple semantic levels. In Tree-RAG, abstracts are arranged hierarchically, where each abstract node corresponds to multiple document chunks, allowing the retrieval process to more effectively traverse related abstracts at multiple levels. This results in enhanced response accuracy and coherence, as the tree structure maintains connections between abstracts that are essential for contextually rich answers~\citep{fatehkia2024t}. However, a critical limitation of Tree-RAG lies in its computational inefficiency: as the datasets and tree depth grow, the time required to locate and retrieve relevant abstracts within the hierarchical structure significantly increases, posing scalability challenges. This paper aims to greatly improve the retrieval efficiency of Tree-RAG without sacrificing the accuracy of the generated responses.
```

### 段落2：Cuckoo Filter优势

```latex
Theoretically, the time complexity of Cuckoo Filter for searching abstracts is O(1), which is significantly lower than that of naive Tree-RAG. From a spatial point of view, abstracts are stored in the Cuckoo Filter in the form of fingerprints (12-bit), which greatly saves memory usage. On the other hand, when the load factor of Cuckoo Filter exceeds the preset threshold, the storage capacity is usually increased by double expansion, while the original elements are re-hashed and migrated to the new storage location to complete the automatic expansion. This keeps the loading rate of cuckoo filter high and not too high, thus saving memory while avoiding hash collisions as much as possible.

Moreover, we propose two novel designs. The first design introduces a temperature variable, with each abstract stored in the Cuckoo Filter maintaining an additional variable called temperature. The variable is used to record the frequency of the abstract being accessed. The Cuckoo Filter sorts the abstracts according to the frequency, and the abstracts with the highest temperature are placed in the front of the bucket, thus speeding up the retrieval. The second design is to introduce block linked list, where Cuckoo Filter stores the addresses of abstracts at different locations in the tree, along with the addresses of corresponding document chunks. The utilization of the space of block linked list is high, it can support relatively efficient random access, reduce the number of linked list nodes, and perform well in balancing time and space complexity, especially for processing large-scale data. Therefore, we achieve acceleration by storing these addresses in the form of a block linked list. An ablation experiment is performed to demonstrate the effectiveness of the design.
```

---

## 四、修改后的Related Work - Tree-RAG部分

```latex
\textbf{Tree-RAG}  Tree-RAG(T-RAG) is an emerging method that combines tree structure and large language models to improve the effectiveness of knowledge retrieval and generation tasks. Compared to traditional RAG, T-RAG further enhances the context retrieved from vector databases by introducing an abstract tree data structure to represent the hierarchy of semantic concepts in knowledge organization. The algorithmic process of Tree-RAG consists of the following steps: first, the input query is parsed to identify key semantic concepts and the retrieval of relevant abstracts is performed in the constructed abstract forest. Next, the system traverses through the hierarchical structure of the tree to obtain the abstract nodes related to the query and their upper and lower multilevel parent-child nodes, along with corresponding document chunks. Subsequently, the retrieved knowledge is fused with the query to generate the augmented context. Finally, the generative model generates the final answer based on the augmented context. This process effectively combines knowledge retrieval and generation and improves the accuracy and contextual relevance of the generative model~\citep{fatehkia2024t}. However, T-RAG runs inefficiently due to the time-consuming nature of finding all the locations of related abstracts in a forest with a large amount of data. Our method applies the improved Cuckoo Filter to the retrieval process of Tree-RAG, making it greatly faster.
```

---

## 五、修改后的Methodology部分

### 5.1 Figure 2说明

```latex
    \caption{The workflow of CFT-RAG when query contains abstract x. The abstract with high temperature will be placed ahead of which with low temperature in the bucket. All the addresses in different trees of the abstract, along with corresponding chunk addresses, are linked by the block linked list.}
```

### 5.2 Storage Mode小节

```latex
\subsection{Storage Mode} 
In addition to abstract trees, we set up an additional Cuckoo Filter to store abstracts to improve retrieval efficiency. Based on the naive Cuckoo Filter, we introduce the block linked list for optimization, which can greatly reduce memory fragmentation. We first find out all locations of each abstract in the forest and then store these addresses, along with the addresses of corresponding document chunks, in a block linked list.

To further optimize the retrieval performance, we propose an adaptive sorting strategy to reorder the abstracts in each bucket in the Cuckoo Filter based on the temperature variable which is stored at the head of the block list. The temperature variable records how often each abstract is accessed, and abstracts with high-frequency access are prioritized to be placed at the front of the bucket. Since the Cuckoo Filter looks up the elements in the buckets linearly, this reordering mechanism can significantly optimize the query process, which can further improve the response speed of the model. In summary, in each entry of the bucket, an abstract's fingerprint, its temperature, and head pointer of its block linked list (containing abstract and chunk addresses) are stored. The storage mode is included in Figure \ref{fig:my_label2} and details about the process of insertion and eviction of abstracts are provided in Appendix~\ref{sec:appendix}.
```

### 5.3 Context Generation小节

```latex
\subsection{Context Generation}
After the fingerprint of the target abstract is found, the temperature of the abstract is added by one and a pointer to the head of the corresponding block linked list of that abstract is returned. From this pointer, the location of the abstract node in different trees including multi-level parent nodes, child nodes, and corresponding document chunks can be accessed through the addresses stored in the block list. If no matching fingerprint is found, the null pointer is returned. For the queried abstract and its parent and child nodes in different trees, along with corresponding chunks, we form a context between the abstract and its relevant nodes based on the set template. For instance, the upward hierarchical relationship of abstract A are: B, C and D. Finally, we fuse this information with the query to generate the augmented context. After that, the augmented context combined with system prompt and query is regarded as the prompt. The lookup and context generation process is stated in Figure \ref{fig:my_label2}.
```

### 5.4 修改后的算法1

```latex
\begin{algorithm}[H]
\caption{Context Generation Algorithm}
\SetAlgoNoLine
\SetAlgoNlRelativeSize{0} % 设置算法行号间距

\SetAlgoNlRelativeSize{0}

\KwIn{$x$: Input abstract}
\KwOut{$context$: Context generated for abstract $x$}

$f(x) \gets \text{fingerprint}(x);$\\
\If{bucket[$i_1$] or bucket[$i_2$] contains $f(x)$}{
    $temperature \gets temperature + \text{1};$\\
    \Return{head}\;
}

$currentBlock \gets \text{head} \rightarrow \text{next};$

\While{$currentBlock \neq \text{NULL}$}{
    
    \ForEach{location in currentBlock}{
       Let $loc$ be the current location of abstract $x$ in the block;\\
       Find the set of hierarchical relationship nodes at location $loc$ in the tree;\\
        $H_{up} \gets \{h_1, h_2, \dots, h_n\};$\\ % Upward hierarchical nodes;
        $H_{down} \gets \{h'_1, h'_2, \dots, h'_n\};$ \\% Downward hierarchical nodes
       Record the first $n$ upward and downward hierarchical relationship nodes;
        \\\For {($i=1$ ; $i$ < $n$ ; $i$++)}{\quad \text{Store $(h_i, h'_i)$ in context;}}
        
    }
    $currentBlock \gets currentBlock \rightarrow \text{next};$\
}
\For{($i=1$ ; $i < n$ ; $i$++)}{$context \gets context \, \cup \, (h_i, h'_i)$;}

\end{algorithm}
```

---

## 六、修改后的Experiments部分

### 6.1 Baseline - Naive T-RAG

```latex
\textbf{Naive T-RAG}
This basic implementation of T-RAG does not include any filtering optimizations. The method constructs an abstract tree using abstracts constructed from the dataset and employs a Breadth-First Search (BFS) algorithm for abstract lookup. Although this approach has high time complexity and prolonged search time, it provides a straightforward baseline for evaluating the benefits of incorporating filtering mechanisms.
```

### 6.2 Baseline - ANN Graph RAG

```latex
\textbf{ANN Graph RAG}
This model integrates approximate nearest neighbor (ANN) search with a graph-based abstract structure to accelerate retrieval while maintaining semantic relevance. Abstracts and their relationships are organized into a directed graph, enabling multi-hop traversal and contextual inference. During retrieval, ANN is used to identify the closest matching abstracts efficiently, and the graph structure guides the expansion to related abstracts for enriched context. This method balances speed and accuracy by leveraging the fast lookup capabilities of ANN and the expressive power of graph reasoning.
```

### 6.3 Baseline - ANN Tree-RAG

```latex
\textbf{ANN Tree-RAG}
In this variant, Approximate Nearest Neighbor (ANN) search is employed to accelerate document retrieval in the abstract tree structure. Instead of performing exact similarity search, the model leverages efficient ANN indexing techniques (e.g., FAISS or HNSW) to retrieve top-K candidates for each abstract. ANN T-RAG provides a strong balance between performance and efficiency, especially compared to the Naive T-RAG baseline.
```

### 6.4 CFT-RAG描述

```latex
\subsection{CFT-RAG}
Cuckoo Filter supports abstract deletion operation, which is suitable for ongoing data update, and it has a lower false positive rate and is more space efficient. The CFT-RAG method stores the individual nodes of the abstract in the forest in each bucket of the Cuckoo Filter, i.e. it merges the Cuckoo Hash with the Cuckoo Filter. After the abstract tree is generated, the nodes with the same abstract details in each tree are concatenated into a block list, where the pointer to the head of the list corresponds to the fingerprint, and stored together in buckets.

An improved CFT-RAG is to maintain access popularity of each abstract, called temperature, at the head node of each block list, and raise the level of temperature corresponding to the hit abstract during retrieval. For each bucket, if there is a bucket that has not been searched, i.e. if it is free, the fingerprints and block list header pointers in the bucket can be sorted according to temperature, and the fingerprints with higher access popularity are placed at the front of the bucket, which can take advantage of the locality of the abstracts contained in the user queries to improve the running speed of the algorithm.
```

### 6.5 Datasets and Abstract Forest

```latex
\subsection{Datasets and Abstract Forest}
Our experiments use three datasets: the large-scale dataset MedQA~\citep{med} and two medium-sized datasets AESLC~\citep{ael} and DART~\citep{dart}. We leverage dependency parsing models to identify key concepts and construct abstract trees based on semantic relationships, forming an abstract forest where each abstract node corresponds to multiple document chunks. The resulting abstract forest is structured to allow efficient retrieval and provides a practical evaluation scenario for our approach.
```

### 6.6 Results and Evaluations

```latex
\subsubsection{Comparison Experiment}
We conduct the experiments by selecting 36 questions on each dataset. Then we record the average retrieval time and average response accuracy by LangSmith. Table~\ref{tab:combined} presents the retrieval time and accuracy of various RAG-based models across the MedQA, AESLC, and DART datasets. As expected, the Naive T-RAG model incurs the highest retrieval latency due to its exhaustive BFS-based search, while offering moderate accuracy improvements over the text-based baseline. Further efficiency gains are observed in ANN-based methods (ANN T-RAG and ANN G-RAG), which leverage approximate nearest neighbor search to achieve faster response times with comparable accuracy. Notably, CFT-RAG consistently outperforms other variants by achieving the lowest retrieval time across all datasets while maintaining high accuracy, demonstrating the effectiveness of integrating probabilistic filtering with structural optimization. Moreover, when the problem is complex involving multi-hop and the required abstract relationships are precise, our method shows an obvious advantage over the other methods. Use cases are provided in Appendix~\ref{sec:appendix}.

Moreover, the error rate of our method in the process of searching abstracts is very low. After building the trees based on the dataset, the Cuckoo Filter includes 1024 buckets, each of which can hold up to 4 fingerprints and block linked list head pointers. The Cuckoo Filter's own memory expansion strategy is to increase the number of buckets by a power of two. In the experimental datasets, there are thousands of abstracts that can be constructed, and the space load factor for the Cuckoo Filter is more than 70\%. Because the space load factor is not too high and searching errors are mainly caused by hash collisions, the error rate is almost 0, showing that the number of abstracts causing the lookup error is 0 to 1 out of 1024 buckets for thousands of abstracts.
```

### 6.7 Ablation Experiment

```latex
\subsubsection{Ablation Experiment}
Sorting the fingerprints and head pointers of the block linked lists by temperature can optimize the retrieval time without occupying any extra space, which is eminently useful when the query given by the user requires retrieving a large number of abstracts.
We design experiments to measure the effect of having or not having the sorting design on the result. In figure \ref{fig:sort_label}, we can observe that the retrieval time after the first round is significantly shorter than that of the first round. This is because the temperatures are updated according to the access frequency in each round and after each query, the Cuckoo Filter sorts the abstracts according to the abstracts' temperatures. This sorting design allows the 'hot' abstracts to be found more quickly in subsequent queries.
```

### 6.8 Figure 3说明

```latex
    \caption{We record the search time per round of query with different number of trees and abstracts. Each round represents a search in the abstract forest, and abstracts are inserted into the improved Cuckoo Filter before the first search is performed.}
```

---

## 七、需要特别注意的地方

1. **Appendix中的算法**：如果Appendix中有算法描述（如Entity Insertion, Entity Deletion, Entity Eviction），也需要将entity改为abstract

2. **Use Cases**：如果Appendix中有Use Cases描述，需要将：
   - "Rare Entity" → "Key Abstract" 或 "Rare Abstract Concept"
   - "Relation: A - B" → "Abstract Relationship: Abstract_A - Abstract_B"

3. **一致性检查**：确保全文术语一致，特别是：
   - entity tree → abstract tree
   - entity forest → abstract forest  
   - entity node → abstract node
   - entity retrieval → abstract retrieval


