# 🔐 微信配置指南

## 您的微信测试公众号信息

根据您提供的信息，以下是需要在 GitHub Secrets 中配置的值：

### 1. GitHub Secrets 配置

请在您的 GitHub 仓库中按照以下步骤配置：

1. 进入您的 GitHub 仓库
2. 点击 `Settings` 选项卡
3. 在左侧菜单中选择 `Secrets and variables` > `Actions`
4. 点击 `New repository secret` 按钮
5. 依次添加以下 4 个 Secrets：

| Secret Name            | Secret Value                             |
| ---------------------- | ---------------------------------------- |
| `WECHAT_APP_ID`        | `您的微信测试号AppID`                    |
| `WECHAT_APP_SECRET`    | `您的微信测试号AppSecret`                |
| `WECHAT_TEMPLATE_ID`   | `您的消息模板ID`                         |
| `WECHAT_USER_OPENID1`  | `第1个用户的OpenID`                      |
| `WECHAT_USER_OPENID2`  | `第2个用户的OpenID（可选）`              |
| `...`                  | `最多支持20个OpenID`                     |

### 2. 获取您的 OpenID

您还需要获取您的微信 OpenID：

1. 访问 [微信测试号平台](https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login)
2. 使用您的微信扫码登录
3. 在页面下方找到"测试号二维码"
4. 用微信扫描这个二维码关注测试号
5. 关注后，页面会显示您的 OpenID
6. 将这个 OpenID 添加到 GitHub Secrets 中的 `WECHAT_USER_OPENID1`
7. 如需添加更多用户，可继续添加 `WECHAT_USER_OPENID2`、`WECHAT_USER_OPENID3` 等（最多20个）

### 3. 微信模板消息配置

确保您在微信测试号平台的"模板消息接口"中已创建模板，格式如下：

```
标题: {{title.DATA}}
内容: {{content.DATA}}
时间: {{report_time.DATA}}
提示: {{tip.DATA}}
```

### 4. 测试步骤

配置完成后，您可以：

1. 在 GitHub 仓库的 `Actions` 页面
2. 选择 `Daily Stock Check & Notify` 工作流
3. 点击 `Run workflow` 手动触发一次测试
4. 查看运行日志确认是否成功
5. 检查微信是否收到测试消息

### 5. 注意事项

- ⚠️ 请勿将这些敏感信息直接写在代码中
- ⚠️ 模板 ID 必须与您在微信平台创建的模板完全匹配
- ⚠️ OpenID 是唯一的，每个微信用户对应不同的测试号都有不同的 OpenID
- ⚠️ 测试号有一定的消息发送限制，请合理使用
- 💡 多用户功能：系统会自动向所有配置的OpenID发送消息，适合团队使用
- 💡 至少配置一个OpenID：系统至少需要 `WECHAT_USER_OPENID1`，其他OpenID为可选
- 💡 发送间隔：系统会在向多个用户发送消息间添加0.5秒延迟，避免触发频率限制

### 6. 多用户配置示例

#### 单用户配置
```
WECHAT_USER_OPENID1 = "your-openid-here"
```

#### 多用户配置（团队使用）
```
WECHAT_USER_OPENID1 = "team-leader-openid"
WECHAT_USER_OPENID2 = "member1-openid" 
WECHAT_USER_OPENID3 = "member2-openid"
```

配置完成后，系统将在每天北京时间上午 9:00 自动运行，并发送股票监控报告到所有配置用户的微信！
