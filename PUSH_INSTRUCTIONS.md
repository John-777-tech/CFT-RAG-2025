# GitHub推送说明

## 当前状态
✅ 代码已准备就绪，可以推送

## 推送方法

### ⚠️ 重要：需要在终端手动执行（因为需要交互式认证）

由于推送需要输入GitHub用户名和Personal Access Token，请在**你自己的终端**中执行以下命令：

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
git push -u origin main
```

### 执行时会提示输入：

1. **Username**: 输入 `John-777-tech`
2. **Password**: 输入你的 **Personal Access Token**（不是GitHub密码！）

### 如果还没有Personal Access Token：

1. 访问：https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 给token起个名字（如：RAG-upload）
4. 勾选权限：至少选择 `repo` (完整仓库权限)
5. 点击 "Generate token"
6. **复制token**（只显示一次，请保存好）
7. 在推送时，当提示Password时，粘贴这个token

### 如果RAG仓库已有内容

如果推送时遇到 "Updates were rejected" 错误，需要先拉取：

```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
git pull origin main --allow-unrelated-histories
# 如果有冲突，解决冲突后
git push -u origin main
```

### 配置Git用户信息（可选）

如果想设置默认的用户信息：

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 使用SSH（推荐，避免每次输入token）

如果想使用SSH密钥（更安全，不需要每次输入token）：

1. **生成SSH密钥**（如果还没有）：
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
# 按Enter使用默认位置
# 可以设置密码（可选）
```

2. **添加SSH密钥到GitHub**：
```bash
# 复制公钥
cat ~/.ssh/id_ed25519.pub
# 复制输出的内容
```

然后：
- 访问 https://github.com/settings/keys
- 点击 "New SSH key"
- 粘贴公钥内容
- 保存

3. **切换到SSH URL**：
```bash
cd /Users/zongyikun/Downloads/CFT-RAG-2025-main
git remote set-url origin git@github.com:John-777-tech/RAG.git
git push -u origin main
```

---

## 快速检查命令

```bash
# 查看远程仓库配置
git remote -v

# 查看提交历史
git log --oneline -5

# 查看当前状态
git status
```




