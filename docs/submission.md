# 提交前最后几步

## 已准备

- Python 游戏源代码及 3 个原创可解关卡。
- 运行依赖、README、运行截图、GIF。
- 23 项真实自动化测试及 T01—T06 结果。
- 分阶段开发记录及有意义的 Git 提交。
- 博客 Markdown 稿、PSP 预算、关键代码讲解。
- 本地 Windows 可执行文件（见项目 dist 文件夹）。
- GitHub 源码、文档、截图和 GIF 已发布至用户指定仓库。

## 需要完成的个人部分

1. 双击 `start.cmd`，亲自通关三关。可在首页直接选择第二、三关；遇到困难用 H 提示。完成后填写 `docs/testing.md` 的本人试玩表。
2. 填写 `docs/blog.md` 的 PSP 实际耗时，差异 = 实际 - 预估。实际耗时应来自本人的阅读、操作、试玩和整理记录，不能把 AI 自动执行时间当成本人劳动时间。
3. 核对心得，保留符合自己真实理解的内容。练习解释路径扫描、坐标方向和可解关卡构造，见 `docs/code-guide.md`。
4. 查看已上传仓库 `https://github.com/myp208116/arrow-game`，确认个人信息及内容符合预期。
5. 将 `docs/blog-cnblogs.md` 粘贴到博客园 Markdown 编辑器；它已使用仓库在线图片链接。也可自行上传 `docs/images/` 中的图片并替换链接。
6. 把博客链接提交到原作业页。截止时间：2026-09-22 23:59:59。

## GitHub 上传

目标仓库由用户指定。此处不保存任何密码或令牌。

本次已通过 GitHub 接口完成上传，本地 main 已与线上历史同步。今后在正确账号且网络可用的终端中，可以从本项目根目录运行：

```powershell
git push -u origin main
```

如果远端已出现其他提交，应先检查远端内容并合并，不能直接强制覆盖。

初次交付时连接账号不匹配；用户重新连接 myp208116 后，已确认写权限并完成分阶段上传。四个原始开发快照均通过 Git tree SHA 校验。详见 `docs/publication.md`；原始本地提交另保存在 `development-original` 分支与交付包的 Git bundle 中。

## 文件说明

- `docs/blog.md`：博客稿。
- `docs/images/demo.gif`：实际程序渲染演示。
- `docs/solutions.json`：三关完整解法，行列编号从 1 开始。
- `docs/test-report.json`：机器验证结果。
- `docs/development.md`：随开发更新的 AI 协作过程。

无需提交 `.venv/`、`build/`、`__pycache__/` 或账号凭据。独立 exe 可以作为发行附件，不必放进源代码历史。
