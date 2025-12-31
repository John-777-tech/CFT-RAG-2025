# 测试Cuckoo Filter流程（depth=1）说明

## 测试脚本已准备

已创建测试脚本：`test_cuckoo_flow_depth1.py`

## 运行测试

在你的终端中运行：

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# 测试MedQA数据集
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 test_cuckoo_flow_depth1.py --dataset medqa

# 测试DART数据集
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 test_cuckoo_flow_depth1.py --dataset dart

# 测试TriviaQA数据集
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 test_cuckoo_flow_depth1.py --dataset triviaqa
```

## 测试流程验证点

脚本会验证以下步骤：

### ✅ 步骤1: 使用spacy提取query中的实体
- 代码位置：`rag_complete.py:287-297`
- 验证：提取EXTRA标签的实体

### ✅ 步骤2: 在Cuckoo Filter中查找这些实体
- 代码位置：`rag_complete.py:317-328`
- 调用：`get_entity_abstract_addresses_from_cuckoo(entity_text_lower)`
- 返回：pair_ids列表

### ✅ 步骤3: 通过pair_ids找到对应的chunks和abstracts
- 代码位置：`rag_complete.py:332-338`
- 计算：`chunk_id1 = pair_id * 2`, `chunk_id2 = pair_id * 2 + 1`
- 每个abstract对应2个chunks

### ✅ 步骤4: 计算query和chunks的余弦相似度，选top k
- 代码位置：`rag_complete.py:409-451`
- 计算相似度：`util.pytorch_cos_sim(query_embedding, chunk_embedding)`
- 排序：按相似度降序排序
- 选top k：`results = unique_chunks[:k]`

### ✅ 步骤5: 从选中的chunks找到对应的abstracts
- 代码位置：`rag_complete.py:453-480`
- 计算pair_id：`pair_id = chunk_id // 2`
- 从向量数据库获取abstracts内容

### ✅ 步骤6: 构建context
- 代码位置：`rag_complete.py:555-640`
- `source_knowledge`: top k chunks的内容（第555行）
- `abstract_knowledge`: 对应的abstracts内容（第561-564行）
- 最终prompt包含：
  ```
  信息: {source_knowledge}
  摘要：{abstract_knowledge}
  问题: {query}
  ```

## 预期输出

测试脚本会显示：
1. 每个步骤的执行结果
2. 提取的实体数量和pair_ids数量
3. 找到的chunks数量
4. 最终查询结果
5. 检索时间和生成时间

如果所有步骤都显示 ✓，说明流程完整且正确！


