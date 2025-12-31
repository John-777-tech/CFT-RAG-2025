# 构建Abstract树并更新Cuckoo Filter

此脚本用于为数据集构建Abstract树并将实体映射更新到Cuckoo Filter中，**不构建实体树**。

## 使用方法

```bash
python build_abstract_and_cuckoo.py --dataset <dataset_name>
```

### 参数说明

- `--dataset`: 数据集名称（必需），可选值：`medqa`, `dart`, `triviaqa`
- `--entities-file`: 实体列表文件路径（可选，默认：`extracted_data/{dataset}_entities_list.txt`）
- `--vec-db-key`: 向量数据库key（可选，默认：dataset名称）

### 示例

```bash
# 为MedQA数据集构建Abstract树并更新Cuckoo Filter
python build_abstract_and_cuckoo.py --dataset medqa

# 为DART数据集构建
python build_abstract_and_cuckoo.py --dataset dart

# 为TriviaQA数据集构建
python build_abstract_and_cuckoo.py --dataset triviaqa
```

## 工作流程

1. **加载实体列表**：从 `extracted_data/{dataset}_entities_list.txt` 读取实体
2. **加载向量数据库**：加载已构建的向量数据库（包含chunks和abstracts）
3. **初始化Cuckoo Filter**：根据实体数量初始化Cuckoo Filter
4. **构建Abstract树**：
   - 从向量数据库读取所有abstracts（tree_nodes）
   - 按文件（source_file）分组
   - 为每个文件构建一个AbstractTree
5. **建立Entity到Abstract映射**：
   - 从向量数据库读取所有chunks
   - 对于每个实体（entities_list.txt中的实体），在chunks中搜索包含该实体的chunks（字符串匹配）
   - 通过chunks找到对应的abstracts（pair_id = chunk_id // 2）
   - 建立实体 → abstract pair_ids的映射
6. **更新Cuckoo Filter**：
   - 将Entity到Abstract的映射存储到Cuckoo Filter中
   - 存储格式：entity_name (小写) → EntityAddr（块状链表）
   - EntityAddr中存储：abstract_pair_id1, abstract_pair_id2, abstract_pair_id3等

## 前置要求

- 实体列表文件已生成（`extracted_data/{dataset}_entities_list.txt`）
- 向量数据库已构建（`vec_db_cache/{dataset}.db`）
- Cuckoo Filter模块已编译（`TRAG-cuckoofilter/build/cuckoo_filter_module.so`）

## 查询流程（search_method=7）

当使用Cuckoo Filter进行查询时：

1. **Query实体识别**：使用spacy从query中提取实体
2. **Cuckoo Filter查找**：在Cuckoo Filter中查找这些实体 → `get_entity_abstract_addresses_from_cuckoo()`
3. **获取Abstract地址**：Cuckoo Filter返回EntityAddr（块状链表），里面存储的是abstract的pair_ids
4. **找到对应Chunks**：通过pair_ids找到对应的chunks（pair_id * 2 和 pair_id * 2 + 1）
5. **计算相似度**：计算query和chunks的余弦相似度，选top k
6. **获取Abstracts**：从选中的chunks找到对应的abstracts（pair_id = chunk_id // 2）

## 参考

此脚本参考了GitHub仓库的实现：https://github.com/TUPYP7180/CFT-RAG-2025

