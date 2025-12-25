# 问题回答总结

## 1. 两个chunk对应一个abstract vs 一个chunk对应一个abstract

### 推荐：两个chunk对应一个abstract ✅

**优点**：
1. **语义完整性更好**：两个chunk合并后能提供更完整的上下文，特别适合摘要任务
2. **双重过滤机制**：dual-threshold同时检查chunk和summary相似度，过滤更精确
3. **存储效率**：减少50%的abstract节点，节省存储空间
4. **减少噪声**：abstract级别的过滤可以去除不相关的chunks

**缺点**：
- 如果两个chunk语义差异很大，合并可能不够精确

**结论**：对于AESLC邮件摘要任务，推荐使用"两个chunk对应一个abstract"，因为：
- 邮件内容通常语义完整
- 摘要任务需要整体理解，不需要精确到单个句子
- 双重过滤机制可以提高检索质量

## 2. 数据集语言

✅ **AESLC数据集是英文的**
- 所有邮件正文都是英文
- 需要将prompt改为英文

✅ **已修改**：
- `benchmark/load_datasets.py`：prompt改为 "Summarize the following email: {subject}"
- `rag_base/rag_complete.py`：根据query自动判断使用英文或中文prompt

## 3. 评估方法（除了LangSmith）

### 3.1 ROUGE指标 ⭐推荐

**最适合摘要任务的标准评估指标**

优点：
- ✅ 专门为摘要任务设计
- ✅ 不需要外部服务
- ✅ 计算速度快
- ✅ 学术标准，可复现

已创建：`benchmark/evaluate_with_rouge.py`

使用方法：
```bash
pip install rouge-score
python benchmark/evaluate_with_rouge.py --results ./benchmark/results/aeslc_results_2.json
```

### 3.2 BLEU指标

- 主要用于机器翻译，也可用于摘要
- 不如ROUGE适合摘要任务

### 3.3 BERTScore

- 使用BERT计算语义相似度
- 更准确，但计算较慢

### 3.4 自定义LLM评估（项目中使用）

- 使用LLM评估相似度（0-100分）
- 需要API调用，成本高

## 4. 下一步建议

1. **重新运行测试（使用英文prompt）**：
   ```bash
   # 重新加载数据集（会使用英文prompt）
   python benchmark/load_datasets.py --dataset aeslc
   
   # 重新运行benchmark
   python benchmark/run_benchmark.py \
       --dataset ./datasets/processed/aeslc.json \
       --vec-db-key aeslc \
       --entities-file-name aeslc_entities_file \
       --tree-num-max 50 \
       --search-method 2 \
       --max-samples 36
   ```

2. **使用ROUGE评估**：
   ```bash
   pip install rouge-score
   python benchmark/evaluate_with_rouge.py --results ./benchmark/results/aeslc_results.json
   ```

3. **对比两种方法的效果**：
   - 运行"两个chunk对应一个abstract"的测试
   - 修改代码为"一个chunk对应一个abstract"
   - 对比ROUGE分数
