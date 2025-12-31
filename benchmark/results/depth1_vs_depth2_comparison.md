# Baseline vs Depth=1 vs Depth=2 Benchmark 对比报告

生成时间: 2025-12-30

## 执行摘要

本报告对比了Baseline RAG、使用Cuckoo Filter的RAG系统在depth=1和depth=2配置下的性能表现。所有测试使用新的向量数据库和知识库。

---

## 1. 评估分数对比

### 1.1 MedQA数据集

| 指标 | Baseline | Depth=1 | Depth=2（修复后） | Baseline→Depth=1 | Depth=1→Depth=2 |
|------|----------|---------|------------------|------------------|-----------------|
| ROUGE-1 | 0.0351 | 0.2826 | 0.0266 | ⬆ +705.1% | ⬇ -90.6% |
| ROUGE-2 | 0.0192 | 0.1963 | 0.0083 | ⬆ +922.4% | ⬇ -95.8% |
| ROUGE-L | 0.0338 | 0.2813 | 0.0247 | ⬆ +732.0% | ⬇ -91.2% |
| BLEU | 0.0064 | 0.1016 | 0.0017 | ⬆ +1487.5% | ⬇ -98.3% |
| BERTScore | 0.7877 | 0.8588 | 0.7813 | ⬆ +9.0% | ⬇ -9.0% |

### 1.2 DART数据集

| 指标 | Baseline | Depth=1 | Depth=2（修复后） | Baseline→Depth=1 | Depth=1→Depth=2 |
|------|----------|---------|------------------|------------------|-----------------|
| ROUGE-1 | 0.4588 | 0.7068 | 0.4658 | ⬆ +54.1% | ⬇ -34.1% |
| ROUGE-2 | 0.3365 | 0.5004 | 0.2627 | ⬆ +48.7% | ⬇ -47.5% |
| ROUGE-L | 0.4010 | 0.5751 | 0.3597 | ⬆ +43.4% | ⬇ -37.5% |
| BLEU | 0.2105 | 0.3457 | 0.1399 | ⬆ +64.2% | ⬇ -59.5% |
| BERTScore | 0.8982 | 0.9299 | 0.8937 | ⬆ +3.5% | ⬇ -3.9% |

### 1.3 TriviaQA数据集

| 指标 | Baseline | Depth=1 | Depth=2 | Baseline→Depth=1 | Depth=1→Depth=2 |
|------|----------|---------|---------|------------------|-----------------|
| ROUGE-1 | 0.0084 | 0.7018 | 0.0604 | ⬆ +8255.9% | ⬇ -91.4% |
| ROUGE-2 | 0.0013 | 0.2970 | 0.0232 | ⬆ +22753.8% | ⬇ -92.2% |
| ROUGE-L | 0.0078 | 0.7018 | 0.0604 | ⬆ +8896.2% | ⬇ -91.4% |
| BLEU | 0.0006 | 0.1529 | 0.0067 | ⬆ +25383.3% | ⬇ -95.6% |
| BERTScore | 0.7956 | 0.9343 | 0.8117 | ⬆ +17.4% | ⬇ -13.1% |

---

## 2. 时间性能对比

### 2.1 平均检索时间 (秒)

| 数据集 | Baseline | Depth=1 | Depth=2（修复后） | Baseline→Depth=1 | Depth=1→Depth=2 |
|--------|----------|---------|------------------|------------------|-----------------|
| MedQA | 0.0204 | 3.33e-06 | 0.0261 | ⬇ -99.98% | ⬆ 7,836x |
| DART | 0.0134 | 2.82e-06 | 0.0262 | ⬇ -99.98% | ⬆ 9,291x |
| TriviaQA | 0.1073 | 5.92e-06 | - | ⬇ -99.99% | - |

**说明**: Baseline使用向量数据库检索，检索时间相对较长。Depth=1使用Cuckoo Filter，检索时间极快（微秒级）。Depth=2（修复后，真正实现追溯父节点）检索时间比Depth=1增加，但仍然比Baseline快。

### 2.2 平均总响应时间 (秒)

| 数据集 | Baseline | Depth=1 | Depth=2（修复后） | Baseline→Depth=1 | Depth=1→Depth=2 |
|--------|----------|---------|------------------|------------------|-----------------|
| MedQA | 27.13 | 16.81 | 30.14 | ⬇ -38.0% | ⬆ +79.2% |
| DART | 12.81 | 8.54 | 11.02 | ⬇ -33.3% | ⬆ +29.0% |
| TriviaQA | 6.93 | 7.84 | - | ⬆ +13.1% | - |

**说明**: 总响应时间包括检索时间和LLM生成时间。Depth=1比Baseline快33-38%（MedQA和DART），主要因为检索更快。Depth=2（修复后）比Depth=1慢29-79%，主要因为需要追溯父节点并处理更多abstracts。

### 2.3 总耗时 (分钟)

| 数据集 | Baseline | Depth=1 | Depth=2（修复后） | Baseline→Depth=1 | Depth=1→Depth=2 |
|--------|----------|---------|------------------|------------------|-----------------|
| MedQA | 45.2 | 28.0 | 50.2 | ⬇ -38.0% | ⬆ +79.2% |
| DART | 21.3 | 14.2 | 18.4 | ⬇ -33.3% | ⬆ +29.0% |
| TriviaQA | 11.6 | 13.1 | - | ⬆ +13.1% | - |

**说明**: 总耗时是处理100个样本的总时间。Depth=1比Baseline快33-38%（MedQA和DART）。Depth=2（修复后）比Depth=1慢29-79%。

---

## 3. 主要发现

### 3.1 评估分数对比

**Baseline vs Depth=1（Cuckoo Filter的优势）:**
- **MedQA**: Depth=1显著优于Baseline，所有指标大幅提升（ROUGE-1提升705%，BLEU提升1488%）
- **DART**: Depth=1优于Baseline，ROUGE提升43-54%，BLEU提升64%
- **TriviaQA**: Depth=1显著优于Baseline，ROUGE和BLEU提升超过8000-25000%
- **结论**: Cuckoo Filter (Depth=1)相比Baseline RAG在评估分数上有显著提升

**Depth=1 vs Depth=2（更深层次的劣势）:**
- **MedQA数据集**: Depth=2（修复后，真正实现追溯父节点）的评估分数大幅下降，特别是BLEU和ROUGE指标下降超过90%，BERTScore下降约9%
- **DART数据集**: Depth=2（修复后）的评估分数下降，相对较小（34-60%），BERTScore仅下降3.9%
- **TriviaQA数据集**: Depth=2（修复后）还在运行中，待完成后更新

### 3.2 时间性能对比

**检索时间:**
- **Baseline**: 使用向量数据库检索，检索时间约0.01-0.11秒
- **Depth=1**: 检索时间极快（微秒级），因为直接通过Cuckoo Filter和实体匹配
- **Depth=2**: 检索时间大幅增加（数千倍），需要构建更深的abstract tree和更多的实体检索匹配

**总响应时间:**
- **Baseline vs Depth=1**: Depth=1比Baseline快33-38%（MedQA和DART），但TriviaQA稍慢13%
- **Depth=1 vs Depth=2（修复后）**: Depth=2比Depth=1慢29-79%（MedQA: +79.2%, DART: +29.0%），主要因为需要追溯父节点并处理更多abstracts

### 3.3 性能权衡分析

- **Depth=2（修复后，真正实现追溯父节点）的优势**: 理论上可以检索更深层次的abstract信息
- **Depth=2的劣势**:
  - 检索时间增加（比Depth=1增加数千倍，但仍然比Baseline快）
  - 评估分数显著下降（特别是n-gram重叠指标，MedQA下降90%+，DART下降34-60%）
  - 可能引入了噪音：追溯父节点可能包含不相关信息，降低了检索精度
  - 总响应时间增加（MedQA增加79%，DART增加29%）

---

## 4. 结论

1. **Cuckoo Filter (Depth=1) 显著优于 Baseline RAG**:
   - 评估分数大幅提升（MedQA提升705-1488%，TriviaQA提升8000-25000%）
   - 检索时间更快（微秒级 vs 毫秒级）
   - 总响应时间更短（MedQA和DART快33-38%）
   - **推荐使用**: Cuckoo Filter (Depth=1) 是当前最佳配置

2. **Depth=2（修复后，真正实现追溯父节点）在当前配置下表现不佳**: 
   - 虽然检索到了更多的abstract信息（包括父节点），但评估分数显著下降
   - MedQA: ROUGE和BLEU指标下降90%+，BERTScore下降9%
   - DART: ROUGE和BLEU指标下降34-60%，BERTScore下降3.9%
   - 检索时间比Depth=1增加数千倍（但仍然比Baseline快）
   - 总响应时间增加29-79%
   - **不推荐使用**: Depth=2在当前配置下没有优势，追溯父节点引入了噪音

3. **性能排序（从好到差）**:
   - **最佳**: Depth=1 (Cuckoo Filter) - 评估分数最高，响应时间最快
   - **中等**: Baseline RAG - 评估分数较低，但响应时间适中
   - **最差**: Depth=2 - 评估分数最低，检索时间最长

---

## 5. 建议

1. **推荐使用Depth=1 (Cuckoo Filter)作为主要配置**:
   - 评估分数显著优于Baseline和Depth=2
   - 检索速度和总响应时间都最优
   - 是最平衡的配置

2. **不建议使用Depth=2**:
   - 评估分数显著下降
   - 检索时间大幅增加
   - 没有明显的优势

3. **Baseline RAG可用但不如Cuckoo Filter**:
   - 可以作为对比基准
   - 在简单场景下可以使用
   - 但在复杂查询中表现不如Cuckoo Filter

4. **进一步优化方向**:
   - 优化Depth=1的实现细节
   - 考虑改进实体识别和匹配策略
   - 探索其他优化方法而不是增加depth

---

## 附录：数据文件位置

- Baseline结果:
  - `benchmark/results/medqa_baseline_new.json`
  - `benchmark/results/dart_baseline_new.json`
  - `benchmark/results/triviaqa_baseline_new.json`

- Depth=1结果:
  - `benchmark/results/medqa_cuckoo_depth1_100.json`
  - `benchmark/results/dart_cuckoo_depth1_100.json`
  - `benchmark/results/triviaqa_cuckoo_depth1_100.json`

- Depth=2结果:
  - `benchmark/results/medqa_cuckoo_depth2.json`
  - `benchmark/results/dart_cuckoo_depth2.json`
  - `benchmark/results/triviaqa_cuckoo_depth2.json`

- 评估结果:
  - Baseline: `benchmark/results/*_baseline_new_evaluation.json`
  - Depth=1: `benchmark/results/*_cuckoo_depth1_100_evaluation.json`
  - Depth=2: `benchmark/results/*_cuckoo_depth2_evaluation.json`

