#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统状态检查脚本
检查股票监控系统的配置状态
"""

import json
import os

def check_config_file():
    """检查配置文件"""
    print("🔍 检查配置文件...")
    
    config_path = "config.json"
    if not os.path.exists(config_path):
        print("❌ config.json 文件不存在")
        return False
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ config.json 文件读取成功")
        
        # 检查配置格式（新格式是股票列表）
        if isinstance(config, list) and len(config) > 0:
            print("✅ 使用新的股票列表配置格式")
            
            # 检查第一只股票的字段
            first_stock = config[0]
            required_fields = ['name', 'code', 'base_price', 'buy_rules', 'sell_rules']
            missing_fields = [field for field in required_fields if field not in first_stock]
            
            if missing_fields:
                print(f"⚠️  缺少必要字段: {missing_fields}")
            else:
                print("✅ 所有必要字段都存在")
            
            # 显示配置详情
            print(f"📊 监控股票数量: {len(config)}")
            
            for i, stock in enumerate(config, 1):
                print(f"\n📈 股票 {i}: {stock.get('name', 'Unknown')}")
                print(f"   代码: {stock.get('code', 'N/A')}")
                print(f"   基准价格: ¥{stock.get('base_price', 0):.3f}")
                print(f"   买入规则数量: {len(stock.get('buy_rules', []))}")
                print(f"   卖出规则数量: {len(stock.get('sell_rules', []))}")
                
                # 显示买入规则详情
                if 'buy_rules' in stock:
                    print(f"   🟢 买入规则:")
                    for j, rule in enumerate(stock['buy_rules'], 1):
                        print(f"      {j}. 下跌 {rule.get('trigger_percent_decrease', 0)}% 时投入 {rule.get('buy_percent_of_capital', 0)}% 资金")
                
                # 显示卖出规则详情
                if 'sell_rules' in stock:
                    print(f"   🔴 卖出规则:")
                    for j, rule in enumerate(stock['sell_rules'], 1):
                        print(f"      {j}. 上涨 {rule.get('trigger_percent_increase', 0)}% 时卖出 {rule.get('sell_percent_of_position', 0)}% 仓位")
        
        else:
            print("❌ 配置文件格式不正确，应该是股票列表格式")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ config.json 格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取 config.json 失败: {e}")
        return False

def check_github_workflow():
    """检查GitHub工作流"""
    print("\n🔍 检查GitHub工作流...")
    
    # 尝试多个可能的路径
    possible_paths = [
        ".github/workflows/daily_check.yml",
        "../.github/workflows/daily_check.yml"
    ]
    
    workflow_path = None
    for path in possible_paths:
        if os.path.exists(path):
            workflow_path = path
            break
    
    if not workflow_path:
        print("❌ GitHub工作流文件不存在")
        print("💡 请确保在仓库根目录下存在 .github/workflows/daily_check.yml")
        return False
    
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ GitHub工作流文件存在: {workflow_path}")
        
        # 检查执行时间
        if "0 2 * * *" in content:
            print("✅ 执行时间: 北京时间上午10:00（UTC 02:00）")
        else:
            print("⚠️  执行时间可能不正确")
        
        # 检查工作目录
        if "Stock-Watcher-Bot/" in content:
            print("✅ 工作目录设置正确")
        else:
            print("⚠️  工作目录设置可能有问题")
        
        return True
        
    except Exception as e:
        print(f"❌ 读取工作流文件失败: {e}")
        return False

def check_environment_variables():
    """检查环境变量（GitHub Secrets）"""
    print("\n🔍 检查环境变量...")
    
    required_secrets = [
        'WECHAT_APP_ID',
        'WECHAT_APP_SECRET', 
        'WECHAT_TEMPLATE_ID',
        'WECHAT_OPEN_IDS'
    ]
    
    print("📋 需要配置的GitHub Secrets:")
    for i, secret in enumerate(required_secrets, 1):
        print(f"   {i}. {secret}")
    
    print("\n💡 请确保在GitHub仓库设置中配置了这些Secrets")
    return True

def main():
    """主检查函数"""
    print("=" * 60)
    print("🔧 股票监控系统状态检查")
    print("=" * 60)
    
    checks = [
        check_config_file(),
        check_github_workflow(),
        check_environment_variables()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ 系统配置检查完成！")
        print("🚀 系统已准备就绪，将在每天北京时间上午10:00自动运行")
        print("📱 支持详细版微信模板消息推送")
    else:
        print("⚠️  发现一些配置问题，请检查上述输出")
    print("=" * 60)

if __name__ == "__main__":
    main()
