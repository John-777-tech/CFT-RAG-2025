# Benchmark最终完整汇总报告

## 完整结果汇总表（Cuckoo Filter vs Baseline）

| 数据集 | 方法 | Depth | 完成数 | ROUGE-L | BLEU | BERTScore | 总时间(s) | 检索时间(s) | 生成时间(s) | 检索占比 |
|--------|------|-------|--------|---------|------|-----------|-----------|-------------|-------------|----------|
| **MedQA** | Cuckoo Filter | 1 | 100 | 0.3155 | 0.1144 | 0.8656 | 19.0337 | 0.0676 | 19.0087 | 0.36% |
| **MedQA** | Cuckoo Filter | 2 | 100 | 0.3058 | 0.1148 | 0.8572 | 15.4204 | 0.0409 | 15.3983 | 0.27% |
| **MedQA** | Baseline RAG | - | 100 | 0.0331 | 0.0064 | 0.7843 | 41.2096 | 0.2626 | 41.1826 | 0.64% |
| **DART** | Cuckoo Filter | 1 | 100 | 0.6003 | 0.3805 | 0.9328 | 7.1993 | 0.0378 | 7.1724 | 0.52% |
| **DART** | Cuckoo Filter | 2 | 100 | 0.6070 | 0.3861 | 0.9335 | 6.4923 | 0.0232 | 6.4732 | 0.36% |
| **DART** | Baseline RAG | - | 100 | 0.4195 | 0.2222 | 0.9004 | 17.8217 | 0.3350 | 17.7955 | 1.88% |
| **TriviaQA** | Cuckoo Filter | 1 | 100 | 0.6700 | 0.1535 | 0.9290 | 10.4342 | 0.0215 | 10.4068 | 0.21% |
| **TriviaQA** | Cuckoo Filter | 2 | 100 | 0.6949 | 0.1527 | 0.9311 | 7.4038 | 0.0132 | 7.3806 | 0.18% |
| **TriviaQA** | Baseline RAG | - | 100 | 0.0353 | 0.0032 | 0.8106 | 19.0923 | 5.6207 | 19.0657 | 29.44% |

*注：所有实验已完成

**注意**: Baseline RAG是depth-agnostic的，可以使用depth=2的baseline结果与所有depth的实验进行对比。

## 关键发现

### 1. 时间性能对比（Cuckoo vs Baseline）

**总时间加速**:
- MedQA: 62.6% ⚡
- DART: ~60% ⚡
- TriviaQA: 45-61% ⚡

**检索时间加速**:
- MedQA: 84.4% ⚡
- DART: ~90% ⚡
- TriviaQA: ~99.8% ⚡

### 2. Depth=1 vs Depth=2对比

**MedQA**:
- 总时间: Depth=1 (19.03s) → Depth=2 (15.42s) → **-19.0%** ⚡
- 检索时间: Depth=1 (0.0676s) → Depth=2 (0.0409s) → **-39.5%** ⚡
- 生成时间: Depth=1 (19.01s) → Depth=2 (15.40s) → **-19.0%** ⚡

**DART**:
- 总时间: Depth=1 (7.20s) → Depth=2 (6.49s) → **-9.82%** ⚡
- 检索时间: Depth=1 (0.0378s) → Depth=2 (0.0232s) → **-38.60%** ⚡
- 生成时间: Depth=1 (7.17s) → Depth=2 (6.47s) → **-9.75%** ⚡

**TriviaQA**:
- 总时间: Depth=1 (10.43s) → Depth=2 (7.40s) → **-29.04%** ⚡
- 检索时间: Depth=1 (0.0215s) → Depth=2 (0.0132s) → **-38.54%** ⚡
- 生成时间: Depth=1 (10.41s) → Depth=2 (7.38s) → **-29.08%** ⚡

### 3. 评估分数

**MedQA**: Depth=1在所有指标上略优（ROUGE-L +3.1%, BLEU -0.3%, BERTScore +1.0%）
**DART**: Depth=2在所有指标上略优（ROUGE-L +1.1%, BLEU +1.5%, BERTScore +0.08%）
**TriviaQA**: Depth=2在ROUGE-L和BERTScore上更好（ROUGE-L +3.7%, BERTScore +0.23%）

## 运行状态

- ✅ 所有实验已完成（6个Cuckoo Filter实验 + 3个Baseline实验）

## 详细报告

- `COMPLETE_BENCHMARK_REPORT.md` - 完整时间分析
- `FINAL_COMPLETE_REPORT.md` - 最终完整报告

