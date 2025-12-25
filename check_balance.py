"""
查询 API Key 余额
"""
from utils.api_balance_checker import APIBalanceChecker
from utils.config import config

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("💰 API Key 余额查询工具")
    print("=" * 60)
    
    # 检查配置
    if not config.OPENAI_API_KEY:
        print("\n❌ 错误: 未配置 OPENAI_API_KEY")
        print("请在 .env 文件中配置 API Key")
        return
    
    if not config.OPENAI_BASE_URL:
        print("\n⚠️  警告: 未配置 OPENAI_BASE_URL")
        print("余额查询功能仅支持中转 API")
        return
    
    # 显示配置信息
    print(f"\n📋 当前配置:")
    print(f"  Base URL: {config.OPENAI_BASE_URL}")
    print(f"  API Key: {config.OPENAI_API_KEY[:20]}...")
    print(f"  模型: {config.OPENAI_MODEL}")
    
    # 查询余额
    checker = APIBalanceChecker(config.OPENAI_BASE_URL)
    checker.print_balance(config.OPENAI_API_KEY)
    
    # 提示信息
    print("💡 提示:")
    print("  • 如果余额不足，请充值或更换 API Key")
    print("  • 可以在 .env 文件中更新 OPENAI_API_KEY")
    print("  • 余额查询 URL: {}/api/log/token".format(config.OPENAI_BASE_URL))
    print()

if __name__ == "__main__":
    main()
