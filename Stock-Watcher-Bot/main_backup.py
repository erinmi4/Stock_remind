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
            print("✅ access_token 获取成功")
            return data["access_token"]
        else:
            print(f"❌ 获取access_token失败: {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求access_token时发生网络错误: {e}")
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
        print(f"🔄 正在获取 {stock_code} 的价格数据...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 解析新浪财经返回的数据
        content = response.text.strip()
        if not content or '=' not in content:
            print(f"❌ 数据格式异常: {content}")
            return None
            
        # 提取引号内的数据
        data_start = content.find('"') + 1
        data_end = content.rfind('"')
        if data_start <= 0 or data_end <= data_start:
            print(f"❌ 无法解析数据格式: {content}")
            return None
            
        data_str = content[data_start:data_end]
        parts = data_str.split(',')
        
        if len(parts) < 4:
            print(f"❌ 数据长度不足: {len(parts)} 项，内容: {data_str}")
            return None
            
        # 不同市场的价格字段位置
        if stock_code.startswith(("sh", "sz")):
            # A股/基金：当前价格在第3个位置（索引3）
            current_price = parts[3]
            stock_name = parts[0]
            print(f"✅ 价格获取成功: {stock_name}({stock_code}) 当前价格: ¥{current_price}")
            return float(current_price)
            
        elif stock_code.startswith("gb_"):
            # 美股：当前价格在第1个位置（索引1）
            current_price = parts[1]
            stock_name = parts[0]
            print(f"✅ 价格获取成功: {stock_name}({stock_code}) 当前价格: ${current_price}")
            return float(current_price)
            
        else:
            print(f"❌ 不支持的股票代码格式: {stock_code}")
            return None
            
    except (requests.exceptions.RequestException, ValueError, IndexError) as e:
        print(f"❌ 获取 {stock_code} 价格失败: {e}")
        return None
    except Exception as e:
        print(f"❌ 解析 {stock_code} 数据时出现未知错误: {e}")
        return None

def analyze_stock_decision(stock_config, current_price):
    """分析股票决策：分层纪律卖出、分层买入或持仓观察
    
    Args:
        stock_config: 股票配置字典
        current_price: 当前价格
        
    Returns:
        dict: 包含决策信息的字典
    """
    name = stock_config['name']
    code = stock_config['code']
    base_price = stock_config['base_price']
    buy_price = stock_config['buy_price']
    buy_rules = stock_config.get('buy_rules', [])
    sell_rules = stock_config['sell_rules']
    note = stock_config.get('note', '')
    
    # 计算当前涨幅
    price_change_percent = (current_price - base_price) / base_price * 100
    
    print(f"📊 分析 {name}({code}):")
    print(f"   当前价格: ¥{current_price:.3f}")
    print(f"   基准价格: ¥{base_price:.3f}")
    print(f"   买入价格: ¥{buy_price:.3f}")
    print(f"   当前涨幅: {price_change_percent:+.2f}%")
    
    # 检查分层买入规则（从基准价下跌触发）
    if buy_rules:
        for rule in sorted(buy_rules, key=lambda x: x['trigger_percent_decrease'], reverse=True):
            required_drop = -rule['trigger_percent_decrease']  # 转为负数
            if price_change_percent <= required_drop:
                buy_percent = rule['buy_percent_of_capital']
                decision = "🔴 分层买入"
                detail = f"触发 -{rule['trigger_percent_decrease']}% 规则，建议买入 {buy_percent}% 资金"
                print(f"   💡 决策: {decision} - {detail}")
                return {
                    'name': name,
                    'code': code,
                    'decision': decision,
                    'detail': detail,
                    'current_price': current_price,
                    'base_price': base_price,
                    'price_change_percent': price_change_percent,
                    'note': note,
                    'action_required': True
                }
    
    # 检查基础价值买入
    if current_price <= buy_price:
        decision = "🔴 价值买入"
        detail = f"当前价格 ¥{current_price:.3f} ≤ 买入价 ¥{buy_price:.3f}"
        print(f"   💡 决策: {decision} - {detail}")
        return {
            'name': name,
            'code': code,
            'decision': decision,
            'detail': detail,
            'current_price': current_price,
            'base_price': base_price,
            'price_change_percent': price_change_percent,
            'note': note,
            'action_required': True
        }
    
    # 检查分层纪律卖出规则
    triggered_rule = None
    for rule in sorted(sell_rules, key=lambda x: x['trigger_percent_increase'], reverse=True):
        if price_change_percent >= rule['trigger_percent_increase']:
            triggered_rule = rule
            break
    
    if triggered_rule:
        trigger_percent = triggered_rule['trigger_percent_increase']
        sell_percent = triggered_rule['sell_percent_of_position']
        decision = "🟢 纪律卖出"
        detail = f"触发 +{trigger_percent}% 规则，建议卖出 {sell_percent}% 仓位"
        print(f"   💡 决策: {decision} - {detail}")
        return {
            'name': name,
            'code': code,
            'decision': decision,
            'detail': detail,
            'current_price': current_price,
            'base_price': base_price,
            'price_change_percent': price_change_percent,
            'note': note,
            'action_required': True
        }
    
    # 默认持仓观察
    decision = "🟡 持仓观察"
    detail = f"当前涨幅 {price_change_percent:+.2f}%，未触发交易条件"
    print(f"   💡 决策: {decision} - {detail}")
    return {
        'name': name,
        'code': code,
        'decision': decision,
        'detail': detail,
        'current_price': current_price,
        'base_price': base_price,
        'price_change_percent': price_change_percent,
        'note': note,
        'action_required': False
    }

def generate_report(decisions):
    """生成投资报告
    
    Args:
        decisions: 决策结果列表
        
    Returns:
        tuple: (报告标题, 报告内容)
    """
    # 统计需要操作的股票数量
    action_count = sum(1 for d in decisions if d['action_required'])
    
    # 动态标题
    if action_count > 0:
        title = f"🚨 投资提醒！发现 {action_count} 项操作机会"
    else:
        title = "📈 投资仪表盘日报"
    
    # 生成报告内容
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content_lines = [
        f"📅 报告时间: {current_time}",
        f"📊 监控标的: {len(decisions)} 只",
        f"⚡ 操作机会: {action_count} 项",
        "",
        "=" * 40,
        ""
    ]
    
    for i, decision in enumerate(decisions, 1):
        content_lines.extend([
            f"【{i}】{decision['name']} ({decision['code']})",
            f"💰 现价: ¥{decision['current_price']:.3f}",
            f"📐 基准: ¥{decision['base_price']:.3f}",
            f"📈 涨幅: {decision['price_change_percent']:+.2f}%",
            f"🎯 决策: {decision['decision']}",
            f"📝 说明: {decision['detail']}",
            f"💭 备注: {decision['note']}",
            ""
        ])
    
    content_lines.extend([
        "=" * 40,
        "🤖 本报告由股票监控系统自动生成",
        "⚠️  投资有风险，决策需谨慎"
    ])
    
    return title, "\n".join(content_lines)

def send_wechat_message_with_decisions(access_token, open_id, template_id, title, content, decisions):
    """向单个用户发送微信模板消息 - 支持详细版模板（带决策信息）"""
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    headers = {'Content-Type': 'application/json'}
    
    # 获取第一只股票的详细信息（用于详细模板）
    first_stock = decisions[0] if decisions else None
    
    # 统计信息
    stock_count = str(len(decisions))
    action_count = str(sum(1 for d in decisions if d['action_required']))
    
    # 格式1：详细版模板（完整的12个字段支持）
    detailed_data = {
        "touser": open_id,
        "template_id": template_id,
        "data": {
            "title": {"value": title, "color": "#FF0000" if "🚨" in title else "#173177"},
            "report_time": {"value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "color": "#173177"},
            "stock_count": {"value": stock_count, "color": "#173177"},
            "action_count": {"value": action_count, "color": "#FF0000" if int(action_count) > 0 else "#173177"},
            "stock_name": {"value": first_stock['name'] if first_stock else "南方中证500ETF", "color": "#173177"},
            "current_price": {"value": f"¥{first_stock['current_price']:.3f}" if first_stock else "¥6.000", "color": "#173177"},
            "base_price": {"value": f"¥{first_stock['base_price']:.3f}" if first_stock else "¥6.140", "color": "#173177"},
            "price_change": {"value": f"{first_stock['price_change_percent']:+.2f}%" if first_stock else "+0.00%", "color": "#FF0000" if first_stock and first_stock['price_change_percent'] > 0 else "#00AA00" if first_stock and first_stock['price_change_percent'] < 0 else "#173177"},
            "decision": {"value": first_stock['decision'] if first_stock else "🟡 持仓观察", "color": "#FF0000" if first_stock and "🔴" in first_stock['decision'] else "#00AA00" if first_stock and "🟢" in first_stock['decision'] else "#173177"},
            "suggestion": {"value": first_stock['detail'] if first_stock else "继续观察市场变化", "color": "#666666"},
            "note": {"value": first_stock['note'] if first_stock else "中盘股核心配置", "color": "#999999"},
            "warning": {"value": "投资有风险，决策需谨慎", "color": "#999999"}
        }
    }
    
    # 格式2：简化详细模板（6个主要字段）
    simple_detailed_data = {
        "touser": open_id,
        "template_id": template_id,
        "data": {
            "title": {"value": title, "color": "#FF0000" if "🚨" in title else "#173177"},
            "report_time": {"value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "color": "#173177"},
            "stock_count": {"value": stock_count + "只", "color": "#173177"},
            "action_count": {"value": action_count + "项", "color": "#FF0000" if int(action_count) > 0 else "#173177"},
            "content": {"value": content[:600] + "..." if len(content) > 600 else content, "color": "#666666"},
            "tip": {"value": "投资有风险，决策需谨慎", "color": "#999999"}
        }
    }
    
    # 格式3：标准模板（first, keyword1, keyword2, remark）
    standard_data = {
        "touser": open_id,
        "template_id": template_id,
        "data": {
            "first": {"value": title, "color": "#FF0000" if "🚨" in title else "#173177"},
            "keyword1": {"value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "color": "#173177"},
            "keyword2": {"value": content[:500] + "..." if len(content) > 500 else content, "color": "#666666"},
            "remark": {"value": "📊 投资有风险，决策需谨慎", "color": "#999999"}
        }
    }
    
    # 格式4：极简模板（只有content字段）
    simple_data = {
        "touser": open_id,
        "template_id": template_id,
        "data": {
            "content": {"value": f"{title}\n\n{content[:800]}", "color": "#173177"}
        }
    }
    
    try:
        print(f"📤 正在发送微信消息给 {open_id}...")
        
        # 首先尝试详细版模板
        response = requests.post(url, data=json.dumps(detailed_data), headers=headers, timeout=5)
        response.raise_for_status()
        result = response.json()
        
        if result.get("errcode") == 0:
            print(f"✅ 消息成功发送给 {open_id}（详细版模板）")
            return
        elif result.get("errcode") == 40001:
            print(f"⚠️  详细模板字段不匹配，尝试简化详细模板...")
            
            # 尝试简化详细模板
            response = requests.post(url, data=json.dumps(simple_detailed_data), headers=headers, timeout=5)
            result = response.json()
            
            if result.get("errcode") == 0:
                print(f"✅ 消息成功发送给 {open_id}（简化详细模板）")
                return
            else:
                print(f"⚠️  简化详细模板失败，尝试标准模板...")
                
                # 尝试标准模板
                response = requests.post(url, data=json.dumps(standard_data), headers=headers, timeout=5)
                result = response.json()
                
                if result.get("errcode") == 0:
                    print(f"✅ 消息成功发送给 {open_id}（标准模板）")
                    return
                else:
                    print(f"⚠️  标准模板失败，尝试极简模板...")
                    
                    # 尝试极简模板
                    response = requests.post(url, data=json.dumps(simple_data), headers=headers, timeout=5)
                    result = response.json()
                    
                    if result.get("errcode") == 0:
                        print(f"✅ 消息成功发送给 {open_id}（极简模板）")
                    else:
                        print(f"❌ 所有模板格式都失败: {result}")
        else:
            print(f"❌ 消息发送失败: {result}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 发送消息时发生网络错误: {e}")

def                     send_wechat_message_with_decisions(access_token, open_id, template_id, title, content, decisions):
    """向单个用户发送微信模板消息 - 支持多种模板格式"""
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    headers = {'Content-Type': 'application/json'}
    
    # 统计信息
    stock_count = "1"
    action_count = "1" if "🚨" in title else "0"
    
    # 格式1：标准模板（first, keyword1, keyword2, remark）
    standard_data = {
        "touser": open_id,
        "template_id": template_id,
        "data": {
            "first": {"value": title, "color": "#FF0000" if "🚨" in title else "#173177"},
            "keyword1": {"value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "color": "#173177"},
            "keyword2": {"value": content[:500] + "..." if len(content) > 500 else content, "color": "#666666"},
            "remark": {"value": "� 投资有风险，决策需谨慎", "color": "#999999"}
        }
    }
    
    # 格式2：详细模板（完整的12个字段支持）
    detailed_data = {
        "touser": open_id,
        "template_id": template_id,
        "data": {
            "title": {"value": title, "color": "#FF0000" if "🚨" in title else "#173177"},
            "report_time": {"value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "color": "#173177"},
            "stock_count": {"value": stock_count, "color": "#173177"},
            "action_count": {"value": action_count, "color": "#FF0000" if action_count != "0" else "#173177"},
            "stock_name": {"value": "南方中证500ETF", "color": "#173177"},
            "current_price": {"value": "获取中...", "color": "#173177"},
            "base_price": {"value": "¥6.140", "color": "#173177"},
            "price_change": {"value": "计算中...", "color": "#173177"},
            "decision": {"value": "分析中...", "color": "#173177"},
            "suggestion": {"value": content[:100] + "..." if len(content) > 100 else content, "color": "#666666"},
            "note": {"value": "中盘股核心配置，跟踪中证500指数", "color": "#999999"},
            "warning": {"value": "投资有风险，决策需谨慎", "color": "#999999"}
        }
    }
    
    # 格式3：极简模板（只有content字段）
    simple_data = {
        "touser": open_id,
        "template_id": template_id,
        "data": {
            "content": {"value": f"{title}\n\n{content[:800]}", "color": "#173177"}
        }
    }
    
    try:
        print(f"📤 正在发送微信消息给 {open_id}...")
        
        # 首先尝试标准模板
        response = requests.post(url, data=json.dumps(standard_data), headers=headers, timeout=5)
        response.raise_for_status()
        result = response.json()
        
        if result.get("errcode") == 0:
            print(f"✅ 消息成功发送给 {open_id}（标准模板）")
            return
        elif result.get("errcode") == 40001:
            print(f"⚠️  模板字段不匹配，尝试详细模板...")
            
            # 尝试详细模板
            response = requests.post(url, data=json.dumps(detailed_data), headers=headers, timeout=5)
            result = response.json()
            
            if result.get("errcode") == 0:
                print(f"✅ 消息成功发送给 {open_id}（详细模板）")
                return
            else:
                print(f"⚠️  详细模板失败，尝试极简模板...")
                
                # 尝试极简模板
                response = requests.post(url, data=json.dumps(simple_data), headers=headers, timeout=5)
                result = response.json()
                
                if result.get("errcode") == 0:
                    print(f"✅ 消息成功发送给 {open_id}（极简模板）")
                else:
                    print(f"❌ 所有模板格式都失败: {result}")
        else:
            print(f"❌ 消息发送失败: {result}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 发送消息时发生网络错误: {e}")

def main():
    """主执行函数"""
    print("🚀 股票监控系统启动")
    print("=" * 50)
    
    # 1. 从GitHub Actions的环境变量中读取微信配置
    APP_ID = os.environ.get('WECHAT_APP_ID')
    APP_SECRET = os.environ.get('WECHAT_APP_SECRET')
    TEMPLATE_ID = os.environ.get('WECHAT_TEMPLATE_ID')
    
    # 获取所有配置的OpenID（支持最多20个用户）
    user_openids = []
    for i in range(1, 21):
        openid = os.environ.get(f'WECHAT_USER_OPENID{i}')
        if openid:
            user_openids.append(openid)
    
    print(f"📱 检测到 {len(user_openids)} 个用户配置")
    
    # 2. 读取股票配置文件
    config_paths = [
        'Stock-Watcher-Bot/config.json',  # GitHub Actions路径
        'config.json',                     # 本地路径
        './config.json'                    # 当前目录
    ]
    
    config_data = None
    for config_path in config_paths:
        try:
            if os.path.exists(config_path):
                print(f"📋 正在读取配置文件: {config_path}")
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                print(f"✅ 配置文件读取成功，发现 {len(config_data)} 个监控标的")
                break
        except Exception as e:
            print(f"❌ 读取 {config_path} 失败: {e}")
            continue
    
    if not config_data:
        print("❌ 无法找到或读取配置文件")
        sys.exit(1)
    
    # 3. 获取实时价格并分析决策
    print("\n🔍 开始获取实时价格并分析...")
    print("=" * 50)
    
    decisions = []
    for stock in config_data:
        current_price = get_stock_price(stock['code'])
        if current_price is not None:
            decision = analyze_stock_decision(stock, current_price)
            decisions.append(decision)
            print()  # 空行分隔
        else:
            print(f"⚠️  跳过 {stock['name']}({stock['code']}) - 价格获取失败\n")
    
    if not decisions:
        print("❌ 未能获取任何股票价格，程序退出")
        sys.exit(1)
    
    # 4. 生成报告
    print("📊 正在生成投资分析报告...")
    title, content = generate_report(decisions)
    
    print(f"\n📄 报告预览:")
    print("=" * 50)
    print(f"标题: {title}")
    print(f"内容预览: {content[:200]}...")
    
    # 5. 发送微信通知
    if not user_openids:
        print("⚠️  未配置微信用户，跳过消息发送")
        print("✅ 程序执行完成（仅生成报告）")
        return
    
    print("\n📱 正在发送微信通知...")
    print("=" * 50)
    
    access_token = get_access_token(APP_ID, APP_SECRET)
    if not access_token:
        print("❌ 无法获取access_token，消息发送失败")
        sys.exit(1)
    
    for openid in user_openids:
        send_wechat_message_with_decisions(access_token, openid, TEMPLATE_ID, title, content, decisions)
        time.sleep(0.5)  # 避免发送过快
    
    print(f"\n✅ 程序执行完成！已向 {len(user_openids)} 个用户发送报告")
    print("=" * 50)

if __name__ == "__main__":
    main()
