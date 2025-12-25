#!/usr/bin/env python
"""从ModelScope下载BERTScore需要的模型"""

import os
import sys

print("=" * 80)
print("从ModelScope下载BERTScore模型")
print("=" * 80)

try:
    from modelscope import snapshot_download
    print("✓ modelscope已安装")
except ImportError:
    print("✗ modelscope未安装")
    print("请运行: pip install modelscope")
    sys.exit(1)

# BERTScore默认使用roberta-large模型
# ModelScope上的roberta-large模型
model_id = "AI-ModelScope/roberta-large"

# 下载到本地目录
cache_dir = os.path.expanduser("~/.cache/modelscope/roberta-large")
print(f"\n模型ID: {model_id}")
print(f"下载目录: {cache_dir}")
print("\n开始下载（这可能需要一些时间）...")

try:
    model_dir = snapshot_download(
        model_id,
        cache_dir=cache_dir,
        revision='master'
    )
    print(f"\n✓ 模型下载完成！")
    print(f"模型路径: {model_dir}")
    print("\n注意：BERTScore需要使用HuggingFace格式的模型")
    print("如果ModelScope的模型格式不同，可能需要转换")
    
except Exception as e:
    print(f"\n✗ 下载失败: {e}")
    import traceback
    traceback.print_exc()
    print("\n提示：也可以尝试直接使用HuggingFace镜像")
    sys.exit(1)


