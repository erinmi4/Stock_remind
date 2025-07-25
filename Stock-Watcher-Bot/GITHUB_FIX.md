# 🚨 GitHub Actions 部署修复指南

## 问题诊断

GitHub Actions 显示的工作流文件版本与本地不同，说明需要重新上传。

## 🔧 立即修复步骤

### 方案 1：直接在 GitHub 编辑（推荐）

1. **访问您的 GitHub 仓库**
2. **进入 `.github/workflows/daily_check.yml` 文件**
3. **点击编辑按钮（铅笔图标）**
4. **完全替换文件内容**为以下内容：

```yaml
name: Daily Stock Check & Notify

on:
  workflow_dispatch: # 允许手动触发
  schedule:
    # 使用Cron表达式定义定时任务
    # 此处设置为每天UTC时间01:00运行 (北京/台北时间上午9:00)
    - cron: "0 1 * * *"

jobs:
  run-stock-watcher:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository code
        uses: actions/checkout@v3

      - name: Set up Python 3.9
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Install dependencies
        run: pip install -r Stock-Watcher-Bot/requirements.txt

      - name: Execute Python script
        run: python Stock-Watcher-Bot/main.py
        env:
          # 将GitHub Secrets中的机密信息注入到环境变量中
          WECHAT_APP_ID: ${{ secrets.WECHAT_APP_ID }}
          WECHAT_APP_SECRET: ${{ secrets.WECHAT_APP_SECRET }}
          WECHAT_TEMPLATE_ID: ${{ secrets.WECHAT_TEMPLATE_ID }}
          # 支持多个用户OpenID（最多20个）
          WECHAT_USER_OPENID1: ${{ secrets.WECHAT_USER_OPENID1 }}
          WECHAT_USER_OPENID2: ${{ secrets.WECHAT_USER_OPENID2 }}
          WECHAT_USER_OPENID3: ${{ secrets.WECHAT_USER_OPENID3 }}
          WECHAT_USER_OPENID4: ${{ secrets.WECHAT_USER_OPENID4 }}
          WECHAT_USER_OPENID5: ${{ secrets.WECHAT_USER_OPENID5 }}
          WECHAT_USER_OPENID6: ${{ secrets.WECHAT_USER_OPENID6 }}
          WECHAT_USER_OPENID7: ${{ secrets.WECHAT_USER_OPENID7 }}
          WECHAT_USER_OPENID8: ${{ secrets.WECHAT_USER_OPENID8 }}
          WECHAT_USER_OPENID9: ${{ secrets.WECHAT_USER_OPENID9 }}
          WECHAT_USER_OPENID10: ${{ secrets.WECHAT_USER_OPENID10 }}
          WECHAT_USER_OPENID11: ${{ secrets.WECHAT_USER_OPENID11 }}
          WECHAT_USER_OPENID12: ${{ secrets.WECHAT_USER_OPENID12 }}
          WECHAT_USER_OPENID13: ${{ secrets.WECHAT_USER_OPENID13 }}
          WECHAT_USER_OPENID14: ${{ secrets.WECHAT_USER_OPENID14 }}
          WECHAT_USER_OPENID15: ${{ secrets.WECHAT_USER_OPENID15 }}
          WECHAT_USER_OPENID16: ${{ secrets.WECHAT_USER_OPENID16 }}
          WECHAT_USER_OPENID17: ${{ secrets.WECHAT_USER_OPENID17 }}
          WECHAT_USER_OPENID18: ${{ secrets.WECHAT_USER_OPENID18 }}
          WECHAT_USER_OPENID19: ${{ secrets.WECHAT_USER_OPENID19 }}
          WECHAT_USER_OPENID20: ${{ secrets.WECHAT_USER_OPENID20 }}
```

5. **提交更改**

### 方案 2：Git 命令上传

如果您熟悉 Git 命令：

```bash
git add .github/workflows/daily_check.yml
git commit -m "Fix workflow file paths"
git push
```

## 🔍 关键修改点

修改后的工作流文件有以下重要变更：

1. ✅ **依赖安装路径**：`pip install -r Stock-Watcher-Bot/requirements.txt`
2. ✅ **脚本执行路径**：`python Stock-Watcher-Bot/main.py`
3. ✅ **保留所有环境变量配置**

## 📋 确认清单

修改完成后，请确认：

- [ ] GitHub 工作流文件已更新
- [ ] GitHub Secrets 已配置（至少 4 个必需的）
- [ ] Stock-Watcher-Bot 文件夹包含所有必需文件
- [ ] 手动触发 Actions 测试

## 🎯 下次测试

修改完成后：

1. 在 GitHub Actions 页面手动运行工作流
2. 查看运行日志确认路径正确
3. 检查是否成功发送微信消息
