#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
股票监控与提醒系统
简化版 - 专注于微信模板消息推送
"""

import requests
import json
import os
from datetime import datetime
import sys

def get_stock_price(stock_code):
    """获取股票实时价格 - 使用新浪财经API"""
    try:
        url = f"https://hq.sinajs.cn/list={stock_code}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://finance.sina.com.cn/'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.text.strip()
        if not data or '=""' in data:
            return None
        
        # 解析数据：var hq_str_sh510500="南方中证500ETF,5.987,6.140,..."
        info = data.split('"')[1].split(',')
        if len(info) < 4:
            return None
        
        stock_name = info[0]
        current_price = float(info[3])  # 当前价格
        
        return {
            'name': stock_name,
            'current_price': current_price,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        print(f"❌ 获取 {stock_code} 价格失败: {e}")
        return None

def analyze_stock_decision(stock_data, stock_config):
    """分析股票决策"""
    if not stock_data:
        return {
            'action_required': False,
            'decision': "🟡 数据获取失败",
            'detail': "无法获取股票价格数据",
            'note': stock_config.get('note', ''),
            'current_price': 0,
            'base_price': stock_config['base_price'],
            'price_change_percent': 0,
            'name': stock_config['name']
        }
    
    current_price = stock_data['current_price']
    base_price = stock_config['base_price']
    price_change_percent = ((current_price - base_price) / base_price) * 100
    
    # 检查买入规则
    for rule in stock_config.get('buy_rules', []):
        trigger_decrease = rule['trigger_percent_decrease']
        if price_change_percent <= -trigger_decrease:
            return {
                'action_required': True,
                'decision': "🟢 建议买入",
                'detail': f"价格下跌{abs(price_change_percent):.2f}%，触发{trigger_decrease}%买入策略",
                'note': stock_config.get('note', ''),
                'current_price': current_price,
                'base_price': base_price,
                'price_change_percent': price_change_percent,
                'name': stock_data['name']
            }
    
    # 检查卖出规则
    for rule in stock_config.get('sell_rules', []):
        trigger_increase = rule['trigger_percent_increase']
        if price_change_percent >= trigger_increase:
            return {
                'action_required': True,
                'decision': "🔴 建议卖出",
                'detail': f"价格上涨{price_change_percent:.2f}%，触发{trigger_increase}%卖出策略",
                'note': stock_config.get('note', ''),
                'current_price': current_price,
                'base_price': base_price,
                'price_change_percent': price_change_percent,
                'name': stock_data['name']
            }
    
    return {
        'action_required': False,
        'decision': "🟡 持仓观察",
        'detail': f"价格变动{price_change_percent:+.2f}%，暂无操作信号",
        'note': stock_config.get('note', ''),
        'current_price': current_price,
        'base_price': base_price,
        'price_change_percent': price_change_percent,
        'name': stock_data['name']
    }

def get_wechat_access_token(app_id, app_secret):
    """获取微信Access Token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'access_token' in data:
            print(f"✅ 成功获取微信Access Token")
            return data['access_token']
        else:
            print(f"❌ 获取微信Access Token失败: {data}")
            return None
            
    except Exception as e:
        print(f"❌ 获取微信Access Token异常: {e}")
        return None

def send_wechat_message(access_token, open_id, template_id, stock_decision):
    """发送微信模板消息"""
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    headers = {'Content-Type': 'application/json'}
    
    # 根据您的模板截图，调整字段名称
    template_data = {
        "touser": open_id,
        "template_id": template_id,
        "data": {
            # 基础信息（顶部3个字段）
            "时间": {
                "value": datetime.now().strftime("%H:%M"),
                "color": "#173177"
            },
            "标的": {
                "value": "1只",
                "color": "#173177"
            },
            "机会": {
                "value": "1项" if stock_decision['action_required'] else "0项",
                "color": "#FF0000" if stock_decision['action_required'] else "#173177"
            },
            
            # 详细信息字段
            "股票名称": {
                "value": stock_decision['name'],
                "color": "#173177"
            },
            "当前价格": {
                "value": f"¥{stock_decision['current_price']:.3f}",
                "color": "#173177"
            },
            "基准价格": {
                "value": f"¥{stock_decision['base_price']:.3f}",
                "color": "#173177"
            },
            "价格涨幅": {
                "value": f"{stock_decision['price_change_percent']:+.2f}%",
                "color": "#FF0000" if stock_decision['price_change_percent'] > 0 else "#00AA00" if stock_decision['price_change_percent'] < 0 else "#173177"
            },
            "投资决策": {
                "value": stock_decision['decision'],
                "color": "#FF0000" if "🔴" in stock_decision['decision'] else "#00AA00" if "🟢" in stock_decision['decision'] else "#173177"
            },
            "操作建议": {
                "value": stock_decision['detail'],
                "color": "#666666"
            },
            "备注": {
                "value": stock_decision['note'],
                "color": "#999999"
            },
            "提醒": {
                "value": "投资有风险，决策需谨慎",
                "color": "#999999"
            }
        }
    }
    
    try:
        print(f"📤 正在发送微信消息给 {open_id}...")
        response = requests.post(url, data=json.dumps(template_data), headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("errcode") == 0:
            print(f"✅ 消息成功发送给 {open_id}")
            return True
        else:
            print(f"❌ 消息发送失败: {result}")
            
            # 如果字段不匹配，尝试简化版本
            if result.get("errcode") == 40001:
                print("🔄 尝试发送简化版消息...")
                return send_simple_message(access_token, open_id, template_id, stock_decision)
            
            return False
            
    except Exception as e:
        print(f"❌ 发送消息时发生网络错误: {e}")
        return False

def send_simple_message(access_token, open_id, template_id, stock_decision):
    """发送简化版模板消息（备用方案）"""
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    headers = {'Content-Type': 'application/json'}
    
    # 尝试常见的模板格式
    simple_templates = [
        # 格式1: first, keyword1, keyword2, remark
        {
            "first": {
                "value": f"📊 股票监控提醒 - {stock_decision['name']}",
                "color": "#FF0000" if stock_decision['action_required'] else "#173177"
            },
            "keyword1": {
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "color": "#173177"
            },
            "keyword2": {
                "value": f"{stock_decision['decision']} - 当前价格¥{stock_decision['current_price']:.3f} ({stock_decision['price_change_percent']:+.2f}%)",
                "color": "#666666"
            },
            "remark": {
                "value": "投资有风险，决策需谨慎",
                "color": "#999999"
            }
        },
        # 格式2: content 单字段
        {
            "content": {
                "value": f"📊 股票监控提醒\n\n股票：{stock_decision['name']}\n当前：¥{stock_decision['current_price']:.3f}\n基准：¥{stock_decision['base_price']:.3f}\n涨跌：{stock_decision['price_change_percent']:+.2f}%\n决策：{stock_decision['decision']}\n建议：{stock_decision['detail']}\n\n⚠️ 投资有风险，决策需谨慎",
                "color": "#173177"
            }
        }
    ]
    
    for i, template_format in enumerate(simple_templates, 1):
        try:
            data = {
                "touser": open_id,
                "template_id": template_id,
                "data": template_format
            }
            
            response = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                print(f"✅ 简化消息发送成功（格式{i}）")
                return True
                
        except Exception as e:
            print(f"⚠️ 简化格式{i}失败: {e}")
            continue
    
    print("❌ 所有消息格式都发送失败")
    return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 股票监控系统启动")
    print("=" * 60)
    
    # 显示运行环境信息
    print(f"🐍 Python版本: {sys.version}")
    print(f"📁 当前工作目录: {os.getcwd()}")
    print(f"📂 目录内容: {os.listdir('.')}")
    
    # 从环境变量获取配置
    APP_ID = os.getenv('WECHAT_APP_ID')
    APP_SECRET = os.getenv('WECHAT_APP_SECRET')
    TEMPLATE_ID = os.getenv('WECHAT_TEMPLATE_ID')
    
    print(f"🔑 APP_ID存在: {'是' if APP_ID else '否'}")
    print(f"🔑 APP_SECRET存在: {'是' if APP_SECRET else '否'}")
    print(f"🔑 TEMPLATE_ID存在: {'是' if TEMPLATE_ID else '否'}")
    
    if not all([APP_ID, APP_SECRET, TEMPLATE_ID]):
        print("❌ 缺少必要的环境变量配置")
        print("需要配置: WECHAT_APP_ID, WECHAT_APP_SECRET, WECHAT_TEMPLATE_ID")
        sys.exit(1)
    
    # 获取用户OpenID列表
    open_ids = []
    for i in range(1, 21):
        openid = os.getenv(f'WECHAT_USER_OPENID{i}')
        if openid:
            open_ids.append(openid)
    
    if not open_ids:
        print("❌ 未配置任何用户OpenID")
        sys.exit(1)
    
    print(f"📱 配置了 {len(open_ids)} 个接收用户")
    
    # 读取股票配置 - 智能查找config.json文件
    config_paths = ['config.json', '../config.json', './config.json']
    stock_configs = None
    
    for config_path in config_paths:
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    stock_configs = json.load(f)
                print(f"✅ 成功读取配置文件: {config_path}")
                break
        except Exception as e:
            print(f"⚠️ 尝试读取 {config_path} 失败: {e}")
            continue
    
    if not stock_configs:
        print("❌ 无法找到或读取config.json配置文件")
        print("📁 当前工作目录:", os.getcwd())
        print("📂 目录内容:", os.listdir('.'))
        sys.exit(1)
    
    print(f"📊 监控 {len(stock_configs)} 只股票")
    
    # 获取微信Access Token
    access_token = get_wechat_access_token(APP_ID, APP_SECRET)
    if not access_token:
        print("❌ 无法获取微信Access Token")
        sys.exit(1)
    
    # 分析每只股票
    for stock_config in stock_configs:
        print(f"\n📈 分析股票: {stock_config['name']} ({stock_config['code']})")
        
        # 获取股票价格
        stock_data = get_stock_price(stock_config['code'])
        
        # 分析决策
        decision = analyze_stock_decision(stock_data, stock_config)
        
        print(f"💰 当前价格: ¥{decision['current_price']:.3f}")
        print(f"📊 基准价格: ¥{decision['base_price']:.3f}")
        print(f"📈 涨跌幅: {decision['price_change_percent']:+.2f}%")
        print(f"🎯 决策: {decision['decision']}")
        print(f"📝 详情: {decision['detail']}")
        
        # 如果需要操作，发送消息给所有用户
        if decision['action_required']:
            print(f"🚨 触发操作信号，发送提醒消息...")
            
            for openid in open_ids:
                send_wechat_message(access_token, openid, TEMPLATE_ID, decision)
        else:
            print(f"✅ 无需操作，继续观察")
    
    print("\n" + "=" * 60)
    print("✅ 股票监控完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
