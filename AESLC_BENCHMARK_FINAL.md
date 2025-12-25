# AESLC Baseline RAG vs Cuckoo Filter Abstract RAG 对比实验

## 实验目标

对比两种RAG方法在AESLC数据集上的性能：
1. **Baseline RAG** (search_method=0): 仅使用向量数据库的标准RAG
2. **Cuckoo Filter Abstract RAG** (search_method=7): 使用Cuckoo Filter和实体树的增强RAG

## 实验配置

- **数据集**: AESLC (30个样本用于快速测试)
- **Baseline RAG**: `search_method=0`
- **Cuckoo Filter Abstract RAG**: `search_method=7`
- **评估指标**: ROUGE-1, ROUGE-2, ROUGE-L, BLEU, BERTScore F1
- **向量数据库**: 已成功构建（2859个向量）

## 运行状态

### 当前状态
- ✅ 向量数据库已构建成功（2859个向量）
- ⏳ Benchmark正在运行中...

### 检查进度

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
./check_aeslc_benchmark_progress.sh
```

### 查看运行日志

```bash
tail -f benchmark/results/aeslc_baseline_vs_cuckoo_final_run.log
```

## 结果文件

运行完成后，将生成以下文件：

1. **Baseline RAG结果**: `./benchmark/results/aeslc_baseline_final.json`
2. **Baseline RAG评估**: `./benchmark/results/aeslc_baseline_final_evaluation.json`
3. **Cuckoo Filter结果**: `./benchmark/results/aeslc_cuckoo_final.json`
4. **Cuckoo Filter评估**: `./benchmark/results/aeslc_cuckoo_final_evaluation.json`
5. **对比报告**: `./benchmark/results/aeslc_baseline_vs_cuckoo_final_report.json`

## 查看结果

### 查看对比报告

```bash
cat ./benchmark/results/aeslc_baseline_vs_cuckoo_final_report.json | python -m json.tool
```

### 查看详细评估结果

```bash
# Baseline RAG
cat ./benchmark/results/aeslc_baseline_final_evaluation.json | python -m json.tool

# Cuckoo Filter
cat ./benchmark/results/aeslc_cuckoo_final_evaluation.json | python -m json.tool
```

## 预期输出

对比报告将包含：

1. **评估指标对比**
   - ROUGE-1, ROUGE-2, ROUGE-L F1分数
   - BLEU分数
   - BERTScore F1分数
   - 各指标的差异

2. **时间性能对比**
   - Baseline RAG平均响应时间
   - Cuckoo Filter平均响应时间
   - 时间差异和百分比

3. **样本统计**
   - 总样本数
   - 成功样本数
   - 错误样本数

## 注意事项

1. **向量数据库**: 已成功构建，包含2859个向量
2. **API调用**: 确保已配置API密钥（OPENAI_API_KEY或ARK_API_KEY）
3. **运行时间**: 30个样本的benchmark可能需要10-30分钟
4. **完整测试**: 如需完整测试，可以修改脚本中的`--max-samples`参数

## 如果benchmark失败

1. 检查日志文件：`benchmark/results/aeslc_baseline_vs_cuckoo_final_run.log`
2. 检查向量数据库：确保`vec_db_cache/aeslc.db`存在且有数据
3. 检查API密钥：确保`.env`文件中配置了正确的API密钥
4. 重新运行：删除结果文件后重新运行脚本

