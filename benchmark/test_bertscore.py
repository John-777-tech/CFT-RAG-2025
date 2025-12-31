#!/usr/bin/env python
"""测试BERTScore是否能正常工作"""

import sys

print("=" * 80)
print("测试BERTScore")
print("=" * 80)

try:
    import bert_score
    print("✓ bert_score模块已导入")
except ImportError:
    print("✗ bert_score未安装，请运行: pip install bert-score")
    sys.exit(1)

# 测试小样本
predictions = [
    "The email informs that expense reports are awaiting your approval.",
    "The necessary email content is not provided."
]
references = [
    "The following reports have been waiting for your approval for more than 4 days.",
    "Email content is missing."
]

print(f"\n测试样本数: {len(predictions)}")
print("\n正在计算BERTScore...")
print("⚠️  首次运行需要下载BERT模型（roberta-large，约1.3GB）")
print("⚠️  这可能需要10-20分钟，请耐心等待...")
print("\n预测样本:")
for i, p in enumerate(predictions, 1):
    print(f"  {i}. {p}")
print("\n参考样本:")
for i, r in enumerate(references, 1):
    print(f"  {i}. {r}")

try:
    P, R, F1 = bert_score.score(
        predictions,
        references,
        lang='en',
        verbose=True,  # 显示进度
        batch_size=2,
        device='cpu'
    )
    
    print(f"\n{'='*80}")
    print("✓ BERTScore计算成功！")
    print(f"{'='*80}")
    print(f"\n结果:")
    print(f"  Precision (P): {P.tolist()}")
    print(f"  Recall (R): {R.tolist()}")
    print(f"  F1: {F1.tolist()}")
    print(f"\n平均分数:")
    print(f"  平均P: {P.mean().item():.4f}")
    print(f"  平均R: {R.mean().item():.4f}")
    print(f"  平均F1: {F1.mean().item():.4f}")
    print(f"\n{'='*80}")
    print("✓ BERTScore已准备好，可以运行完整评估了！")
    print(f"{'='*80}")
    
except Exception as e:
    print(f"\n✗ 计算错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)





