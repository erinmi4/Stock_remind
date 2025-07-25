# 📈 Stock Watcher Bot - 自动化股票监控与提醒系统

一个基于 GitHub Actions 的全自动股票监控系统，能够定时监控股票价格并通过微信推送投资决策提醒。

## 🚀 核心功能

- ⏰ **定时自动执行**: 每日北京时间上午 9:00 自动运行
- 📊 **多市场支持**: 支持 A 股、美股等多个市场
- 💰 **智能决策**: 根据设定的买卖价位自动生成投资建议
- 📱 **微信推送**: 通过微信测试公众号推送格式化报告
- 🔧 **零维护**: 完全基于 GitHub Actions，无需服务器

## 📁 项目结构

```
Stock-Watcher-Bot/
├── .github/
│   └── workflows/
│       └── daily_check.yml   # GitHub Actions 配置文件
├── config.json               # 股票策略配置文件
├── main.py                   # 核心执行脚本
└── README.md                 # 项目说明文档
```

## 🛠️ 部署步骤

### 1. 创建 GitHub 仓库

1. 在 GitHub 上创建一个新的公开仓库
2. 将本项目的所有文件上传到仓库

### 2. 申请微信测试公众号

1. 访问 [微信测试号平台](https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login)
2. 使用微信扫码登录
3. 记录以下信息：
   - `appID`
   - `appsecret`
   - `微信号` (扫码关注测试号后获得 openID)

### 3. 创建消息模板

在微信测试号平台的"模板消息接口"中添加模板：

```
标题: {{title.DATA}}
内容: {{content.DATA}}
时间: {{report_time.DATA}}
提示: {{tip.DATA}}
```

记录生成的模板 ID。

### 4. 配置 GitHub Secrets

在你的 GitHub 仓库中，进入 `Settings` > `Secrets and variables` > `Actions`，添加以下 Secrets：

- `WECHAT_APP_ID`: 微信测试号的 appID
- `WECHAT_APP_SECRET`: 微信测试号的 appsecret
- `WECHAT_TEMPLATE_ID`: 消息模板 ID
- `WECHAT_USER_OPENID1`: 第1个用户的微信 openID
- `WECHAT_USER_OPENID2`: 第2个用户的微信 openID (可选)
- `...`: 最多支持20个用户 (WECHAT_USER_OPENID1 到 WECHAT_USER_OPENID20)

> 💡 **多用户支持**: 系统支持同时向最多20个用户发送消息，只需配置对应的 WECHAT_USER_OPENID1、WECHAT_USER_OPENID2 等即可。  
> 💡 **快速配置**: 参考项目中的 `WECHAT_CONFIG.md` 文件获取详细配置步骤，或运行 `python test_config.py` 测试配置是否正确。

### 5. 自定义监控股票

编辑 `config.json` 文件，添加你要监控的股票：

```json
[
  {
    "name": "股票名称",
    "code": "股票代码",
    "sell_price": 卖出价位,
    "buy_price": 买入价位,
    "note": "备注信息"
  }
]
```

**股票代码格式说明：**

- A 股上海: `sh` + 代码，如 `sh000001`
- A 股深圳: `sz` + 代码，如 `sz000001`
- 美股: `gb_` + 代码，如 `gb_aapl`

## 🎯 使用说明

### 自动运行

系统会在每天北京时间上午 9:00 自动执行，无需人工干预。

### 手动触发

在 GitHub 仓库的 `Actions` 页面，选择 `Daily Stock Check & Notify` 工作流，点击 `Run workflow` 可手动触发。

### 决策逻辑

- 🟢 **纪律卖出**: 当前价格 > 设定卖出价
- 🔴 **价值买入**: 当前价格 < 设定买入价
- 🟡 **持仓观察**: 价格在买卖区间内

## 📱 消息示例

正常情况下的消息：

```
📊 投资仪表盘日报 2025-07-25

上证50ETF: 🟡 持仓观察 (现价:6.25)
苹果: 🟢 纪律卖出 (现价:225.0 > 目标:220.0)
创业板ETF: 🟡 持仓观察 (现价:1.9)

时间: 2025-07-25 09:00:15
提示: 投资有风险，决策需谨慎。本提醒仅供参考。
```

触发提醒时的消息：

```
🚨注意！2项投资提醒！

上证50ETF: 🔴 价值买入 (现价:5.95 < 目标:6.00)
苹果: 🟢 纪律卖出 (现价:225.0 > 目标:220.0)
创业板ETF: 🟡 持仓观察 (现价:1.9)
```

## ⚙️ 自定义设置

### 修改运行时间

编辑 `.github/workflows/daily_check.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: "0 1 * * *" # UTC时间01:00 = 北京时间09:00
```

### 添加更多股票

直接编辑 `config.json` 文件，按格式添加新的股票配置。

## 🔍 故障排除

### 1. 消息发送失败

- 检查微信测试号是否已关注
- 确认 GitHub Secrets 配置正确
- 查看 Actions 日志中的错误信息

### 2. 股票价格获取失败

- 确认股票代码格式正确
- 检查网络连接状况
- 新浪财经 API 可能有访问限制

### 3. GitHub Actions 不执行

- 确认仓库是公开的（私有仓库有使用限制）
- 检查 cron 表达式格式
- GitHub Actions 可能有延迟

## 📋 技术说明

- **运行环境**: GitHub Actions (Ubuntu)
- **编程语言**: Python 3.9+
- **依赖库**: requests
- **数据源**: 新浪财经 API
- **消息推送**: 微信测试公众号

## ⚠️ 免责声明

本系统仅供学习和参考使用，所有投资决策建议仅基于预设的价格规则，不构成专业的投资建议。投资有风险，决策需谨慎。

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

🎉 **祝你投资顺利！** 如有问题，欢迎提交 Issue。
