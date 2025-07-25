#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Secrets 配置助手
帮助用户生成完整的GitHub Secrets配置清单
"""

def collect_config():
    """收集配置信息"""
    print("🔧 GitHub Secrets 配置助手")
    print("=" * 50)
    print("此工具将帮助您生成完整的GitHub Secrets配置清单")
    print("⚠️ 注意：请确保信息安全，不要在不安全的环境中输入敏感信息")
    print()
    
    # 收集基本配置
    app_id = input("请输入微信测试号 AppID: ").strip()
    app_secret = input("请输入微信测试号 AppSecret: ").strip()
    template_id = input("请输入消息模板 ID: ").strip()
    
    if not all([app_id, app_secret, template_id]):
        print("❌ 基本配置信息不完整，请重新运行")
        return
    
    # 收集用户OpenID
    print("\n👥 用户OpenID配置（最多20个）")
    print("提示：输入空行结束输入")
    
    openids = []
    while len(openids) < 20:
        prompt = f"第{len(openids)+1}个用户OpenID"
        if len(openids) == 0:
            prompt += " (必填)"
        else:
            prompt += " (可选)"
        prompt += ": "
        
        openid = input(prompt).strip()
        if not openid:
            break
        openids.append(openid)
    
    if not openids:
        print("❌ 至少需要一个用户OpenID")
        return
    
    # 生成配置清单
    print("\n📋 GitHub Secrets 配置清单")
    print("=" * 50)
    print("请在GitHub仓库的 Settings > Secrets and variables > Actions 中添加以下Secrets：")
    print()
    
    secrets = [
        ("WECHAT_APP_ID", app_id),
        ("WECHAT_APP_SECRET", app_secret),
        ("WECHAT_TEMPLATE_ID", template_id),
    ]
    
    for i, openid in enumerate(openids, 1):
        secrets.append((f"WECHAT_USER_OPENID{i}", openid))
    
    # 显示配置表格
    print("| Secret Name              | Secret Value                     |")
    print("|--------------------------|----------------------------------|")
    for name, value in secrets:
        # 隐藏敏感信息的部分字符
        display_value = value
        if len(value) > 8:
            display_value = value[:4] + "*" * (len(value) - 8) + value[-4:]
        print(f"| `{name:<24}` | `{display_value:<30}` |")
    
    print()
    print("📝 配置步骤：")
    print("1. 复制上表中的Secret Name和对应的完整Secret Value")
    print("2. 在GitHub仓库中逐一添加这些Secrets") 
    print("3. 确保Secret Name完全匹配（区分大小写）")
    print("4. 运行GitHub Actions进行测试")
    
    # 保存到文件
    save_to_file = input("\n💾 是否保存配置到文件？(y/N): ").strip().lower()
    if save_to_file in ['y', 'yes']:
        with open('github_secrets_config.txt', 'w', encoding='utf-8') as f:
            f.write("GitHub Secrets 配置清单\n")
            f.write("=" * 50 + "\n\n")
            for name, value in secrets:
                f.write(f"{name} = {value}\n")
            f.write(f"\n配置时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print("✅ 配置已保存到 github_secrets_config.txt")
        print("⚠️ 请妥善保管此文件，包含敏感信息")
    
    print("\n🎉 配置清单生成完成！")

def main():
    try:
        collect_config()
    except KeyboardInterrupt:
        print("\n\n❌ 用户取消操作")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    main()
