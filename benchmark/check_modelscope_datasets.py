#!/usr/bin/env python
"""检查ModelScope上是否有MedQA和DART数据集"""

import sys
import os

print("=" * 80)
print("检查ModelScope上的数据集")
print("=" * 80)

try:
    from modelscope.msdatasets import MsDataset
    print("✓ ModelScope已安装\n")
except ImportError:
    print("✗ ModelScope未安装")
    print("请运行: pip install modelscope")
    sys.exit(1)

# 常见的数据集ID（需要根据实际情况调整）
datasets_to_check = [
    "MedQA",
    "DART", 
    "aeslc",
    "medical_qa",
    "medqa",
]

print("搜索ModelScope上的数据集...\n")

# ModelScope数据集搜索（通常需要通过网站搜索，这里尝试常见的ID）
print("注意：ModelScope数据集ID可能与HuggingFace不同")
print("建议访问 https://modelscope.cn/datasets 搜索数据集\n")

# 尝试加载一些常见的数据集ID
test_ids = [
    "Yale-LILY/aeslc",  # AESLC
    "dart",             # DART
    "medqa",            # MedQA
]

for dataset_id in test_ids:
    print(f"尝试加载: {dataset_id}")
    try:
        # 只尝试加载元数据，不加载完整数据
        dataset = MsDataset.load(dataset_id, subset_name="default", split="test", download_mode="FORCE_REDOWNLOAD")
        print(f"  ✓ 找到数据集: {dataset_id}")
        print(f"  样本数: {len(dataset) if hasattr(dataset, '__len__') else '未知'}")
    except Exception as e:
        print(f"  ✗ 未找到或加载失败: {str(e)[:100]}")
    print()

print("=" * 80)
print("提示：")
print("1. ModelScope数据集ID可能与HuggingFace不同")
print("2. 访问 https://modelscope.cn/datasets 搜索具体的数据集")
print("3. 找到后可以使用正确的数据集ID")
print("=" * 80)


