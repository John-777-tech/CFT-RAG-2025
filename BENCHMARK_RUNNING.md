# AESLC Baseline RAG vs Cuckoo Filter Benchmark 运行状态

## 当前状态

✅ **Benchmark 正在运行中**

脚本 `run_aeslc_baseline_vs_cuckoo.sh` 已在后台启动，正在执行以下任务：

### 任务列表

1. **运行 Baseline RAG (search_method=0)** - 当前进行中
   - 输出: `./benchmark/results/aeslc_baseline_comparison.json`
   - 评估: `./benchmark/results/aeslc_baseline_comparison_evaluation.json`

2. **运行 Cuckoo Filter (search_method=7)**
   - 输出: `./benchmark/results/aeslc_cuckoo_comparison.json`
   - 评估: `./benchmark/results/aeslc_cuckoo_comparison_evaluation.json`

3. **生成对比报告**
   - 输出: `./benchmark/results/aeslc_baseline_vs_cuckoo_comparison.json`

## 监控进度

### 方法1: 使用监控脚本
```bash
bash check_benchmark_progress.sh
```

### 方法2: 查看日志
```bash
tail -f benchmark/results/aeslc_baseline_vs_cuckoo_run.log
```

### 方法3: 检查结果文件
```bash
# 检查Baseline RAG进度
python -c "import json; data=json.load(open('./benchmark/results/aeslc_baseline_comparison.json')); print(f'Baseline: {len(data)}/30')"

# 检查Cuckoo Filter进度
python -c "import json; data=json.load(open('./benchmark/results/aeslc_cuckoo_comparison.json')); print(f'Cuckoo: {len(data)}/30')"
```

## 预期时间

- **向量数据库构建**: 首次运行需要构建，可能需要几分钟
- **Baseline RAG**: ~30个样本 × 平均10-15秒/样本 ≈ 5-8分钟
- **Cuckoo Filter**: ~30个样本 × 平均10-15秒/样本 ≈ 5-8分钟
- **评估**: 每个约1-2分钟

**总预计时间**: 约15-20分钟

## 评估指标

运行完成后，将对比以下指标：

### ROUGE指标
- ROUGE-1 (F1)
- ROUGE-2 (F1)
- ROUGE-L (F1)

### BLEU指标
- BLEU Score

### BERTScore指标
- BERTScore F1

### 时间指标
- 平均响应时间
- 总时间

## 结果文件

运行完成后，将生成以下文件：

1. `benchmark/results/aeslc_baseline_comparison.json` - Baseline RAG结果
2. `benchmark/results/aeslc_baseline_comparison_evaluation.json` - Baseline RAG评估
3. `benchmark/results/aeslc_cuckoo_comparison.json` - Cuckoo Filter结果
4. `benchmark/results/aeslc_cuckoo_comparison_evaluation.json` - Cuckoo Filter评估
5. `benchmark/results/aeslc_baseline_vs_cuckoo_comparison.json` - 对比报告
6. `benchmark/results/aeslc_baseline_vs_cuckoo_run.log` - 运行日志

## 查看最终结果

运行完成后，查看对比报告：
```bash
cat benchmark/results/aeslc_baseline_vs_cuckoo_comparison.json | python -m json.tool
```

或使用Python查看：
```python
import json
with open('benchmark/results/aeslc_baseline_vs_cuckoo_comparison.json') as f:
    data = json.load(f)
    print(json.dumps(data, indent=2, ensure_ascii=False))
```

