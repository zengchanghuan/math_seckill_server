# Math Seckill Server

数学秒杀服务器后端 API，基于 FastAPI 构建，用于动态生成数学题目（特别是导数相关题目）。

## 📋 项目简介

这是一个为数学秒杀应用提供后端服务的 API 服务器。服务器使用 SymPy 库进行符号数学计算，能够自动生成数学题目、答案和解题步骤，并以 LaTeX 格式返回，方便前端进行数学公式渲染。

## ✨ 功能特性

- 🎯 **动态题目生成**：基于指定的主题和难度自动生成数学题目
- 📐 **符号计算**：使用 SymPy 进行精确的符号数学运算
- 📝 **LaTeX 支持**：题目、答案和解题步骤均以 LaTeX 格式返回
- 🔄 **CORS 支持**：配置了跨域资源共享，方便前端应用调用
- 🚀 **热重载**：开发模式下支持代码修改后自动重启
- 📚 **自动 API 文档**：提供 Swagger UI 交互式文档

## 🛠 技术栈

- **FastAPI** 0.115.0 - 现代、快速的 Web 框架
- **Uvicorn** 0.30.5 - ASGI 服务器
- **SymPy** 1.13.2 - 符号数学计算库
- **Pydantic** 2.9.2 - 数据验证和序列化
- **Python** 3.12+

## 📁 项目结构

```
math_seckill_server/
├── core/
│   └── problem_generator.py  # 题目生成核心逻辑
├── main.py                   # FastAPI 应用入口
├── schemas.py                # Pydantic 数据模型
├── requirements.txt          # Python 依赖包
└── README.md                # 项目文档
```

## 🚀 快速开始

### 环境要求

- Python 3.12 或更高版本
- pip 包管理器

### 安装步骤

1. **克隆项目**（如果是从仓库获取）

```bash
cd math_seckill_server
```

2. **创建虚拟环境**（推荐）

```bash
python3 -m venv venv
```

3. **激活虚拟环境**

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

4. **安装依赖**

```bash
pip install -r requirements.txt
```

如果下载速度较慢，可以使用国内镜像源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 运行服务器

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务器启动后，你可以访问：

- **API 根路径**：http://localhost:8000
- **交互式 API 文档**：http://localhost:8000/docs
- **替代 API 文档**：http://localhost:8000/redoc

## 📡 API 文档

### 健康检查

**GET** `/`

检查服务器运行状态。

**响应示例：**
```json
{
  "status": "ok"
}
```

### 生成题目

**POST** `/api/problem`

根据指定的主题和难度生成数学题目。

**请求体：**
```json
{
  "topic": "导数基础",
  "difficulty": "基础"
}
```

**响应示例：**
```json
{
  "id": "backend-temp",
  "topic": "导数基础",
  "difficulty": "基础",
  "question": "求函数 $f(x) = 3x^{3} - 2x^{2} + 5x - 1$ 的导数。",
  "answer": "A",
  "solution": "利用幂函数求导法则 $\\frac{d}{dx}(x^n) = nx^{n-1}$，对多项式 $f(x) = 3x^{3} - 2x^{2} + 5x - 1$ 中的每一项分别求导：\\[6pt]f'(x) = 9x^{2} - 4x + 5",
  "options": [
    "$9x^{2} - 4x + 5$",
    "$9x^{2} - 4x + 8$",
    "$9x^{2} - 4x + 2$",
    "$\\frac{3 x^{4}}{4} - \\frac{2 x^{3}}{3} + \\frac{5 x^{2}}{2} - x$"
  ],
  "tags": ["导数", "多项式", "后端生成"]
}
```

**请求参数说明：**

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| topic | string | 否 | "导数基础" | 题目主题 |
| difficulty | string | 否 | "基础" | 题目难度 |

**响应字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 题目唯一标识 |
| topic | string | 题目主题 |
| difficulty | string | 题目难度 |
| question | string | 题目内容（LaTeX 格式） |
| answer | string | 正确答案标签（A/B/C/D） |
| solution | string | 解题步骤（LaTeX 格式） |
| options | array | 选项列表（LaTeX 格式） |
| tags | array | 题目标签 |

## 💡 使用示例

### 使用 cURL

```bash
# 健康检查
curl http://localhost:8000/

# 生成题目
curl -X POST "http://localhost:8000/api/problem" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "导数基础",
    "difficulty": "基础"
  }'
```

### 使用 Python

```python
import requests

# 生成题目
response = requests.post(
    "http://localhost:8000/api/problem",
    json={
        "topic": "导数基础",
        "difficulty": "基础"
    }
)

problem = response.json()
print(f"题目: {problem['question']}")
print(f"答案: {problem['answer']}")
```

### 使用 JavaScript/Flutter

```javascript
fetch('http://localhost:8000/api/problem', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    topic: '导数基础',
    difficulty: '基础'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🔧 开发说明

### 添加新的题目类型

要添加新的题目生成器，请在 `core/problem_generator.py` 中：

1. 创建新的生成函数（如 `generate_integral_basic()`）
2. 在 `generate_problem()` 函数中添加路由逻辑

示例：

```python
def generate_problem(topic: str, difficulty: str) -> Dict:
    if topic == "导数基础" and difficulty == "基础":
        return generate_derivative_basic()
    elif topic == "积分基础" and difficulty == "基础":
        return generate_integral_basic()
    # 默认返回导数基础题目
    return generate_derivative_basic()
```

### 数据模型

所有数据模型定义在 `schemas.py` 中：

- `ProblemRequest`: 题目生成请求模型
- `ProblemResponse`: 题目响应模型

## 🔒 CORS 配置

当前配置允许所有来源访问（`allow_origins=["*"]`），适用于开发环境。生产环境建议限制为特定的域名：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📝 注意事项

1. **LaTeX 格式**：所有数学公式以 LaTeX 格式返回，前端需要使用支持 LaTeX 的渲染库（如 Flutter 的 `flutter_math_fork` 或 Web 的 `KaTeX`）

2. **题目 ID**：当前题目 ID 为临时值 "backend-temp"，后续可以扩展为真实的唯一标识

3. **题目类型**：目前仅支持"导数基础-基础"类型的题目，其他类型会复用该生成器

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[在此添加许可证信息]

## 📞 联系方式

[在此添加联系方式]


