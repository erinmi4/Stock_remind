#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署检查脚本
检查所有必要文件是否存在并提供部署指导
"""

import os
import json

def check_files():
    """检查必要文件是否存在"""
    print("📁 检查项目文件...")
    
    required_files = [
        "main.py",
        "config.json", 
        "requirements.txt",
        ".github/workflows/daily_check.yml",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    return len(missing_files) == 0

def check_config():
    """检查配置文件格式"""
    print("\n⚙️ 检查配置文件...")
    
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if not isinstance(config, list):
            print("❌ config.json 应该是一个数组")
            return False
        
        for i, stock in enumerate(config):
            required_keys = ['name', 'code', 'sell_price', 'buy_price']
            for key in required_keys:
                if key not in stock:
                    print(f"❌ 第{i+1}个股票配置缺少字段: {key}")
                    return False
        
        print(f"✅ 配置文件格式正确，共{len(config)}只股票")
        return True
        
    except json.JSONDecodeError:
        print("❌ config.json 格式错误")
        return False
    except FileNotFoundError:
        print("❌ config.json 文件不存在")
        return False

def show_deployment_guide():
    """显示部署指南"""
    print("\n🚀 部署指南:")
    print("=" * 50)
    
    steps = [
        "1. 将项目上传到GitHub仓库",
        "2. 配置GitHub Secrets (参考 WECHAT_CONFIG.md)",
        "3. 在微信测试号平台创建模板消息",
        "4. 关注测试号获取OpenID",
        "5. 在GitHub Actions中手动运行一次测试",
        "6. 检查微信是否收到测试消息",
        "7. 系统将每天自动运行"
    ]
    
    for step in steps:
        print(f"  {step}")
    
    print("\n📖 详细说明:")
    print("  - 微信配置: 查看 WECHAT_CONFIG.md")
    print("  - 测试配置: 运行 python test_config.py")
    print("  - 项目说明: 查看 README.md")

def main():
    print("🎯 Stock Watcher Bot 部署检查工具")
    print("=" * 50)
    
    # 检查文件
    files_ok = check_files()
    
    # 检查配置
    config_ok = check_config()
    
    # 显示部署指南
    show_deployment_guide()
    
    print("\n" + "=" * 50)
    if files_ok and config_ok:
        print("✅ 项目检查通过，可以开始部署！")
    else:
        print("❌ 项目检查失败，请修复上述问题后重试")

if __name__ == "__main__":
    main()
