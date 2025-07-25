#!/usr/bin/env python3
"""
配置验证测试脚本
用于验证config.json配置文件的正确性和交易逻辑
"""

import json
import sys
from main import get_stock_price, analyze_stock_decision

def test_config():
    """测试配置文件的有效性"""
    print("🧪 开始配置验证测试...")
    print("=" * 50)
    
    # 读取配置文件
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        print(f"✅ 配置文件读取成功，发现 {len(config_data)} 个配置项")
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        return False
    
    # 验证每个配置项
    for i, stock in enumerate(config_data, 1):
        print(f"\n📊 测试配置项 {i}: {stock.get('name', 'Unknown')}")
        
        # 检查必需字段
        required_fields = ['name', 'code', 'base_price', 'buy_price', 'sell_rules']
        for field in required_fields:
            if field not in stock:
                print(f"❌ 缺少必需字段: {field}")
                return False
            else:
                print(f"✅ {field}: {stock[field]}")
        
        # 验证sell_rules结构
        if not isinstance(stock['sell_rules'], list) or len(stock['sell_rules']) == 0:
            print("❌ sell_rules 必须是非空列表")
            return False
        
        for j, rule in enumerate(stock['sell_rules']):
            if 'trigger_percent_increase' not in rule or 'sell_percent_of_position' not in rule:
                print(f"❌ sell_rules[{j}] 缺少必需字段")
                return False
        
        print(f"✅ sell_rules 包含 {len(stock['sell_rules'])} 条规则")
    
    return True

def test_real_price():
    """测试实时价格获取"""
    print("\n🌐 测试实时价格获取...")
    print("=" * 50)
    
    with open('config.json', 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    for stock in config_data:
        code = stock['code']
        name = stock['name']
        
        print(f"🔄 测试 {name}({code})...")
        price = get_stock_price(code)
        
        if price is not None:
            print(f"✅ 价格获取成功: ¥{price}")
            
            # 测试决策分析
            decision = analyze_stock_decision(stock, price)
            print(f"🎯 决策结果: {decision['decision']}")
            print(f"📝 详情: {decision['detail']}")
            
        else:
            print(f"❌ 价格获取失败")
            return False
    
    return True

def test_scenarios():
    """测试不同价格场景下的决策逻辑"""
    print("\n🎭 测试决策场景...")
    print("=" * 50)
    
    with open('config.json', 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    stock = config_data[0]  # 使用第一个配置项
    base_price = stock['base_price']
    buy_price = stock['buy_price']
    
    # 测试场景
    scenarios = [
        ("价值买入场景", buy_price - 0.1),
        ("持仓观察场景", base_price + 0.1),
        ("5%卖出场景", base_price * 1.05),
        ("10%卖出场景", base_price * 1.10),
        ("15%卖出场景", base_price * 1.15),
        ("20%卖出场景", base_price * 1.20),
    ]
    
    for scenario_name, test_price in scenarios:
        print(f"\n🧪 {scenario_name} (价格: ¥{test_price:.3f})")
        decision = analyze_stock_decision(stock, test_price)
        print(f"   结果: {decision['decision']}")
        print(f"   说明: {decision['detail']}")
    
    return True

def main():
    """主测试函数"""
    print("🚀 股票监控系统配置验证")
    print("=" * 50)
    
    success = True
    
    # 运行各项测试
    if not test_config():
        success = False
    
    if not test_real_price():
        success = False
        
    if not test_scenarios():
        success = False
    
    # 输出最终结果
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有测试通过！配置文件和系统运行正常")
    else:
        print("❌ 测试失败，请检查配置文件和网络连接")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
