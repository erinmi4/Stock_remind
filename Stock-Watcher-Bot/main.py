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
    """从新浪财经API获取股票/基金的实时价格"""
    url = f"https://hq.sinajs.cn/list={stock_code}"
    headers = {
        'Referer': 'https://finance.sina.com.cn'
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        # 解析返回的数据
        parts = response.text.split(',')
        # A股和基金的价格在第3个位置
        if stock_code.startswith("sh") or stock_code.startswith("sz"):
            if len(parts) > 3:
                return float(parts[3])
        # 美股的价格在第1个位置
        elif stock_code.startswith("gb_"):
            if len(parts) > 1:
                return float(parts[1])
        return None
    except (requests.exceptions.RequestException, ValueError, IndexError) as e:
        print(f"获取 {stock_code} 价格失败: {e}")
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
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            stocks = json.load(f)
    except FileNotFoundError:
        print("错误: config.json 文件未找到！")
        sys.exit(1)

    # 3. 初始化报告内容列表
    report_lines = []
    triggered_alerts = []

    # 4. 遍历所有股票，生成决策报告
    for stock in stocks:
        price = get_stock_price(stock['code'])
        line = f"**{stock['name']}**: "
        if price is None:
            decision = "价格获取失败 ❌"
        elif price > stock['sell_price']:
            decision = f"🟢 **纪律卖出** (现价:{price} > 目标:{stock['sell_price']})"
            triggered_alerts.append(decision)
        elif price < stock['buy_price']:
            decision = f"🔴 **价值买入** (现价:{price} < 目标:{stock['buy_price']})"
            triggered_alerts.append(decision)
        else:
            decision = f"🟡 持仓观察 (现价:{price})"
        report_lines.append(line + decision)

    # 5. 组合成最终的Markdown格式报告
    today_str = datetime.now().strftime('%Y-%m-%d')
    final_report_content = "\n".join(report_lines)
    
    # 确定报告标题
    title = f"投资仪表盘日报 {today_str}"
    if triggered_alerts:
        title = f"🚨注意！{len(triggered_alerts)}项投资提醒！"

    # 6. 获取access_token
    token = get_access_token(APP_ID, APP_SECRET)
    if not token:
        sys.exit(1)

    # 7. 构建发送给微信的数据结构
    wechat_data = {
        "template_id": TEMPLATE_ID,
        "url": "http://finance.sina.com.cn/", # 点击消息跳转的链接
        "data": {
            "title": {"value": title, "color": "#FF0000" if triggered_alerts else "#173177"},
            "content": {"value": final_report_content},
            "report_time": {"value": datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
            "tip": {"value": "投资有风险，决策需谨慎。本提醒仅供参考。"}
        }
    }

    # 8. 向所有配置的用户发送微信消息
    for i, openid in enumerate(user_openids, 1):
        print(f"正在向用户{i}发送消息...")
        wechat_data["touser"] = openid
        send_wechat_message(token, openid, TEMPLATE_ID, wechat_data)
        # 避免发送过快，添加小延迟
        if i < len(user_openids):
            time.sleep(0.5)

if __name__ == "__main__":
    main()
