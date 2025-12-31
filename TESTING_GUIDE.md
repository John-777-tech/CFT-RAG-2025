# 测试指南：两个chunk对应一个abstract的benchmark测试

## 已完成的修改

### 1. `rag_base/build_index.py`
- ✅ `expand_chunks_to_tree_nodes` 函数已实现：**每两个chunk对应一个abstract (tree_node)**
- 逻辑：chunk_id为i和i+1的chunks共享pair_id为i//2的tree_node

### 2. `rag_base/rag_complete.py` 
- ✅ 添加了 `enrich_results_with_summary_embeddings` 函数
  - 为每个raw_chunk找到对应的tree_node（通过chunk_id // 2计算pair_id）
  - 将tree_node的embedding作为summary_embedding添加到结果中
  - 支持dual-threshold过滤（同时检查chunk和summary的相似度）

- ✅ 修改了 `augment_prompt` 函数
  - 检索时使用更大的k值（k * 3）以确保检索到足够的chunks和summaries
  - 检索后调用enrich_results_with_summary_embeddings来关联chunk和abstract
  - 然后进行dual-threshold过滤

### 3. `langsmith/langsmith_test.py`
- ✅ 修复了导入路径：`src.build_index` → `rag_base.build_index`
- ✅ 修复了导入路径：`src.rag_complete` → `rag_base.rag_complete`

## 运行测试前的准备

### 1. 安装依赖

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# 如果使用uv（推荐）
pip install uv
uv sync
pip install lab-1806-vec-db==0.2.3 python-dotenv sentence-transformers openai pybloom_live

# 或者直接使用pip
pip install lab-1806-vec-db==0.2.3 python-dotenv sentence-transformers openai pybloom_live

# 设置HuggingFace镜像（可选，如果下载模型慢）
export HF_ENDPOINT=https://hf-mirror.com

# 下载spacy中文模型
python -m spacy download zh_core_web_sm
```

### 2. 配置环境变量

创建 `.env` 文件（或复制 `.env.example`）：

```bash
OPENAI_API_KEY=YOUR_API_KEY
# 或使用ARK API
ARK_API_KEY=YOUR_ARK_API_KEY
MODEL_NAME=gpt-4o-mini  # 可选
EMBED_MODEL_NAME=  # 可选
```

## 运行测试

### 方式1：使用main.py进行简单测试

```bash
python main.py --tree-num-max 50 --search-method 7 --vec-db-key "your_key"
```

### 方式2：使用langsmith进行benchmark测试

```bash
python langsmith/langsmith_test.py --tree-num-max 50 --search-method 7
```

参数说明：
- `--tree-num-max`: 构建的最大树数量（默认50）
- `--search-method`: 搜索方法
  - `0`: 仅向量数据库
  - `1`: 朴素Tree-RAG
  - `2`: Bloom Filter Tree-RAG
  - `7`: Cuckoo Filter Tree-RAG（推荐）
- `--vec-db-key`: 向量数据库的key
- `--entities-file-name`: 实体文件名

## 验证修改是否生效

修改的关键点：
1. **两个chunk共享一个abstract**：在`expand_chunks_to_tree_nodes`中，pair_id = chunk_id // 2
2. **检索时关联abstract**：在`enrich_results_with_summary_embeddings`中，通过pair_id找到对应的tree_node embedding
3. **双重相似度过滤**：同时检查query与chunk的相似度和query与summary的相似度

## 预期效果

通过让两个chunk对应一个abstract，预期可以：
- 提高检索的准确度（通过abstract级别的相似度过滤）
- 保持或提升benchmark性能指标
- 减少噪声（不相关的chunks会被abstract过滤掉）





