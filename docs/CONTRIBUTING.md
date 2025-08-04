# 🎉 Contributing to CMDB 🥳

首先，非常感谢您考虑为我们的项目做出贡献！我们欢迎任何形式的贡献，无论是提出新功能、改进代码、修复 bug 还是改善文档。

本指南将为您提供所有相关信息，帮助您快速入门并开始参与本项目。请花几分钟阅读它，它将帮助我们更好地协作，共同创造一个更好的项目。

## ❖ 提交问题 (Issue)

在提交 PR 之前，请先搜索 现有的 [PR](https://github.com/veops/cmdb/pulls) 或 [Issue](https://github.com/veops/cmdb/issues)，查看是否已经有相关的开放或关闭的提交。

如果是修复 bug，请首先提交一个 Issue。

对于新增功能，请先通过我们提供的联系方式与我们直接联系，以便更好的合作。

## ❖ 提交 PR 的步骤

1. 在 Github 上 fork 该项目的仓库。
2. 在本地复制仓库后创建一个新分支，用于开发新功能、修复 bug 或进行其他贡献，命令：`git checkout -b feat/xxxx`。
3. 提交您的更改：`git commit -am 'feat: add xxxxx'`。
4. 推送您的分支：`git push origin feat/xxxx`。
5. 提交 Pull Request 时，请确保您的源分支是刚刚推送的分支，目标分支是 CMDB 项目的 master 分支。
6. 提交后，请留意与 Pull Request 相关的邮件和通知。待通过审核后，我们会按计划将其合并到 master 分支，并进行新一轮的版本发布。

## ❖ 开发环境
- Python 版本 >= 3.8
- Node.js 版本 >= 14.17.6
- Docker

## ❖ 代码风格

**API**: 请遵循 [Python Style](https://google.github.io/styleguide/pyguide.html) 

**UI**: 请遵循 [node-style-guide](https://github.com/felixge/node-style-guide)

## ❖ 提交信息

+ 请遵循 [Angular](https://github.com/conventional-changelog/conventional-changelog/tree/master/packages/conventional-changelog-angular)

+ 提交时使用不同的范围
  - API: `feat(api): xxx`
  - UI: `feat(ui): xxx`

+ 为了确保所有开发者都能更好地理解，提交信息请使用英文。

  - `feat` 添加新功能
  - `fix` 修复问题/BUG
  - `style` 代码风格相关，不影响运行结果
  - `perf` 优化/性能提升
  - `refactor` 代码重构
  - `revert` 撤销编辑
  - `test` 测试相关
  - `docs` 文档/注释
  - `chore` 依赖更新/脚手架配置修改等
  - `workflow` 工作流优化
  - `ci` 持续集成
  - `types` 类型定义文件变更
  - `wip` 开发中

## ❖ 代码内容

为了便于所有开发者理解，请确保代码注释和代码内容使用英文。