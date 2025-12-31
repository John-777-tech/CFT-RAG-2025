# 运行说明：构建Abstract树并更新Cuckoo Filter

## 使用方法

### 方法1：逐个数据集运行

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# MedQA数据集
python3 build_abstract_and_cuckoo.py --dataset medqa

# DART数据集
python3 build_abstract_and_cuckoo.py --dataset dart

# TriviaQA数据集
python3 build_abstract_and_cuckoo.py --dataset triviaqa
```

### 方法2：使用Python环境运行

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# 使用python310_arm环境
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 build_abstract_and_cuckoo.py --dataset medqa
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 build_abstract_and_cuckoo.py --dataset dart
/Users/zongyikun/opt/anaconda3/envs/python310_arm/bin/python3 build_abstract_and_cuckoo.py --dataset triviaqa
```

### 方法3：使用shell脚本（如果终端正常）

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
./run_build_cuckoo.sh
```

## 工作流程

1. **加载实体列表**：从 `extracted_data/{dataset}_entities_list.txt` 读取实体
2. **加载向量数据库**：加载已构建的向量数据库（包含chunks和abstracts）
3. **初始化Cuckoo Filter**：根据实体数量初始化（容量 = 实体数 × 2）
4. **构建Abstract树**：
   - 从向量数据库读取所有abstracts（tree_nodes）
   - 按文件分组
   - 为每个文件构建一个AbstractTree
5. **建立Entity到Abstract映射**：
   - 对于每个实体（entities_list.txt中的实体）
   - 在chunks中搜索包含该实体的chunks（字符串匹配）
   - 通过chunks找到对应的abstracts（pair_id = chunk_id // 2）
6. **更新Cuckoo Filter**：
   - 将映射存储：entity_name (小写) → EntityAddr（块状链表）
   - EntityAddr中存储：abstract_pair_id1, abstract_pair_id2, ...

## 注意事项

- 确保Cuckoo Filter模块已编译（`TRAG-cuckoofilter/build/cuckoo_filter_module.so`）
- 确保向量数据库已构建并包含abstracts（tree_nodes）
- 如果遇到模块导入错误，可能需要先编译Cuckoo Filter


