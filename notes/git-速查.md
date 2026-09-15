# Git 团队协作速查

## 第一次：把仓库传到 GitHub

在仓库目录里依次执行（把地址换成你们自己的）：

```bash
git remote add origin https://github.com/你的账号/team-mcm-2027.git
git branch -M main
git push -u origin main
```

第一次推送会弹 GitHub 登录窗口（凭据管理器），登录一次以后就不用再输。

## 队友加入

```bash
git clone https://github.com/你的账号/team-mcm-2027.git
```

## 每天的标准动作

```bash
# 开始工作前
git pull

# 看一眼改了哪些文件
git status

# 做完一块，提交一次
git add .
git commit -m "完成：问题一的动力学模型"

# 收工前
git push
```

## 分支（三种人同时改代码时用）

```bash
git checkout -b dev-ethan      # 建自己的分支
git push -u origin dev-ethan   # 推上去
# 做完后在 GitHub 网页上发起 Pull Request，合并进 main
```

## 出事了怎么办

| 情况 | 处理 |
|---|---|
| 改错了想退回上一次提交 | `git checkout -- 文件名` |
| 提交信息写错了 | `git commit --amend -m "新信息"` |
| 想看看历史 | `git log --oneline -10` |
| 两个人的改动撞了 | 打开冲突文件，保留正确内容，删掉 `<<<<<<<` 那些标记，再 `git add . && git commit` |
| 彻底搞乱了 | 别硬来，先 `git status`，把输出发我 |

## 三条铁律

1. **改代码前先 pull**，能省掉八成的冲突
2. **一个小功能一次提交**，不要攒三天堆成一次
3. **永远不要**在没提交的情况下 `git reset --hard`
