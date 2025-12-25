# CFT-RAG-2025-main 2 修改清单

## 📋 主要功能改进

### 1. 两个Chunk对应一个Abstract的实现 ⭐

**核心改进**：实现了"两个chunk对应一个abstract"的层次化知识库结构

#### 修改文件：
- `rag_base/build_index.py`
  - 新增 `expand_chunks_to_tree_nodes()` 函数
  - 修改 `build_index_on_chunks()` 使用新的层次结构
  - 每个两个连续chunk共享一个summary节点（tree_node）

#### 关键代码：
```python
def expand_chunks_to_tree_nodes(chunks: list[str]):
    # 1) 保存所有原始chunks
    # 2) 每两个chunk创建一个summary节点
    pair_id = 0
    for i in range(0, len(chunks), 2):
        merged_text = chunks[i] + "\n" + chunks[i+1]  # 合并两个chunk
        items.append({
            "text": merged_text,
            "meta": {
                "type": "tree_node",
                "pair_id": pair_id,
                "chunk_ids": [i, i+1],
            }
        })
```

### 2. 双重相似度过滤（Dual-Similarity Filtering）⭐

**功能**：对检索结果进行双重相似度过滤，确保chunk和abstract都与query相关

#### 修改文件：
- `rag_base/rag_complete.py`
  - 新增 `enrich_results_with_summary_embeddings()` 函数
  - 新增 `filter_contexts_by_dual_threshold()` 函数
  - 修改 `augment_prompt()` 集成双重相似度过滤

#### 过滤逻辑：
```python
# 保留chunk的条件：
# 1) sim(query, chunk) >= 0.7
# 2) sim(query, abstract) >= 0.7
```

### 3. 向量数据库API适配

#### 修改文件：
- `rag_base/build_index.py`
  - 适配 `lab-1806-vec-db` 的新API（使用目录路径初始化）
  - 使用 `create_table_if_not_exists()` 创建表
  - 使用模块级字典 `_db_table_map` 存储table_name映射

### 4. ARK API集成

#### 修改文件：
- `rag_base/rag_complete.py`
  - 修改 `rag_complete()` 使用 `client.responses.create()`
  - 适配ARK API的输入输出格式
  - 支持从 `response.output[1].content[0].text` 提取答案

#### 环境变量配置：
- `.env` 文件添加 `ARK_API_KEY`、`BASE_URL`、`MODEL_NAME`

### 5. Benchmark测试增强

#### 新增功能：
- **断点续传**：支持中断后继续运行
- **多种评估指标**：ROUGE、BLEU、BERTScore
- **数据集支持**：AESLC、MedQA、DART

#### 新增文件：
- `benchmark/run_benchmark.py` - 支持断点续传的benchmark运行器
- `benchmark/evaluate_comprehensive.py` - 综合评估脚本（ROUGE + BLEU + BERTScore）
- `benchmark/load_datasets.py` - 数据集加载脚本（支持HuggingFace镜像）
- `benchmark/test_bertscore.py` - BERTScore测试脚本
- `benchmark/DATASET_DOWNLOAD_GUIDE.md` - 数据集下载指南

#### 关键改进：
```python
# 断点续传功能
def run_dataset(self, dataset, checkpoint_path=None, resume=True):
    # 自动保存checkpoint（每10个样本）
    # 自动从checkpoint恢复
    # 跳过已完成的样本
```

### 6. 数据集加载改进

#### 修改文件：
- `benchmark/load_datasets.py`
  - 支持HuggingFace镜像（默认使用 `hf-mirror.com`）
  - 支持ModelScope（可选）
  - 自动回退机制（ModelScope → HuggingFace）

### 7. 条件导入和错误处理

#### 修改文件：
- `trag_tree/node.py` - Bloom Filter条件导入
- `trag_tree/hash.py` - Cuckoo Filter条件导入
- `trag_tree/build.py` - 只在 `search_method == 7` 时初始化Cuckoo Filter

#### 改进：
```python
# 条件导入，避免未编译模块导致错误
cuckoo_filter_module = None
try:
    import cuckoo_filter_module
except ImportError:
    pass
```

### 8. 多语言支持

#### 修改文件：
- `rag_base/rag_complete.py`
  - `augment_prompt()` 根据query语言自动选择中英文prompt
  - 支持英文数据集（如AESLC）的英文prompt

### 9. 错误处理和稳定性改进

#### 修改文件：
- `rag_base/rag_complete.py`
  - `rank_contexts()` 增加空列表检查
  - `truncate_to_fit()` 增加fallback机制（tiktoken失败时使用字符截断）
  - 增加异常处理，避免单个样本失败导致整个流程中断

### 10. 文档和说明文件

#### 新增文档：
- `DUAL_SIMILARITY_EXPLANATION.md` - 双重相似度机制详解
- `SIMILARITY_CALCULATION_FLOW.md` - 相似度计算流程说明
- `FILTER_AND_POINTER_ANALYSIS.md` - Filter和指针机制分析
- `CUCKOO_FILTER_USAGE.md` - Cuckoo Filter使用说明
- `benchmark/DATASET_DOWNLOAD_GUIDE.md` - 数据集下载指南

## 📊 性能对比

### Benchmark结果（AESLC数据集）

**改进版本（两个chunk对应一个abstract）**：
- ROUGE-L: 13.45% ⬆️
- BERTScore: 81.45%

**原始版本**：
- ROUGE-L: 7.44%

**改进幅度**：ROUGE-L提升约 **80%**

## 🔧 技术细节

### 向量数据库API变更
```python
# 旧方式
db = RagVecDB(dim)

# 新方式
db_dir = tempfile.gettempdir() + "/vec_db_temp"
db = RagVecDB(db_dir)
db.create_table_if_not_exists(table_name, dim)
```

### 双重相似度过滤流程
1. 向量数据库检索top-k候选
2. `enrich_results_with_summary_embeddings()` 关联chunk和abstract
3. `filter_contexts_by_dual_threshold()` 双重过滤
4. 返回高质量结果

## 📝 配置变更

### `.env` 文件新增配置
```
ARK_API_KEY=...
BASE_URL=https://ark.cn-beijing.volces.com/api/v3
MODEL_NAME=ep-20251221235820-5h6l2
HF_ENDPOINT=https://hf-mirror.com
```

## 🎯 主要改进点总结

1. ✅ **两个chunk对应一个abstract** - 核心功能改进
2. ✅ **双重相似度过滤** - 提升检索质量
3. ✅ **断点续传** - 提升benchmark测试可靠性
4. ✅ **多指标评估** - ROUGE + BLEU + BERTScore
5. ✅ **ARK API集成** - 支持新的LLM API
6. ✅ **错误处理改进** - 提升系统稳定性
7. ✅ **文档完善** - 详细的使用说明

## 🚀 使用建议

1. 使用改进版本运行benchmark（search_method=2，双重相似度过滤已启用）
2. 使用断点续传功能进行长时间测试
3. 使用综合评估脚本获得完整的评估结果
4. 参考文档了解各个机制的详细原理


