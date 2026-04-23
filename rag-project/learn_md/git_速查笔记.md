# Git 速查笔记

## 1. Git 是干什么的

**Git 是一个版本管理工具。**

它主要用来：

- 记录代码历史
- 管理不同版本
- 回退错误修改
- 和别人协作开发
- 把本地代码同步到 GitHub

你可以把它理解成：
**给代码“拍快照”和“记历史”的工具。**

---

## 2. Git 里几个最重要的概念

### 工作区
就是你当前正在修改代码的文件夹。

### 暂存区
你准备提交的改动先放在这里。

### 本地仓库
保存在你电脑里的 Git 历史记录。

### 远程仓库
保存在 GitHub / Gitee 上的仓库。

---

## 3. 最核心的日常流程

你以后最常用的就是这 4 步：

```bash
git status
git add .
git commit -m "本次修改说明"
git push
```

### 这四步的意思

- `git status`：看当前仓库状态
- `git add .`：把所有改动加入暂存区
- `git commit -m "..."`：正式提交到本地仓库
- `git push`：把本地提交上传到远程仓库

---

## 4. 你一定要会的基础命令

### 初始化仓库

```bash
git init
```

作用：把当前文件夹变成 Git 仓库。

### 查看状态

```bash
git status
```

作用：查看当前有没有新文件、修改、是否已经 add、是否已经 commit。

### 加入暂存区

```bash
git add hello.txt
```

或者：

```bash
git add .
```

作用：把改动放进暂存区，准备提交。

### 提交

```bash
git commit -m "first commit"
```

作用：把暂存区内容正式保存到本地 Git 历史中。

### 查看提交历史

```bash
git log --oneline
```

作用：查看提交记录，简洁显示。

### 查看改动内容

```bash
git diff
```

作用：查看还没 add 的改动。

```bash
git diff --cached
```

作用：查看已经 add、准备 commit 的改动。

---

## 5. `add` 和 `commit` 的区别

这是最常见的基础问题。

### `git add`
把改动加入暂存区。

### `git commit`
把暂存区内容正式提交到本地仓库。

一句话记忆：
**add 是“选中改动”，commit 是“正式保存”。**

---

## 6. `-m` 是什么

比如：

```bash
git commit -m "update hello.txt"
```

这里的 `-m` 表示：
**给这次提交写一条说明。**

不写 `-m` 也可以，但 Git 会打开编辑器让你手动输入说明。
平时最方便的方式就是直接写：

```bash
git commit -m "提交说明"
```

---

## 7. 分支是什么

**分支就是代码的一条开发线。**

主分支一般是：

- `main`
- 或者 `master`

你可以在新分支上开发新功能，不影响主分支。

---

## 8. 分支常用命令

### 查看分支

```bash
git branch
```

前面有 `*` 的，就是当前分支。

### 创建分支

```bash
git branch feature
```

作用：创建一个叫 `feature` 的新分支。

### 切换分支

```bash
git switch feature
```

作用：切换到 `feature` 分支。

### 切回主分支

```bash
git switch master
```

或者：

```bash
git switch main
```

### 合并分支

```bash
git merge feature
```

注意：这条命令的意思是：
**把 `feature` 分支合并到当前分支。**

所以一般要先切回主分支，再执行合并。

### 删除分支

```bash
git branch -d feature
```

作用：删除已经合并完成的分支。

---

## 9. `stash` 速查

### `stash` 是什么意思

`stash` 的意思是：
**把当前还没有 commit 的改动，先临时收起来。**

最常见的场景是：

- 你代码改到一半，还没准备提交
- 但你又想先切到别的分支去修 bug
- 这时候就可以先 `git stash`

### 常用命令

```bash
git stash
```

作用：把当前改动临时存起来。

```bash
git stash list
```

作用：查看现在一共有多少条 stash 记录。

```bash
git stash pop
```

作用：恢复最近一次 stash，并把这条 stash 记录删掉。

```bash
git stash apply
```

作用：恢复 stash，但不删除 stash 记录。

### 一个简单例子

你正在开发 `feature/login`，但突然要去修一个按钮 bug：

```bash
git stash
git switch main
git switch -c fix/button-text
```

修完之后再切回来：

```bash
git switch feature/login
git stash pop
```

一句话记忆：
**stash = 临时保存还没提交的改动**

---

## 10. `worktree` 速查

### `worktree` 是什么

`branch` 和 `worktree` 不是一回事：

- `branch` 是一条开发分支
- `worktree` 是一个实际工作的文件夹

你可以简单理解成：

- `branch` 决定“你在做哪条开发线”
- `worktree` 决定“你在哪个目录里做这条开发线”

### 为什么要有 `worktree`

平时如果你只有一个仓库目录，那么你在同一个目录里一次通常只方便工作在一个分支上。

如果你一会儿做 `feature/login`，一会儿又要修 `fix/button-text`，通常就要：

- 切换分支
- stash
- 再切回来

这样会比较乱。

`worktree` 的作用就是：
**让同一个仓库同时拥有多个工作目录，每个目录可以对应不同分支。**

### 一个具体例子

假设你当前仓库目录是：

```text
D:\repo\my-project
```

你现在想同时做两件事：

- 开发登录功能 `feature/login`
- 修复按钮问题 `fix/button-text`

你可以执行：

```bash
git worktree add ../my-project-login -b feature/login main
git worktree add ../my-project-fix -b fix/button-text main
```

执行完之后，你磁盘上可能会出现：

```text
my-project/         -> main
my-project-login/   -> feature/login
my-project-fix/     -> fix/button-text
```

这时你就可以：

- 在 `my-project-login/` 里继续开发登录功能
- 在 `my-project-fix/` 里修按钮 bug
- 不用在同一个目录里来回切分支

### 最重要的一句话

**worktree 只是把不同 branch 放到不同文件夹里工作，最后合并时，本质上还是 branch 在 merge。**

也就是说，最后合并仍然和普通 Git 一样：

```bash
git switch main
git merge feature/login
git merge fix/button-text
```

---

## 11. `worktree` 常用命令

### 查看当前有哪些 worktree

```bash
git worktree list
```

作用：查看这个仓库现在挂了哪些工作目录，以及每个目录对应什么分支。

### 新建一个 worktree（分支已存在）

```bash
git worktree add ../repo-login feature/login
```

作用：在 `../repo-login` 创建一个新目录，并检出 `feature/login`。

### 新建一个 worktree（顺便创建新分支）

```bash
git worktree add ../repo-login -b feature/login main
```

作用：基于 `main` 创建 `feature/login`，并在新目录中打开这个分支。

### 删除一个 worktree

```bash
git worktree remove ../repo-login
```

作用：删除这个 worktree 对应的工作目录。

注意：
**这只是删文件夹，不是删分支。**

如果分支也不要了，再执行：

```bash
git branch -d feature/login
```

### 清理失效的 worktree 记录

```bash
git worktree prune
```

作用：清理已经失效的 worktree 记录。

### 锁定 / 解锁 worktree

```bash
git worktree lock ../repo-login
git worktree unlock ../repo-login
```

作用：防止某个 worktree 被误删。

---

## 12. `worktree` 一套完整流程

### 1. 从 main 拉一个新任务出来

```bash
git worktree add ../repo-feature -b feature/login main
```

### 2. 去新目录开发

```bash
cd ../repo-feature
git status
git add .
git commit -m "add login feature"
```

### 3. 开发完回主目录合并

```bash
cd ../repo
git switch main
git merge feature/login
```

### 4. 合并完删除 worktree

```bash
git worktree remove ../repo-feature
```

### 5. 如果分支也不用了，再删 branch

```bash
git branch -d feature/login
```

一句话记忆：
**worktree 用来分开工作，merge 还是按 branch 来合并。**

---

## 13. 远程仓库常用命令

### 查看远程仓库

```bash
git remote -v
```

### 添加远程仓库

```bash
git remote add origin 仓库地址
```

### 修改远程仓库地址

```bash
git remote set-url origin 仓库地址
```

### 第一次推送

```bash
git push -u origin master
```

如果主分支叫 `main`，就改成：

```bash
git push -u origin main
```

### 以后正常推送

```bash
git push
```

### 拉取远程最新代码

```bash
git pull
```

### 克隆仓库

```bash
git clone 仓库地址
```

---

## 14. GitHub SSH 相关

### 生成 SSH key

```bash
ssh-keygen -t ed25519 -C "你的GitHub邮箱"
```

### 测试 SSH 连接

```bash
ssh -T git@github.com
```

如果网络特殊，也可以走 SSH over 443。

### SSH over 443 配置

编辑 `~/.ssh/config`，加入：

```text
Host github.com
    Hostname ssh.github.com
    Port 443
    User git
```

---

## 15. 你以后最常用的一整套流程

### 本地开发并上传

```bash
git status
git add .
git commit -m "本次修改说明"
git push
```

### 远程有更新时

```bash
git pull
git status
git add .
git commit -m "本次修改说明"
git push
```

---

## 16. 面试时可以怎么回答

### 你会用 Git 吗？

可以答：

> 会，主要用于版本管理和项目协作。我会使用 `clone`、`status`、`add`、`commit`、`push`、`pull`、`branch`、`switch`、`merge` 这些基本命令，也能把本地项目上传到 GitHub。

### `git add` 和 `git commit` 有什么区别？

- `git add`：把改动加入暂存区
- `git commit`：把暂存区内容正式保存到本地仓库

### `git push` 是干什么的？

- 把本地提交上传到远程仓库

### 分支有什么用？

- 用来在不影响主分支的情况下开发新功能

### `stash` 是什么？

- 把当前还没有 commit 的改动先临时收起来

### `worktree` 是什么？

- `branch` 是开发线，`worktree` 是工作目录
- 它的作用是让同一个仓库同时在不同文件夹里做不同的分支任务
- 最后合并时，本质上还是用 `git merge` 去合并分支

---

## 17. 最后一句话记忆

**Git = 管理代码历史，add = 选中改动，commit = 正式保存，push = 上传远程。**
