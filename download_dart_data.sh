#!/bin/bash
# 只下载DART数据集的data目录

echo "正在下载DART数据集的data目录..."

# 方法1：使用git sparse-checkout（推荐，只下载data目录）
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
mkdir -p datasets/DART
cd datasets/DART

# 初始化git仓库但不checkout
git init
git remote add origin https://github.com/Yale-LILY/dart.git
git config core.sparseCheckout true

# 只下载data目录
echo "data/*" > .git/info/sparse-checkout

# 拉取数据
git pull origin master

echo "✅ 下载完成！数据在: datasets/DART/data/"

# 方法2（备选）：如果方法1不行，可以使用svn
# echo "使用方法2: svn checkout..."
# cd /Users/zongyikun/Downloads/CFT-RAG-2025-main/datasets
# svn checkout https://github.com/Yale-LILY/dart/trunk/data DART/data


