"""
Mathpix API 配置管理模块

安全地从环境变量读取 Mathpix API 凭证，避免硬编码密钥。
"""

import os
from typing import Optional
from pathlib import Path

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    # 加载 .env 文件（如果存在）
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        # 也尝试从当前目录加载
        load_dotenv()
except ImportError:
    # 如果没有 dotenv，手动读取 .env 文件
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                # 解析 KEY=VALUE 格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # 移除引号（如果有）
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    # 设置环境变量
                    os.environ[key] = value


class MathpixConfig:
    """Mathpix API 配置类"""

    def __init__(self):
        self.app_id: Optional[str] = os.getenv('MATHPIX_APP_ID')
        self.app_key: Optional[str] = os.getenv('MATHPIX_APP_KEY')
        self.api_url: str = os.getenv('MATHPIX_API_URL', 'https://api.mathpix.com/v3/text')
        self.timeout: int = int(os.getenv('MATHPIX_TIMEOUT', '30'))

    def is_configured(self) -> bool:
        """检查配置是否完整"""
        return bool(self.app_id and self.app_key)

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        验证配置

        返回: (is_valid, error_message)
        """
        if not self.app_id:
            return False, "MATHPIX_APP_ID 未设置"
        if not self.app_key:
            return False, "MATHPIX_APP_KEY 未设置"
        if len(self.app_id) < 10:
            return False, "MATHPIX_APP_ID 格式不正确"
        if len(self.app_key) < 20:
            return False, "MATHPIX_APP_KEY 格式不正确"
        return True, None

    def get_headers(self) -> dict:
        """
        获取 API 请求头

        返回包含认证信息的请求头字典
        """
        if not self.is_configured():
            raise ValueError("Mathpix API 未配置，请设置 MATHPIX_APP_ID 和 MATHPIX_APP_KEY")

        return {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'Content-Type': 'application/json'
        }

    def __repr__(self) -> str:
        """安全地显示配置信息（不暴露密钥）"""
        app_id_display = f"{self.app_id[:8]}..." if self.app_id else "未设置"
        app_key_display = "已设置" if self.app_key else "未设置"
        return f"MathpixConfig(app_id={app_id_display}, app_key={app_key_display}, api_url={self.api_url})"


# 全局配置实例
_config: Optional[MathpixConfig] = None


def get_config() -> MathpixConfig:
    """
    获取全局配置实例（单例模式）

    返回: MathpixConfig 实例
    """
    global _config
    if _config is None:
        _config = MathpixConfig()
    return _config


def check_config() -> bool:
    """
    检查并验证配置

    返回: 配置是否有效
    """
    config = get_config()
    is_valid, error = config.validate()
    if not is_valid:
        print(f"❌ Mathpix API 配置错误: {error}")
        print("\n请按以下步骤配置：")
        print("1. 复制 .env.example 为 .env")
        print("2. 在 .env 文件中填入你的 MATHPIX_APP_ID 和 MATHPIX_APP_KEY")
        print("3. 确保 .env 文件在项目根目录")
        return False
    return True


if __name__ == '__main__':
    """配置检查脚本"""
    print("🔍 检查 Mathpix API 配置...")
    config = get_config()

    print(f"\n配置状态: {config}")

    is_valid, error = config.validate()
    if is_valid:
        print("✅ 配置有效")
        print(f"   API URL: {config.api_url}")
        print(f"   超时设置: {config.timeout}秒")
    else:
        print(f"❌ 配置无效: {error}")
        print("\n配置方法：")
        print("1. 创建 .env 文件（从 .env.example 复制）")
        print("2. 填入以下内容：")
        print("   MATHPIX_APP_ID=your_app_id")
        print("   MATHPIX_APP_KEY=your_app_key")
