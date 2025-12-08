# Mathpix API 配置指南

## 概述

本项目使用 Mathpix Convert API 进行数学公式识别和转换。为了安全地管理 API 凭证，我们使用环境变量配置文件（`.env`）来存储敏感信息。

## 安全原则

⚠️ **重要安全提示：**

1. **永远不要**将 API 密钥硬编码在代码中
2. **永远不要**将 `.env` 文件提交到 Git（已在 `.gitignore` 中）
3. **永远不要**在公开场合分享你的 API 密钥
4. 定期轮换 API 密钥
5. 限制 API 密钥的权限范围

## 配置步骤

### 1. 安装依赖

确保已安装 `python-dotenv`：

```bash
pip install -r requirements.txt
```

### 2. 创建配置文件

复制配置模板：

```bash
cp .env.example .env
```

### 3. 填入 API 凭证

编辑 `.env` 文件，填入你的 Mathpix API 凭证：

```env
MATHPIX_APP_ID=your_app_id_here
MATHPIX_APP_KEY=your_app_key_here
```

### 4. 验证配置

运行配置检查脚本：

```bash
python mathpix_config.py
```

如果配置正确，会显示：
```
✅ 配置有效
   API URL: https://api.mathpix.com/v3/text
   超时设置: 30秒
```

## 使用方法

### 在代码中使用

```python
from mathpix_config import get_config, check_config

# 检查配置
if not check_config():
    print("配置无效，请检查 .env 文件")
    exit(1)

# 获取配置
config = get_config()

# 获取 API 请求头
headers = config.get_headers()

# 使用 headers 发送请求
import requests
response = requests.post(
    config.api_url,
    headers=headers,
    json={"src": "your_image_url"},
    timeout=config.timeout
)
```

## 环境变量说明

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `MATHPIX_APP_ID` | ✅ | - | Mathpix 应用 ID |
| `MATHPIX_APP_KEY` | ✅ | - | Mathpix 应用密钥 |
| `MATHPIX_API_URL` | ❌ | `https://api.mathpix.com/v3/text` | API 端点 |
| `MATHPIX_TIMEOUT` | ❌ | `30` | 请求超时时间（秒） |

## 获取 API 凭证

1. 访问 [Mathpix 官网](https://mathpix.com/)
2. 注册账号并登录
3. 进入 Dashboard
4. 创建新应用或使用现有应用
5. 获取 `APP_ID` 和 `APP_KEY`

## 相关文件

- `mathpix_config.py` - 配置管理模块
- `.env.example` - 配置模板
- `.env` - 实际配置文件（不提交到 Git）
- `.gitignore` - 确保 `.env` 不被提交
