# 开始构建Cuckoo Filter

## ✅ 查询流程验证完成

查询阶段（search_method=7）的流程已确认正确实现：

1. ✅ Query来了之后，使用spacy提取query中的实体
   - 代码位置：`rag_complete.py:287-297`

2. ✅ 在Cuckoo Filter中查找这些实体 → `get_entity_abstract_addresses_from_cuckoo()`
   - 代码位置：`rag_complete.py:317-328`
   - 返回：pair_ids列表（EntityAddr中的abstract_pair_id）

3. ✅ Cuckoo Filter返回EntityAddr（块状链表），里面存储的是abstract的pair_ids
   - 通过`get_entity_abstract_addresses_from_cuckoo()`直接获取pair_ids

4. ✅ 通过pair_ids找到对应的chunks（pair_id * 2 和 pair_id * 2 + 1）
   - 代码位置：`rag_complete.py:332-338`

5. ✅ 计算query和chunks的余弦相似度，选top k
   - 代码位置：`rag_complete.py:409-451`

6. ✅ 从选中的chunks找到对应的abstracts（pair_id = chunk_id // 2）
   - 代码位置：`rag_complete.py:453-480`

7. ✅ 构建context
   - `source_knowledge`: top k chunks的内容（`rag_complete.py:555`）
   - `abstract_knowledge`: 对应的abstracts内容（`rag_complete.py:561-564`）
   - 最终prompt（`rag_complete.py:639-640`）：
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

## 🚀 运行构建脚本

请运行以下命令来构建Abstract树并更新Cuckoo Filter：

### 方法1：使用Python环境直接运行

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# MedQA数据集
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 build_abstract_and_cuckoo.py --dataset medqa

# DART数据集  
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 build_abstract_and_cuckoo.py --dataset dart

# TriviaQA数据集
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 build_abstract_and_cuckoo.py --dataset triviaqa
```

### 方法2：使用shell脚本批量运行

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
chmod +x build_all_datasets_cuckoo.sh
./build_all_datasets_cuckoo.sh
```

---

## 📋 构建流程

构建脚本将执行：

1. **加载实体列表** - 从`extracted_data/{dataset}_entities_list.txt`
2. **加载向量数据库** - 包含chunks和abstracts
3. **初始化Cuckoo Filter** - 容量 = 实体数 × 2
4. **构建Abstract树** - 从向量数据库读取abstracts并构建树
5. **建立Entity到Abstract映射**：
   - 对每个实体，在chunks中搜索包含该实体的chunks
   - 通过chunk找到对应的abstract（pair_id = chunk_id // 2）
6. **更新Cuckoo Filter** - 存储实体→abstract pair_ids的映射

构建完成后，查询阶段（search_method=7）就可以正常工作了！

---

## 📄 相关文档

- `CUCKOO_FILTER_FLOW.md` - 完整流程说明
- `BUILD_ABSTRACT_CUCKOO_README.md` - 构建脚本使用说明
- `RUN_BUILD_CUCKOO.md` - 运行指南


