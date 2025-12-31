# GitHub上传指南

## 将代码上传到GitHub的RAG仓库

### 方法一：如果RAG仓库是空的（推荐）

```bash
# 1. 进入项目目录
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# 2. 初始化git仓库
git init

# 3. 添加所有文件（.gitignore会排除不需要的文件）
git add .

# 4. 创建初始提交
git commit -m "Initial commit: CFT-RAG implementation"

# 5. 添加远程仓库（替换为你的实际仓库URL）
# 如果仓库URL是 https://github.com/John-777-tech/RAG.git
git remote add origin https://github.com/John-777-tech/RAG.git

# 6. 推送到GitHub（如果是新仓库，使用main分支）
git branch -M main
git push -u origin main
```

### 方法二：如果RAG仓库已有内容（需要先拉取）

```bash
# 1. 进入项目目录
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# 2. 初始化git仓库
git init

# 3. 添加远程仓库
git remote add origin https://github.com/John-777-tech/RAG.git

# 4. 先拉取远程内容（如果有）
git pull origin main --allow-unrelated-histories

# 5. 添加所有文件
git add .

# 6. 提交
git commit -m "Add CFT-RAG code to RAG repository"

# 7. 推送到GitHub
git push -u origin main
```

### 方法三：直接克隆并复制文件（最简单）

```bash
# 1. 先克隆RAG仓库到临时位置
cd /Users/zongyikun/Downloads
git clone https://github.com/John-777-tech/RAG.git RAG-temp

# 2. 复制所有文件到克隆的仓库
cp -r CFT-RAG-2025-main/* RAG-temp/
cp -r CFT-RAG-2025-main/.* RAG-temp/ 2>/dev/null || true

# 3. 进入仓库目录
cd RAG-temp

# 4. 添加所有文件
git add .

# 5. 提交
git commit -m "Add CFT-RAG implementation"

# 6. 推送
git push origin main

# 7. 清理临时目录（可选）
cd ..
# rm -rf RAG-temp
```

## 重要提示

### 1. 确认仓库URL
在运行命令前，请确认你的RAG仓库URL。常见格式：
- HTTPS: `https://github.com/John-777-tech/RAG.git`
- SSH: `git@github.com:John-777-tech/RAG.git`

### 2. 认证方式
- **HTTPS**: 需要输入GitHub用户名和Personal Access Token（不是密码）
- **SSH**: 需要配置SSH密钥

### 3. 需要排除的文件
检查`.gitignore`文件，确保以下内容不会被上传：
- `.env` (包含API密钥)
- `__pycache__/`
- `*.pyc`
- `.DS_Store`
- `node_modules/`
- 大文件或缓存文件

### 4. 如果遇到冲突
```bash
# 如果推送时遇到冲突，先拉取
git pull origin main --rebase

# 解决冲突后
git add .
git commit -m "Resolve conflicts"
git push origin main
```

## 快速命令（一键执行）

如果你想直接执行，可以使用以下命令（请先确认仓库URL）：

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main && \
git init && \
git add . && \
git commit -m "Initial commit: CFT-RAG implementation" && \
git remote add origin https://github.com/John-777-tech/RAG.git && \
git branch -M main && \
git push -u origin main
```

## 检查上传状态

```bash
# 查看远程仓库
git remote -v

# 查看提交历史
git log --oneline

# 查看当前状态
git status
```




