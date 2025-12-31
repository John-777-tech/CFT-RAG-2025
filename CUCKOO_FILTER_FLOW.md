# Cuckoo Filter完整流程说明

## 一、构建阶段（build_abstract_and_cuckoo.py）

### 流程步骤：

1. **加载实体列表**
   - 从 `extracted_data/{dataset}_entities_list.txt` 读取实体
   - 这些实体是在构建知识库时从数据集的chunks中用spacy提取的

2. **加载向量数据库**
   - 加载已构建的向量数据库（包含chunks和abstracts）

3. **初始化Cuckoo Filter**
   - 容量 = 实体数 × 2

4. **构建Abstract树**
   - 从向量数据库读取所有abstracts（tree_nodes）
   - 按文件分组，为每个文件构建一个AbstractTree

5. **建立Entity到Abstract映射**
   - 对于每个实体（entities_list.txt中的实体）：
     * 在chunks中搜索包含该实体的chunks（字符串匹配）
     * 通过chunk找到对应的abstract（pair_id = chunk_id // 2）
     * 建立实体 → abstract pair_ids的映射

6. **更新Cuckoo Filter**
   - 存储格式：`entity_name` (小写) → `EntityAddr`（块状链表）
   - `EntityAddr`中存储：`abstract_pair_id1`, `abstract_pair_id2`, `abstract_pair_id3`等

---

## 二、查询阶段（search_method=7）

### 完整流程：

**代码位置：`rag_base/rag_complete.py` 第272-651行**

#### 步骤1: 使用spacy提取query中的实体
- **位置**：`rag_complete.py:287-297`
- **代码**：
  ```python
  query_lower = query.lower().strip()
  doc = nlp(query_lower)
  for ent in doc.ents:
      if ent.label_ == 'EXTRA':
          found_entities.append(ent.text)
  ```

#### 步骤2: 在Cuckoo Filter中查找这些实体
- **位置**：`rag_complete.py:317-328`
- **代码**：
  ```python
  from trag_tree.set_cuckoo_abstract_addresses import get_entity_abstract_addresses_from_cuckoo
  entity_text_lower = entity_text.lower()
  pair_ids = get_entity_abstract_addresses_from_cuckoo(entity_text_lower)
  ```
- **返回**：`pair_ids`列表（EntityAddr中的abstract_pair_id）

#### 步骤3: 通过pair_ids找到对应的chunks
- **位置**：`rag_complete.py:332-338`
- **代码**：
  ```python
  for pair_id in pair_ids:
      chunk_id1 = pair_id * 2
      chunk_id2 = pair_id * 2 + 1
      all_chunk_ids.add(chunk_id1)
      all_chunk_ids.add(chunk_id2)
  ```

#### 步骤4: 计算query和chunks的余弦相似度，选top k
- **位置**：`rag_complete.py:373-451`
- **流程**：
  1. 从向量数据库获取所有候选chunks（`all_chunk_ids`中的chunks）
  2. 对每个chunk计算query和chunk的余弦相似度
  3. 按相似度排序
  4. 取top k chunks
- **代码**：
  ```python
  similarity = util.pytorch_cos_sim(
      util.tensor(input_embedding),
      util.tensor(chunk_embedding)
  )[0].item()
  # 排序后取top k
  results = unique_chunks[:k]
  ```

#### 步骤5: 从选中的chunks找到对应的abstracts
- **位置**：`rag_complete.py:453-480`
- **流程**：
  1. 从选中的chunks中提取对应的pair_ids（`pair_id = chunk_id // 2`）
  2. 从向量数据库获取这些abstracts的内容
- **代码**：
  ```python
  for chunk in results:
      chunk_id = int(chunk.get("chunk_id"))
      pair_id = chunk_id // 2
      selected_pair_ids.add(pair_id)
  # 从向量数据库获取abstracts内容
  ```

#### 步骤6: 构建context
- **位置**：`rag_complete.py:555-640`
- **构建内容**：
  1. **source_knowledge**：top k chunks的内容（第555行）
     ```python
     source_knowledge = "\n".join([x["content"] for x in results])
     ```
  2. **abstract_knowledge**：对应的abstracts内容（第561-564行）
     ```python
     if hasattr(augment_prompt, '_cuckoo_abstracts') and augment_prompt._cuckoo_abstracts:
         abstract_knowledge = "\n---\n".join(augment_prompt._cuckoo_abstracts)
     ```
  3. **最终prompt**（第639-640行）：
     ```
     请回答问题，可以使用我提供的信息（不保证信息是有用的），在回答中不要有分析我提供信息的内容，直接说答案，答案要简略。
     
     信息:
     {source_knowledge}
     
     摘要：
     {abstract_knowledge}
     
     问题: 
     {query}
     ```

---

## 三、运行构建脚本

### 方法1：逐个运行
```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# MedQA
python3 build_abstract_and_cuckoo.py --dataset medqa

# DART
python3 build_abstract_and_cuckoo.py --dataset dart

# TriviaQA
python3 build_abstract_and_cuckoo.py --dataset triviaqa
```

### 方法2：批量运行
```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
./build_all_datasets_cuckoo.sh
```

### 方法3：使用Python环境
```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 build_abstract_and_cuckoo.py --dataset medqa
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 build_abstract_and_cuckoo.py --dataset dart
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 build_abstract_and_cuckoo.py --dataset triviaqa
```

---

## 四、验证查询流程

查询流程代码已完整实现，包含：

✅ 1. spacy提取query中的实体  
✅ 2. Cuckoo Filter查找实体，获取pair_ids  
✅ 3. 通过pair_ids找到对应的chunks  
✅ 4. 计算query和chunks的余弦相似度，选top k  
✅ 5. 从选中的chunks找到对应的abstracts  
✅ 6. 构建context（source_knowledge + abstract_knowledge）

所有步骤都已正确实现，可以直接使用！


