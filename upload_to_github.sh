#!/bin/bash

# GitHub上传脚本
# 使用方法: bash upload_to_github.sh

echo "=== 开始上传代码到GitHub ==="

# 进入项目目录
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# 检查是否已经是git仓库
if [ -d ".git" ]; then
    echo "检测到已有git仓库，跳过初始化"
else
    echo "1. 初始化git仓库..."
    git init
fi

# 添加所有文件
echo "2. 添加文件到暂存区..."
git add .

# 检查是否有更改
if git diff --staged --quiet; then
    echo "没有需要提交的更改"
    exit 0
fi

# 提交
echo "3. 提交更改..."
git commit -m "Add CFT-RAG implementation and paper revisions"

# 设置远程仓库（如果还没有）
if ! git remote | grep -q origin; then
    echo "4. 添加远程仓库..."
    echo "请确认你的GitHub仓库URL（例如: https://github.com/John-777-tech/RAG.git）"
    read -p "请输入仓库URL: " repo_url
    git remote add origin "$repo_url"
else
    echo "4. 远程仓库已存在"
    repo_url=$(git remote get-url origin)
    echo "当前远程仓库: $repo_url"
fi

# 设置分支为main
echo "5. 设置分支为main..."
git branch -M main

# 推送
echo "6. 推送到GitHub..."
echo "注意：如果这是第一次推送，可能需要输入GitHub用户名和Personal Access Token"
git push -u origin main

echo "=== 上传完成 ==="
echo "如果遇到认证问题，请："
echo "1. 使用Personal Access Token而不是密码"
echo "2. 或者配置SSH密钥使用SSH URL"

