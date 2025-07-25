#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 部署故障排除指南
"""

def main():
    print("🔧 GitHub Actions 故障排除指南")
    print("=" * 60)
    
    print("\n📋 常见问题及解决方案:")
    
    print("\n1. ❌ 找不到 main.py 文件")
    print("   原因: 文件未正确上传到GitHub仓库")
    print("   解决方案:")
    print("   ✅ 确保将整个 Stock-Watcher-Bot 文件夹上传到GitHub")
    print("   ✅ 检查仓库根目录是否包含以下文件:")
    print("      - main.py")
    print("      - config.json") 
    print("      - requirements.txt")
    print("      - .github/workflows/daily_check.yml")
    
    print("\n2. ❌ 微信配置错误")
    print("   原因: GitHub Secrets 未正确配置")
    print("   解决方案:")
    print("   ✅ 在GitHub仓库设置中配置以下Secrets:")
    print("      - WECHAT_APP_ID")
    print("      - WECHAT_APP_SECRET")
    print("      - WECHAT_TEMPLATE_ID")
    print("      - WECHAT_USER_OPENID1")
    
    print("\n3. ❌ 依赖安装失败")
    print("   原因: requirements.txt 文件问题")
    print("   解决方案:")
    print("   ✅ 确保 requirements.txt 内容正确")
    print("   ✅ 使用 pip install -r requirements.txt")
    
    print("\n🚀 推荐的部署步骤:")
    print("=" * 60)
    steps = [
        "1. 在GitHub创建新仓库",
        "2. 上传所有项目文件到仓库根目录",
        "3. 配置GitHub Secrets",
        "4. 在Actions页面手动触发工作流",
        "5. 查看运行日志排除问题"
    ]
    
    for step in steps:
        print(f"   {step}")
    
    print("\n📂 正确的仓库结构:")
    print("=" * 60)
    structure = """
    your-repo/
    ├── .github/
    │   └── workflows/
    │       └── daily_check.yml
    ├── main.py
    ├── config.json
    ├── requirements.txt
    ├── README.md
    └── WECHAT_CONFIG.md
    """
    print(structure)
    
    print("\n💡 调试技巧:")
    print("=" * 60)
    print("   ✅ 查看GitHub Actions运行日志")
    print("   ✅ 确认文件路径和文件名大小写")
    print("   ✅ 使用工作流中的调试步骤查看文件列表")
    print("   ✅ 先测试简单的工作流再添加复杂功能")

if __name__ == "__main__":
    main()
