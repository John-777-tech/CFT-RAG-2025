# Benchmark结果汇总报告

## 实验配置

- **方法**: Cuckoo Filter Abstract RAG（新架构）
- **Search Method**: 7
- **样本数**: 100
- **Depth**: 1 和 2
- **数据集**: MedQA, DART, TriviaQA

## 结果汇总表

| 数据集 | Depth | 完成数 | ROUGE-L | BLEU | BERTScore | 平均时间(s) | 总时间(s) |
|--------|-------|--------|---------|------|-----------|-------------|-----------|
| medqa | 1 | - | - | - | - | - | - |
| medqa | 2 | 100 | - | - | - | 15.42 | 1542.04 |
| dart | 1 | 100 | - | - | - | 7.20 | 719.93 |
| dart | 2 | 100 | - | - | - | 6.49 | 649.23 |
| triviaqa | 1 | 100 | - | - | - | 10.43 | 1043.42 |
| triviaqa | 2 | 100 | - | - | - | 7.40 | 740.38 |

## 时间性能分析

### MedQA
- Depth=2: 平均 15.42秒/样本

### DART
- Depth=1: 平均 7.20秒/样本
- Depth=2: 平均 6.49秒/样本
- **改进**: Depth=2 比 Depth=1 快 9.9%

### TriviaQA
- Depth=1: 平均 10.43秒/样本
- Depth=2: 平均 7.40秒/样本
- **改进**: Depth=2 比 Depth=1 快 29.1%

## 评估分数

评估分数需要从评估文件中读取，格式为：
```json
{
  "average_scores": {
    "rougeL": ...,
    "bleu": ...,
    "bertscore": ...
  }
}
```

## 运行状态

- ✓ medqa depth=2: 已完成
- ⏳ medqa depth=1: 运行中
- ✓ dart depth=1: 已完成
- ✓ dart depth=2: 已完成
- ✓ triviaqa depth=1: 已完成
- ✓ triviaqa depth=2: 已完成

## 新架构特性

所有实验使用新架构：
- AbstractTree构建（从向量数据库读取abstracts）
- Entity到Abstract映射建立
- Cuckoo Filter地址映射更新（C++层，使用Abstract的pair_id）
- 使用Abstract地址而非Entity地址进行查询



