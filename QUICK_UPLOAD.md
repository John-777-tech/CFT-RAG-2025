# 快速上传到GitHub

## 当前状态
✅ Git仓库已初始化
✅ 所有文件已添加
✅ 已创建初始提交（351个文件）

## 下一步：推送到GitHub

### 方法1：使用HTTPS（推荐，需要Personal Access Token）

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# 添加远程仓库（请替换为你的实际URL）
git remote add origin https://github.com/John-777-tech/RAG.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

**注意**：推送时会要求输入：
- Username: `John-777-tech`
- Password: 输入你的 **Personal Access Token**（不是GitHub密码）

### 方法2：使用SSH（如果已配置SSH密钥）

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main

# 添加远程仓库（SSH格式）
git remote add origin git@github.com:John-777-tech/RAG.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

## 如何获取Personal Access Token

1. 登录GitHub
2. 点击右上角头像 → Settings
3. 左侧菜单 → Developer settings
4. Personal access tokens → Tokens (classic)
5. Generate new token (classic)
6. 选择权限：至少勾选 `repo`
7. 生成后复制token（只显示一次）

## 如果仓库已存在内容

如果RAG仓库已经有内容，需要先拉取：

```bash
git pull origin main --allow-unrelated-histories
# 解决可能的冲突后
git push -u origin main
```

## 检查状态

```bash
# 查看远程仓库
git remote -v

# 查看提交历史
git log --oneline -5
```




