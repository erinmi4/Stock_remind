import requests
import json
import os
import sys
from datetime import datetime
import time

def get_access_token(app_id, app_secret):
    """获取微信access_token"""
    url = (
        "https://api.weixin.qq.com/cgi-bin/token"
        f"?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    )
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "access_token" in data:
            print("access_token 获取成功")
            return data["access_token"]
        else:
            print(f"获取access_token失败: {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"请求access_token时发生网络错误: {e}")
        return None

def get_stock_price(stock_code):
    """从新浪财经API获取股票/基金的实时价格
    
    支持的股票代码格式：
    - 上海证券：sh + 代码 (如 sh510500)
    - 深圳证券：sz + 代码 (如 sz159901)
    - 美股：gb_ + 代码 (如 gb_aapl)
    """
    url = f"https://hq.sinajs.cn/list={stock_code}"
    headers = {
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        print(f"正在获取 {stock_code} 的价格数据...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 解析新浪财经返回的数据
        # 格式：var hq_str_sh510500="南方中证500ETF,6.364,6.273,6.364,6.386,6.328,6.363,6.364,16167,102911130.000,..."
        content = response.text.strip()
        if not content or '=' not in content:
            print(f"数据格式异常: {content}")
            return None
            
        # 提取引号内的数据
        data_start = content.find('"') + 1
        data_end = content.rfind('"')
        if data_start <= 0 or data_end <= data_start:
            print(f"无法解析数据格式: {content}")
            return None
            
        data_str = content[data_start:data_end]
        parts = data_str.split(',')
        
        if len(parts) < 4:
            print(f"数据长度不足: {len(parts)} 项，内容: {data_str}")
            return None
            
        # 不同市场的价格字段位置
        if stock_code.startswith(("sh", "sz")):
            # A股/基金：当前价格在第3个位置（索引3）
            current_price = parts[3]
            stock_name = parts[0]
            print(f"获取到 {stock_name}({stock_code}) 当前价格: {current_price}")
            return float(current_price)
            
        elif stock_code.startswith("gb_"):
            # 美股：当前价格在第1个位置（索引1）
            current_price = parts[1]
            stock_name = parts[0]
            print(f"获取到 {stock_name}({stock_code}) 当前价格: {current_price}")
            return float(current_price)
            
        else:
            print(f"不支持的股票代码格式: {stock_code}")
            return None
            
    except (requests.exceptions.RequestException, ValueError, IndexError) as e:
        print(f"获取 {stock_code} 价格失败: {e}")
        return None
    except Exception as e:
        print(f"解析 {stock_code} 数据时出现未知错误: {e}")
        return None

def send_wechat_message(access_token, open_id, template_id, report_data):
    """向单个用户发送格式化的模板消息"""
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, data=json.dumps(report_data), headers=headers, timeout=5)
        response.raise_for_status()
        result = response.json()
        if result.get("errcode") == 0:
            print(f"消息成功发送给 {open_id}")
        else:
            print(f"消息发送失败: {result}")
    except requests.exceptions.RequestException as e:
        print(f"发送消息时发生网络错误: {e}")

def main():
    """主执行函数"""
    # 1. 从GitHub Actions的环境变量中读取微信配置
    APP_ID = os.environ.get('WECHAT_APP_ID')
    APP_SECRET = os.environ.get('WECHAT_APP_SECRET')
    TEMPLATE_ID = os.environ.get('WECHAT_TEMPLATE_ID')
    
    # 获取所有配置的OpenID（支持最多20个用户）
    user_openids = []
    for i in range(1, 21):  # 支持WECHAT_USER_OPENID1到WECHAT_USER_OPENID20
        openid = os.environ.get(f'WECHAT_USER_OPENID{i}')
        if openid:
            user_openids.append(openid)

    if not all([APP_ID, APP_SECRET, TEMPLATE_ID]) or not user_openids:
        print("错误: 微信配置信息不完整，请检查GitHub Secrets。")
        print("必需配置: WECHAT_APP_ID, WECHAT_APP_SECRET, WECHAT_TEMPLATE_ID")
        print("至少需要一个: WECHAT_USER_OPENID1, WECHAT_USER_OPENID2, ...")
        sys.exit(1)
    
    print(f"检测到 {len(user_openids)} 个用户配置")

    # 2. 读取 config.json 文件
    config_path = 'Stock-Watcher-Bot/config.json' if os.path.exists('Stock-Watcher-Bot/config.json') else 'config.json'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            stocks = json.load(f)
    except FileNotFoundError:
        print("错误: config.json 文件未找到！")
        print(f"查找路径: {config_path}")
        sys.exit(1)

    # 3. 初始化报告内容列表
    report_lines = []
    triggered_alerts = []

    # 4. 遍历所有股票，生成智能决策报告
    for stock in stocks:
        print(f"\n处理股票: {stock['name']} ({stock['code']})")
        price = get_stock_price(stock['code'])
        
        # 构建报告行
        line = f"📊 **{stock['name']}** ({stock['code']}): "
        
        if price is None:
            decision = "❌ 价格获取失败"
            line += decision
        else:
            # 智能决策逻辑
            if price >= stock['sell_price']:
                decision = f"🟢 **纪律卖出**\n   现价: ¥{price:.3f} ≥ 卖出价: ¥{stock['sell_price']}"
                triggered_alerts.append(f"{stock['name']}: 达到卖出条件")
            elif price <= stock['buy_price']:
                decision = f"🔴 **价值买入**\n   现价: ¥{price:.3f} ≤ 买入价: ¥{stock['buy_price']}"
                triggered_alerts.append(f"{stock['name']}: 达到买入条件")
            else:
                decision = f"🟡 **持仓观察**\n   现价: ¥{price:.3f} (买入: ¥{stock['buy_price']} ~ 卖出: ¥{stock['sell_price']})"
            
            line += decision
            if stock.get('note'):
                line += f"\n   💡 {stock['note']}"
        
        report_lines.append(line)
        
    print(f"\n生成报告完成，触发 {len(triggered_alerts)} 项提醒")

    # 5. 生成完整的智能分析报告
    today_str = datetime.now().strftime('%Y年%m月%d日')
    time_str = datetime.now().strftime('%H:%M:%S')
    
    # 报告标题根据触发条件动态生成
    if triggered_alerts:
        title = f"🚨 投资提醒！发现 {len(triggered_alerts)} 项操作机会"
        alert_summary = "⚠️ **触发提醒**:\n" + "\n".join([f"• {alert}" for alert in triggered_alerts])
    else:
        title = f"📈 投资仪表盘日报 - {today_str}"
        alert_summary = "✅ 当前所有持仓均在正常区间内"
    
    # 组装最终报告内容
    final_report_content = f"""{alert_summary}

📋 **详细监控报告**:
{chr(10).join(report_lines)}

🕐 报告时间: {today_str} {time_str}
📱 数据来源: 新浪财经实时行情
💡 温馨提示: 投资有风险，决策需谨慎"""

    print(f"\n📄 生成最终报告:")
    print(f"标题: {title}")
    print(f"内容长度: {len(final_report_content)} 字符")

    # 6. 获取access_token
    token = get_access_token(APP_ID, APP_SECRET)
    if not token:
        sys.exit(1)

    # 7. 构建微信模板消息数据
    wechat_data = {
        "template_id": TEMPLATE_ID,
        "url": "https://finance.sina.com.cn/fund/quotes/510500/bc.shtml",  # 点击跳转到南方中证500ETF页面
        "data": {
            "title": {
                "value": title, 
                "color": "#FF6B6B" if triggered_alerts else "#4ECDC4"
            },
            "content": {
                "value": final_report_content,
                "color": "#333333"
            },
            "report_time": {
                "value": f"{today_str} {time_str}",
                "color": "#999999"
            },
            "tip": {
                "value": "💼 智能投资监控系统为您服务",
                "color": "#6C5CE7"
            }
        }
    }

    print(f"\n📨 准备向 {len(user_openids)} 位用户发送微信提醒...")

    # 8. 向所有配置的用户发送智能投资报告
    success_count = 0
    for i, openid in enumerate(user_openids, 1):
        print(f"📤 向用户 {i}/{len(user_openids)} 发送消息...")
        wechat_data["touser"] = openid
        
        try:
            send_wechat_message(token, openid, TEMPLATE_ID, wechat_data)
            success_count += 1
        except Exception as e:
            print(f"❌ 向用户 {i} 发送消息失败: {e}")
        
        # 避免发送过快触发限频，添加延迟
        if i < len(user_openids):
            time.sleep(1)
    
    print(f"\n✅ 任务完成！成功发送 {success_count}/{len(user_openids)} 条消息")
    if triggered_alerts:
        print(f"🔔 本次共触发 {len(triggered_alerts)} 项投资提醒")
    
    return success_count > 0

if __name__ == "__main__":
    main()
