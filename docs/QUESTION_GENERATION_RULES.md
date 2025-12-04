# 题目生成规则 - 符合真实考试标准

## 核心原则

### 1. 使用符号而非浮点数
```python
# ❌ 错误示例
answer = 3.14159265359
answer = 2.71828182846

# ✅ 正确示例  
answer = "\\pi"
answer = "e"
answer = "\\frac{\\pi}{2}"
```

### 2. 三角函数特殊值
```python
# 常用三角函数值（全部使用符号）
TRIG_VALUES = {
    0: "0",
    30: {
        'sin': "\\frac{1}{2}",
        'cos': "\\frac{\\sqrt{3}}{2}",
        'tan': "\\frac{\\sqrt{3}}{3}"
    },
    45: {
        'sin': "\\frac{\\sqrt{2}}{2}",
        'cos': "\\frac{\\sqrt{2}}{2}",
        'tan': "1"
    },
    60: {
        'sin': "\\frac{\\sqrt{3}}{2}",
        'cos': "\\frac{1}{2}",
        'tan': "\\sqrt{3}"
    },
    90: {
        'sin': "1",
        'cos': "0",
        'tan': "\\text{undefined}"
    }
}
```

### 3. 选项必须不重复
```python
def generate_distinct_options(correct_answer, pool, n=4):
    """生成n个不重复的选项"""
    options = [correct_answer]
    
    # 从选项池中随机选择，确保不重复
    available = [opt for opt in pool if opt != correct_answer]
    options.extend(random.sample(available, min(n-1, len(available))))
    
    # 确保恰好n个选项
    while len(options) < n:
        options.append(generate_distractor())
    
    # 去重
    options = list(dict.fromkeys(options))
    
    # 打乱顺序
    random.shuffle(options)
    
    return options
```

## 各章节生成规则

### 第1章：三角函数

#### 求值题
```python
def generate_trig_value_question():
    """生成三角函数求值题"""
    angle = random.choice([0, 30, 45, 60, 90, 120, 135, 150, 180])
    func = random.choice(['sin', 'cos', 'tan'])
    
    # 使用符号答案
    if angle == 30 and func == 'sin':
        answer = "\\frac{1}{2}"
    elif angle == 45 and func == 'cos':
        answer = "\\frac{\\sqrt{2}}{2}"
    # ... 其他特殊值
    
    # 生成干扰选项（全部符号）
    distractors = [
        "\\frac{1}{2}",
        "\\frac{\\sqrt{2}}{2}",
        "\\frac{\\sqrt{3}}{2}",
        "1"
    ]
    
    return generate_distinct_options(answer, distractors)
```

#### 周期和性质
```python
# 周期必须使用π的倍数
periods = {
    'sin': "2\\pi",
    'cos': "2\\pi",
    'tan': "\\pi"
}
```

### 第2章：代数与方程

#### 根式化简
```python
# ❌ 错误
answer = 1.414213562373095

# ✅ 正确
answer = "\\sqrt{2}"
```

#### 分数答案
```python
# 使用有理数表示
from fractions import Fraction

# ❌ 错误
answer = 0.5

# ✅ 正确
answer = "\\frac{1}{2}"
```

### 第4章：参数方程

#### 涉及π的参数
```python
# 参数范围使用π
parameter_range = {
    't': "[0, 2\\pi]",
    '\\theta': "[0, \\pi]"
}

# ❌ 错误
t_values = [0, 1.57, 3.14, 4.71, 6.28]

# ✅ 正确
t_values = ["0", "\\frac{\\pi}{2}", "\\pi", "\\frac{3\\pi}{2}", "2\\pi"]
```

### 第6章：复数

#### 欧拉公式
```python
# e^(iθ) = cos(θ) + i·sin(θ)

# ❌ 错误
answer = 2.71828 * (0.5 + 0.866j)

# ✅ 正确
answer = "e^{i\\frac{\\pi}{3}}"
# 或
answer = "\\frac{1}{2} + \\frac{\\sqrt{3}}{2}i"
```

## 干扰选项生成规则

### 1. 三角函数题
```python
TRIG_DISTRACTOR_POOL = [
    "0",
    "\\frac{1}{2}",
    "\\frac{\\sqrt{2}}{2}",
    "\\frac{\\sqrt{3}}{2}",
    "1",
    "-\\frac{1}{2}",
    "-\\frac{\\sqrt{2}}{2}",
    "-\\frac{\\sqrt{3}}{2}",
    "-1",
    "\\frac{\\sqrt{3}}{3}",
    "\\sqrt{3}"
]
```

### 2. 周期/角度题
```python
ANGLE_DISTRACTOR_POOL = [
    "\\frac{\\pi}{6}",
    "\\frac{\\pi}{4}",
    "\\frac{\\pi}{3}",
    "\\frac{\\pi}{2}",
    "\\pi",
    "2\\pi"
]
```

### 3. 指数/对数题
```python
EXPONENTIAL_DISTRACTOR_POOL = [
    "e",
    "e^2",
    "\\frac{e}{2}",
    "\\ln 2",
    "\\ln e",
    "1"
]
```

## 质量检查清单

生成题目后必须检查：

- [ ] 答案不是浮点数（除非必要）
- [ ] 使用了数学符号（π, e, √等）
- [ ] 4个选项完全不重复
- [ ] 答案LaTeX格式正确
- [ ] 干扰选项合理（不要太明显）
- [ ] 符合真实考试标准

## 代码模板

```python
def generate_question_template():
    """标准题目生成模板"""
    # 1. 生成题目内容
    question_text = "..."
    
    # 2. 计算正确答案（使用符号）
    correct_answer = "\\frac{\\pi}{2}"  # 符号形式
    
    # 3. 选择干扰项池
    distractor_pool = APPROPRIATE_POOL
    
    # 4. 生成不重复选项
    options = generate_distinct_options(
        correct_answer, 
        distractor_pool, 
        n=4
    )
    
    # 5. 确保选项不重复
    assert len(options) == len(set(options)), "选项重复！"
    
    # 6. 找到正确答案索引
    answer_index = options.index(correct_answer)
    answer_letter = ['A', 'B', 'C', 'D'][answer_index]
    
    return {
        'question': question_text,
        'answer': answer_letter,
        'options': options,
        'type': 'choice'
    }
```

## 更新记录

- 2025-12-03: 创建规范文档
- 重点：使用π和e等符号，避免浮点数，确保选项不重复

