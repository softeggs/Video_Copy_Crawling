"""
API Key 余额查询工具
"""
import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from utils.logger import logger

class APIBalanceChecker:
    """API Key 余额检查器"""
    
    def __init__(self, base_url: str = "https://api2.qiandao.mom"):
        """初始化余额检查器
        
        Args:
            base_url: API 基础 URL
        """
        # 保留原始 base_url（包含 /v1）
        self.base_url = base_url.rstrip('/')
        # 移除 /v1 的版本用于旧接口
        self.base_url_no_v1 = self.base_url.replace('/v1', '')
    
    def check_subscription(self, api_key: str) -> Optional[Dict]:
        """查询订阅信息（额度、过期时间等）
        
        Args:
            api_key: OpenAI API Key
            
        Returns:
            订阅信息字典
        """
        if not api_key:
            logger.warning("API Key 为空，无法查询订阅信息")
            return None
        
        try:
            url = f"{self.base_url}/dashboard/billing/subscription"
            
            logger.info(f"查询订阅信息: {api_key[:20]}...")
            
            response = requests.get(
                url,
                timeout=10,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"订阅信息查询成功: {data}")
                return {
                    'success': True,
                    'data': data,
                    'message': self._format_subscription_message(data)
                }
            else:
                logger.error(f"订阅信息查询失败，状态码: {response.status_code}")
                return {
                    'success': False,
                    'data': {},
                    'message': f"查询失败（状态码: {response.status_code}）"
                }
                
        except Exception as e:
            logger.error(f"订阅信息查询异常: {str(e)}")
            return {
                'success': False,
                'data': {},
                'message': f"查询异常: {str(e)}"
            }
    
    def check_usage(self, api_key: str, days: int = 30) -> Optional[Dict]:
        """查询使用量统计
        
        Args:
            api_key: OpenAI API Key
            days: 查询最近多少天的数据
            
        Returns:
            使用量信息字典
        """
        if not api_key:
            logger.warning("API Key 为空，无法查询使用量")
            return None
        
        try:
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            url = f"{self.base_url}/dashboard/billing/usage"
            params = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
            
            logger.info(f"查询使用量: {api_key[:20]}... (最近 {days} 天)")
            
            response = requests.get(
                url,
                params=params,
                timeout=10,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"使用量查询成功: {data}")
                return {
                    'success': True,
                    'data': data,
                    'message': self._format_usage_message(data, days)
                }
            else:
                logger.error(f"使用量查询失败，状态码: {response.status_code}")
                return {
                    'success': False,
                    'data': {},
                    'message': f"查询失败（状态码: {response.status_code}）"
                }
                
        except Exception as e:
            logger.error(f"使用量查询异常: {str(e)}")
            return {
                'success': False,
                'data': {},
                'message': f"查询异常: {str(e)}"
            }
    
    def check_balance(self, api_key: str) -> Optional[Dict]:
        """查询 API Key 余额（综合查询）
        
        Args:
            api_key: OpenAI API Key
            
        Returns:
            余额信息字典，包含订阅信息、使用量和调用记录
        """
        if not api_key:
            logger.warning("API Key 为空，无法查询余额")
            return None
        
        result = {
            'success': False,
            'subscription': None,
            'usage': None,
            'logs': None,
            'message': ''
        }
        
        # 1. 查询订阅信息
        subscription = self.check_subscription(api_key)
        if subscription and subscription['success']:
            result['subscription'] = subscription
            result['success'] = True
        
        # 2. 查询使用量
        usage = self.check_usage(api_key, days=30)
        if usage and usage['success']:
            result['usage'] = usage
            result['success'] = True
        
        # 3. 查询调用记录（旧接口）
        logs = self._check_logs(api_key)
        if logs and logs['success']:
            result['logs'] = logs
            result['success'] = True
        
        # 生成综合消息
        if result['success']:
            messages = []
            
            # 计算剩余额度
            total_limit = None
            total_usage = None
            remaining = None
            
            if result['subscription'] and result['subscription']['data']:
                sub_data = result['subscription']['data']
                total_limit = sub_data.get('hard_limit_usd') or sub_data.get('hard_limit')
            
            if result['usage'] and result['usage']['data']:
                usage_data = result['usage']['data']
                if 'total_usage' in usage_data:
                    total_usage = usage_data['total_usage']
            
            # 计算剩余额度
            if total_limit is not None and total_usage is not None:
                used_amount = total_usage * 0.01  # 1 usage = 0.01 额度
                remaining = total_limit - used_amount
                messages.append(f"剩余额度: ${remaining:.2f} / ${total_limit:.2f}")
            
            if result['subscription']:
                messages.append(result['subscription']['message'])
            if result['usage']:
                messages.append(result['usage']['message'])
            if result['logs']:
                messages.append(result['logs']['message'])
            
            result['message'] = ' | '.join(messages)
            result['remaining'] = remaining
            result['total_limit'] = total_limit
            result['used_amount'] = total_usage * 0.01 if total_usage else None
        else:
            result['message'] = "所有查询接口均失败"
        
        return result
    
    def _check_logs(self, api_key: str) -> Optional[Dict]:
        """查询调用记录（旧接口）
        
        Args:
            api_key: OpenAI API Key
            
        Returns:
            调用记录信息字典
        """
        try:
            url = f"{self.base_url_no_v1}/api/log/token"
            params = {"key": api_key}
            
            logger.info(f"查询调用记录: {api_key[:20]}...")
            
            response = requests.get(
                url,
                params=params,
                timeout=10,
                headers={
                    "Referer": self.base_url_no_v1,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"调用记录查询成功")
                return {
                    'success': True,
                    'data': data,
                    'message': self._format_logs_message(data)
                }
            else:
                logger.warning(f"调用记录查询失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"调用记录查询异常: {str(e)}")
            return None
    
    def _format_subscription_message(self, data: Dict) -> str:
        """格式化订阅信息"""
        try:
            # 常见字段: hard_limit_usd, has_payment_method, access_until 等
            if 'hard_limit_usd' in data:
                limit = data.get('hard_limit_usd', 0)
                return f"总额度: ${limit:.2f}"
            
            if 'hard_limit' in data:
                limit = data.get('hard_limit', 0)
                return f"总额度: ${limit:.2f}"
            
            if 'plan' in data:
                plan = data.get('plan', {})
                title = plan.get('title', 'Unknown')
                return f"订阅计划: {title}"
            
            return "订阅信息已获取"
            
        except Exception as e:
            logger.warning(f"解析订阅信息失败: {str(e)}")
            return "订阅信息已获取"
    
    def _format_usage_message(self, data: Dict, days: int) -> str:
        """格式化使用量信息"""
        try:
            # API 返回格式: {"object":"list","total_usage":104}
            # 1 usage = 0.01 额度
            if 'total_usage' in data:
                total_usage = data.get('total_usage', 0)
                cost = total_usage * 0.01  # 转换为额度
                return f"最近 {days} 天使用: {total_usage} usage (${cost:.2f})"
            
            if 'total_cost' in data:
                cost = data.get('total_cost', 0)
                return f"最近 {days} 天费用: ${cost:.2f}"
            
            return f"最近 {days} 天使用量已获取"
            
        except Exception as e:
            logger.warning(f"解析使用量信息失败: {str(e)}")
            return f"最近 {days} 天使用量已获取"
    
    def _format_logs_message(self, data: Dict) -> str:
        """格式化调用记录信息"""
        try:
            # 这个 API 返回的是使用记录列表
            if 'data' in data and isinstance(data['data'], list):
                records = data['data']
                if not records:
                    return "暂无调用记录"
                
                # 统计总使用量
                total_prompt_tokens = sum(r.get('prompt_tokens', 0) for r in records)
                total_completion_tokens = sum(r.get('completion_tokens', 0) for r in records)
                total_tokens = total_prompt_tokens + total_completion_tokens
                
                return f"{len(records)} 次调用，{total_tokens:,} tokens"
            
            return "调用记录已获取"
            
        except Exception as e:
            logger.warning(f"解析调用记录失败: {str(e)}")
            return "调用记录已获取"
    
    def print_balance(self, api_key: str) -> None:
        """打印 API Key 余额信息（用于命令行）
        
        Args:
            api_key: OpenAI API Key
        """
        print("\n" + "=" * 60)
        print("🔍 查询 API Key 使用情况")
        print("=" * 60)
        
        result = self.check_balance(api_key)
        
        if result and result['success']:
            print(f"\n✅ {result['message']}")
            
            # 显示详细的余额信息
            if result.get('remaining') is not None:
                remaining = result['remaining']
                total = result.get('total_limit', 0)
                used = result.get('used_amount', 0)
                percentage = (used / total * 100) if total > 0 else 0
                
                print(f"\n💰 额度详情:")
                print(f"  总额度: ${total:.2f}")
                print(f"  已使用: ${used:.2f} ({percentage:.1f}%)")
                print(f"  剩余额度: ${remaining:.2f}")
                
                # 余额警告
                if remaining < 1:
                    print(f"  ⚠️  警告: 余额不足 $1，建议及时充值！")
                elif remaining < 5:
                    print(f"  ⚠️  提示: 余额较低，建议关注")
            
            # 显示使用量详情
            if result.get('usage') and result['usage']['data']:
                usage_data = result['usage']['data']
                if 'total_usage' in usage_data:
                    total_usage = usage_data['total_usage']
                    print(f"\n📊 使用统计:")
                    print(f"  总使用量: {total_usage} usage")
                    print(f"  等价费用: ${total_usage * 0.01:.2f}")
            
            # 打印最近的调用记录
            if result.get('logs') and result['logs']['data']:
                logs_data = result['logs']['data']
                if 'data' in logs_data and isinstance(logs_data['data'], list):
                    records = logs_data['data']
                    if records:
                        print(f"\n📝 最近 {min(5, len(records))} 次调用:")
                        print("-" * 60)
                        
                        for i, record in enumerate(records[:5], 1):
                            timestamp = record.get('created_at', 0)
                            dt = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                            model = record.get('model_name', 'unknown')
                            prompt_tokens = record.get('prompt_tokens', 0)
                            completion_tokens = record.get('completion_tokens', 0)
                            use_time = record.get('use_time', 0)
                            
                            print(f"  {i}. {dt}")
                            print(f"     模型: {model}")
                            print(f"     Tokens: {prompt_tokens + completion_tokens:,} "
                                  f"(输入: {prompt_tokens:,}, 输出: {completion_tokens:,})")
                            print(f"     耗时: {use_time}s")
                            if i < min(5, len(records)):
                                print()
        else:
            message = result['message'] if result else "查询失败"
            print(f"\n❌ {message}")
        
        print("=" * 60 + "\n")

# 便捷函数
def check_api_balance(api_key: str, base_url: str = "https://api2.qiandao.mom") -> Optional[Dict]:
    """快速查询 API 余额
    
    Args:
        api_key: OpenAI API Key
        base_url: API 基础 URL
        
    Returns:
        余额信息字典
    """
    checker = APIBalanceChecker(base_url)
    return checker.check_balance(api_key)


class KimiBalanceChecker:
    """Kimi (Moonshot AI) API 余额检查器"""
    
    BASE_URL = "https://api.moonshot.cn/v1"
    
    def __init__(self, api_key: str):
        """初始化 Kimi 余额检查器
        
        Args:
            api_key: Kimi API Key
        """
        self.api_key = api_key
    
    def check_balance(self) -> Optional[Dict]:
        """查询 Kimi API 余额
        
        Returns:
            余额信息字典，包含：
            - available_balance: 可用余额（人民币）
            - voucher_balance: 代金券余额
            - cash_balance: 现金余额
        """
        if not self.api_key:
            logger.warning("Kimi API Key 为空，无法查询余额")
            return {
                'success': False,
                'message': 'API Key 未配置'
            }
        
        try:
            url = f"{self.BASE_URL}/users/me/balance"
            
            logger.info(f"查询 Kimi 余额: {self.api_key[:15]}...")
            
            response = requests.get(
                url,
                timeout=10,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Kimi 余额查询成功: {data}")
                
                # 解析返回数据
                if data.get('code') == 0 and data.get('status'):
                    balance_data = data.get('data', {})
                    available = balance_data.get('available_balance', 0)
                    voucher = balance_data.get('voucher_balance', 0)
                    cash = balance_data.get('cash_balance', 0)
                    
                    return {
                        'success': True,
                        'available_balance': available,
                        'voucher_balance': voucher,
                        'cash_balance': cash,
                        'message': f"可用余额: ¥{available:.2f} (代金券: ¥{voucher:.2f}, 现金: ¥{cash:.2f})"
                    }
                else:
                    return {
                        'success': False,
                        'message': f"查询失败: {data.get('message', '未知错误')}"
                    }
            else:
                logger.error(f"Kimi 余额查询失败，状态码: {response.status_code}")
                return {
                    'success': False,
                    'message': f"查询失败（状态码: {response.status_code}）"
                }
                
        except Exception as e:
            logger.error(f"Kimi 余额查询异常: {str(e)}")
            return {
                'success': False,
                'message': f"查询异常: {str(e)}"
            }
    
    def print_balance(self) -> None:
        """打印 Kimi API 余额信息（用于命令行）"""
        print("\n" + "=" * 50)
        print("🌙 Kimi (Moonshot AI) 余额查询")
        print("=" * 50)
        
        result = self.check_balance()
        
        if result and result['success']:
            print(f"\n✅ {result['message']}")
            print(f"\n💰 余额详情:")
            print(f"  可用余额: ¥{result['available_balance']:.2f}")
            print(f"  代金券余额: ¥{result['voucher_balance']:.2f}")
            print(f"  现金余额: ¥{result['cash_balance']:.2f}")
            
            # 余额警告
            available = result['available_balance']
            if available <= 0:
                print(f"\n  ⚠️  警告: 余额已用尽，请及时充值！")
            elif available < 5:
                print(f"\n  ⚠️  提示: 余额较低，建议关注")
        else:
            message = result['message'] if result else "查询失败"
            print(f"\n❌ {message}")
        
        print("=" * 50 + "\n")


def check_kimi_balance(api_key: str) -> Optional[Dict]:
    """快速查询 Kimi API 余额
    
    Args:
        api_key: Kimi API Key
        
    Returns:
        余额信息字典
    """
    checker = KimiBalanceChecker(api_key)
    return checker.check_balance()
