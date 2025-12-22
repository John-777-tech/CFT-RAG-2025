# Benchmark测试完整指南

## 📊 项目中的Benchmark测试方法

### 1. README.md中的说明（虽然被注释，但包含重要信息）

**测试指标：**
- **Average Retrieval Time**: 平均检索时间（在36个问题上的平均值）
- **Time Ratio**: 检索时间占总响应时间的比例 (检索时间 / (检索时间 + 推理时间))
- **Accuracy**: 使用LangSmith评估模型回答的准确率

**测试数据集：**
- MedQA: https://github.com/jind11/MedQA
- AESLC: https://huggingface.co/datasets/Yale-LILY/aeslc
- DART: https://github.com/Yale-LILY/dart
- Rui'an People's Hospital: https://www.rahos.gov.cn

### 2. 原始测试方法：langsmith/langsmith_test.py

**工作原理：**
```python
# 1. 加载向量数据库和实体树
vec_db = load_vec_db(vec_db_key, "vec_db_cache/")
forest, nlp = build.build_forest(tree_num_max, entities_file_name, search_method, node_num_max)

# 2. 创建RagBot类，包含retrieve_docs和get_answer方法
rag_bot = RagBot()

# 3. 使用LangSmith的evaluate函数进行评估
experiment_results = evaluate(
    predict_rag_answer,           # 预测函数
    data="t-rag-new",             # LangSmith平台上的数据集名称
    evaluators=[SimpleStringEvaluator()],  # 评估器
    experiment_prefix="...",      # 实验前缀
)
```

**评估器（SimpleStringEvaluator）：**
- 简单的字符串相似度评分
- 如果预测回答包含期望答案的关键内容：评分0.9
- 否则：评分0.5

**运行方式：**
```bash
python langsmith/langsmith_test.py --tree-num-max 50 --search-method 7
```

**要求：**
- 需要在LangSmith平台创建数据集"t-rag-new"
- 数据集需要包含"prompt"（问题）和"answer"（期望答案）字段
- 需要配置LANGCHAIN_API_KEY环境变量

### 3. 本地测试方法：benchmark/run_benchmark.py

**工作原理：**
- 从本地JSON文件加载数据集
- 直接调用RAG系统获取回答
- 记录响应时间和结果
- 保存结果到JSON文件

**运行方式：**
```bash
# 使用AESLC数据集
python benchmark/run_benchmark.py \
    --dataset ./datasets/processed/aeslc.json \
    --vec-db-key "test" \
    --tree-num-max 50 \
    --search-method 2 \
    --max-samples 20
```

**优势：**
- 不依赖LangSmith平台
- 可以使用论文中提到的公开数据集
- 更灵活，可以自定义评估逻辑

## 🔄 两种测试方法的对比

| 特性 | LangSmith方法 | 本地方法 |
|------|--------------|---------|
| 平台依赖 | 需要LangSmith账号 | 无依赖 |
| 数据集 | LangSmith平台上的数据集 | 本地JSON文件 |
| 评估 | LangSmith的evaluator | 自定义评估逻辑 |
| 结果查看 | LangSmith平台 | 本地JSON文件 |
| 适合场景 | 正式评估、对比实验 | 快速测试、开发调试 |

## 📈 论文中的Benchmark结果参考

从README.md（虽然被注释）可以看到论文中的测试结果：

**MedQA数据集：**
- CF T-RAG: 检索时间5.04s, 时间比率15%, 准确率68%
- 对比：Naive T-RAG: 检索时间18.37s, 时间比率56%, 准确率68%

**AESLC数据集：**
- CF T-RAG: 检索时间0.95s, 时间比率5%, 准确率56%
- 对比：Naive T-RAG: 检索时间12.11s, 时间比率61%, 准确率56%

**DART数据集：**
- CF T-RAG: 检索时间1.78s, 时间比率8%, 准确率67%
- 对比：Naive T-RAG: 检索时间15.88s, 时间比率72%, 准确率67%

## 💡 建议

1. **开发阶段**：使用本地测试方法（benchmark/run_benchmark.py）快速验证
2. **正式评估**：使用LangSmith方法进行标准化评估和对比
3. **数据集准备**：可以先用本地方法测试，确认无误后再上传到LangSmith
