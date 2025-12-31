# AESLC Baseline RAG vs Cuckoo Filter 对比实验

## 实验目标

对比Baseline RAG和Cuckoo Filter RAG在AESLC数据集上的性能，包括：
- ROUGE-1, ROUGE-2, ROUGE-L 指标
- BLEU 指标
- BERTScore 指标
- 平均响应时间

## 实验配置

- **数据集**: AESLC (30个样本用于快速测试)
- **Baseline RAG**: `search_method=0` (仅使用向量数据库)
- **Cuckoo Filter RAG**: `search_method=7` (使用Cuckoo Filter + 实体树)
- **评估指标**: ROUGE, BLEU, BERTScore

## 运行方法

### 自动运行完整对比

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
./run_aeslc_baseline_vs_cuckoo_comparison.sh
```

### 监控进度

```bash
./monitor_aeslc_comparison.sh
```

### 手动检查进度

```bash
python -c "
import json, os
baseline_file = './benchmark/results/aeslc_baseline_comparison.json'
cuckoo_file = './benchmark/results/aeslc_cuckoo_comparison.json'

if os.path.exists(baseline_file):
    baseline_data = json.load(open(baseline_file, 'r', encoding='utf-8'))
    print(f'Baseline RAG: {len(baseline_data)}/30 完成')
else:
    print('Baseline RAG: 尚未开始')

if os.path.exists(cuckoo_file):
    cuckoo_data = json.load(open(cuckoo_file, 'r', encoding='utf-8'))
    print(f'Cuckoo Filter: {len(cuckoo_data)}/30 完成')
else:
    print('Cuckoo Filter: 尚未开始')
"
```

## 结果文件

- **Baseline RAG结果**: `./benchmark/results/aeslc_baseline_comparison.json`
- **Baseline RAG评估**: `./benchmark/results/aeslc_baseline_comparison_evaluation.json`
- **Cuckoo Filter结果**: `./benchmark/results/aeslc_cuckoo_comparison.json`
- **Cuckoo Filter评估**: `./benchmark/results/aeslc_cuckoo_comparison_evaluation.json`
- **对比报告**: `./benchmark/results/aeslc_baseline_vs_cuckoo_comparison_report.json`

## 查看结果

### 查看对比报告

```bash
cat ./benchmark/results/aeslc_baseline_vs_cuckoo_comparison_report.json | python -m json.tool
```

### 查看详细评估结果

```bash
# Baseline RAG
cat ./benchmark/results/aeslc_baseline_comparison_evaluation.json | python -m json.tool

# Cuckoo Filter
cat ./benchmark/results/aeslc_cuckoo_comparison_evaluation.json | python -m json.tool
```

## 当前状态

- ✅ Baseline RAG: 已完成 (30/30样本)
- ✅ Baseline RAG评估: 已完成
- ⏳ Cuckoo Filter: 运行中...
- ⏳ 对比报告: 等待Cuckoo Filter完成

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

3. **分析**
   - 哪个方法在质量指标上表现更好
   - 哪个方法在速度上更快
   - 综合性能评估

## 注意事项

1. **首次运行**: 向量数据库会在首次运行时自动构建，可能需要一些时间
2. **API调用**: 确保已配置API密钥（OPENAI_API_KEY或ARK_API_KEY）
3. **样本数量**: 当前使用30个样本进行快速测试，可以修改脚本中的`--max-samples`参数调整
4. **完整测试**: 如需完整测试，可以修改为使用全部1906个样本




