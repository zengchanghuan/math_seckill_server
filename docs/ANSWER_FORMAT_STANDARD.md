# 答案格式标准（数学考试规范）

## 核心原则

> **所有答案必须是精确值。使用截断（Truncated）或四舍五入（Rounded）的小数来表示无理数，将视为错误答案。**

---

## 答案类别

### 1. 精确有理数（Exact Rational Numbers）

#### 定义

必须以**整数**或**最简分数**形式表示。有限小数（如 0.5）在评测系统允许时可接受。

#### 表示规则

**整数形式**

```
0, 1, 2, -1, -3, 5, ...
```

**最简分数形式**

```latex
\frac{1}{2}, \frac{3}{4}, \frac{2}{3}, \frac{5}{6}, ...
```

**有限小数（可接受）**

```
0.5, 0.25, 0.75, 1.5, 2.5, ...
```

#### 示例

| 表达式 | 最佳答案 | 可接受 | 说明 |
|--------|----------|--------|------|
| sin(30°) | `\frac{1}{2}` | `0.5` | 精确有理数 |
| cos(60°) | `\frac{1}{2}` | `0.5` | 精确有理数 |
| 1÷2 | `\frac{1}{2}` | `0.5` | 精确有理数 |
| 3÷4 | `\frac{3}{4}` | `0.75` | 精确有理数 |

#### 判断标准

```python
def is_exact_rational(value):
    """判断是否为精确有理数"""
    # 整数
    if isinstance(value, int):
        return True

    # 分数形式（LaTeX）
    if '\\frac{' in value and '\\sqrt' not in value:
        return True

    # 有限小数（可转换为分数）
    if isinstance(value, float):
        # 检查是否可以表示为简单分数
        from fractions import Fraction
        frac = Fraction(value).limit_denominator(100)
        if float(frac) == value:
            return True

    return False
```

---

### 2. 精确无理数（Exact Irrational Numbers）

#### 定义

必须以包含**根式（Radicals）**和/或**数学常量（π, e）**的**最简化代数表达式**表示。

#### 表示规则

**根式形式**

```latex
\sqrt{2}, \sqrt{3}, \sqrt{5}, \sqrt[3]{2}, ...
\frac{\sqrt{2}}{2}, \frac{\sqrt{3}}{2}, \frac{2\sqrt{3}}{3}, ...
```

**π 和 e**

```latex
\pi, 2\pi, \frac{\pi}{2}, \frac{\pi}{3}, \frac{\pi}{4}, ...
e, e^2, \frac{e}{2}, \ln 2, ...
```

**组合形式**

```latex
\sqrt{2} + \sqrt{3}
\pi + e
\frac{\sqrt{3} - 1}{2}
```

#### 示例

| 表达式 | 正确答案 | 状态 |
|--------|----------|------|
| cos(45°) | `\frac{\sqrt{2}}{2}` | ✅ 符合 |
| sin(60°) | `\frac{\sqrt{3}}{2}` | ✅ 符合 |
| tan(60°) | `\sqrt{3}` | ✅ 符合 |
| 圆周率 | `\pi` | ✅ 符合 |
| 自然常数 | `e` | ✅ 符合 |

#### 判断标准

```python
def is_exact_irrational(value):
    """判断是否为精确无理数"""
    # 包含根式
    if '\\sqrt' in value:
        return True

    # 包含π或e
    if '\\pi' in value or 'e' in value:
        return True

    return False
```

---

### 3. 近似值（Approximate Values）

#### 定义

不得使用**小数近似值（Decimal Approximation）**表示，除非题目明确要求保留特定位数的小数。

#### 禁止的表示

| 表达式 | 错误答案 | 状态 | 正确答案 |
|--------|----------|------|----------|
| cos(45°) | `0.707...` | ❌ 不符合 | `\frac{\sqrt{2}}{2}` |
| tan(60°) | `1.732...` | ❌ 不符合 | `\sqrt{3}` |
| sin(60°) | `0.866...` | ❌ 不符合 | `\frac{\sqrt{3}}{2}` |
| π | `3.14159...` | ❌ 不符合 | `\pi` |
| e | `2.71828...` | ❌ 不符合 | `e` |
| √2 | `1.414...` | ❌ 不符合 | `\sqrt{2}` |

#### 例外情况

**题目明确要求时**

```
题目：计算 cos(45°)，结果保留3位小数。
答案：0.707  ✅ （题目要求）
```

---

## 完整对照表

### 三角函数特殊值

| 角度 | sin | cos | tan |
|------|-----|-----|-----|
| 0° | `0` | `1` | `0` |
| 30° | `\frac{1}{2}` 或 `0.5` | `\frac{\sqrt{3}}{2}` | `\frac{\sqrt{3}}{3}` |
| 45° | `\frac{\sqrt{2}}{2}` | `\frac{\sqrt{2}}{2}` | `1` |
| 60° | `\frac{\sqrt{3}}{2}` | `\frac{1}{2}` 或 `0.5` | `\sqrt{3}` |
| 90° | `1` | `0` | undefined |
| 120° | `\frac{\sqrt{3}}{2}` | `-\frac{1}{2}` 或 `-0.5` | `-\sqrt{3}` |
| 135° | `\frac{\sqrt{2}}{2}` | `-\frac{\sqrt{2}}{2}` | `-1` |
| 150° | `\frac{1}{2}` 或 `0.5` | `-\frac{\sqrt{3}}{2}` | `-\frac{\sqrt{3}}{3}` |
| 180° | `0` | `-1` | `0` |

### 常用无理数

| 表达式 | 精确形式 | 禁止形式 |
|--------|----------|----------|
| √2 | `\sqrt{2}` | `1.414...` |
| √3 | `\sqrt{3}` | `1.732...` |
| √5 | `\sqrt{5}` | `2.236...` |
| √2/2 | `\frac{\sqrt{2}}{2}` | `0.707...` |
| √3/2 | `\frac{\sqrt{3}}{2}` | `0.866...` |
| π | `\pi` | `3.14159...` |
| 2π | `2\pi` | `6.28318...` |
| π/2 | `\frac{\pi}{2}` | `1.5708...` |
| e | `e` | `2.71828...` |

---

## 题目生成规则

### 规则1：有理数答案

```python
# ✅ 正确
answer = "\\frac{1}{2}"  # 分数形式（推荐）
answer = "0.5"           # 有限小数（可接受）

# ✅ 都符合精确有理数标准
```

### 规则2：无理数答案

```python
# ✅ 正确
answer = "\\frac{\\sqrt{2}}{2}"  # 精确无理数
answer = "\\sqrt{3}"              # 精确无理数
answer = "\\pi"                   # 精确无理数

# ❌ 错误
answer = "0.707"   # 近似值，不符合
answer = "1.732"   # 近似值，不符合
answer = "3.14"    # 近似值，不符合
```

### 规则3：选项生成

```python
def generate_trig_options(correct_answer):
    """生成三角函数选项"""

    # 所有选项必须是精确值
    options_pool = [
        '0',                      # 精确有理数
        '\\frac{1}{2}',          # 精确有理数
        '0.5',                    # 精确有理数（有限小数）
        '\\frac{\\sqrt{2}}{2}',  # 精确无理数
        '\\frac{\\sqrt{3}}{2}',  # 精确无理数
        '1',                      # 精确有理数
        '\\sqrt{3}',             # 精确无理数
    ]

    # ❌ 禁止使用
    forbidden = [
        '0.707',   # 近似值
        '0.866',   # 近似值
        '1.732',   # 近似值
    ]

    return generate_distinct_options(correct_answer, options_pool, 4)
```

---

## 验证检查清单

生成题目后必须检查：

- [ ] 有理数：使用整数或最简分数（有限小数可接受）
- [ ] 无理数：使用根式或数学常量（π, e）
- [ ] 无近似值：无截断或四舍五入的小数
- [ ] √2/2 而非 0.707
- [ ] √3 而非 1.732
- [ ] π 而非 3.14
- [ ] 所有答案均为精确值

---

## 代码实现

### 答案格式验证器

```python
def validate_answer_format(answer):
    """验证答案格式是否符合标准"""

    # 检查是否为近似值
    if '.' in answer:
        # 提取小数部分
        decimal_part = answer.split('.')[-1]

        # 有限小数（≤2位）→ 可能是精确有理数
        if len(decimal_part) <= 2:
            # 检查是否可转为简单分数
            try:
                from fractions import Fraction
                frac = Fraction(float(answer)).limit_denominator(100)
                if abs(float(frac) - float(answer)) < 1e-10:
                    return True, "精确有理数（有限小数）"
            except:
                pass

        # 多位小数 → 可能是近似值
        else:
            return False, f"疑似近似值（{len(decimal_part)}位小数）"

    # 检查是否包含根式或数学常量
    if any(symbol in answer for symbol in ['\\sqrt', '\\pi', 'e']):
        return True, "精确无理数"

    # 检查是否为分数
    if '\\frac' in answer:
        if '\\sqrt' in answer:
            return True, "精确无理数（含根式分数）"
        else:
            return True, "精确有理数（分数形式）"

    # 整数或字母
    return True, "精确值"

# 示例
validate_answer_format("0.5")                    # ✅ 精确有理数
validate_answer_format("\\frac{1}{2}")          # ✅ 精确有理数
validate_answer_format("\\frac{\\sqrt{2}}{2}")  # ✅ 精确无理数
validate_answer_format("0.707")                  # ❌ 疑似近似值
```

---

## 总结

| 类别 | 表示方式 | 示例 | 状态 |
|------|----------|------|------|
| 精确有理数 | 整数/最简分数/有限小数 | `\frac{1}{2}` 或 `0.5` | ✅ |
| 精确无理数 | 根式/π/e | `\frac{\sqrt{2}}{2}` | ✅ |
| 近似值 | 小数近似 | `0.707...` | ❌ |

**核心：所有答案必须是精确值，禁止使用近似值。**





