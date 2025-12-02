import random
from typing import Dict

import sympy as sp


def generate_derivative_basic() -> Dict:
    """
    生成一题简单的“导数基础-基础”题目，返回结构与 Flutter 端 Problem 模型对齐。
    """
    x = sp.symbols("x")

    # 随机生成一个 2~3 次多项式，例如 3x^3 - 2x^2 + 5x - 1
    degree = random.choice([2, 3])
    coeffs = [random.randint(-5, 5) or 1 for _ in range(degree + 1)]

    poly = sum(coeffs[i] * x ** (degree - i) for i in range(degree)) + coeffs[-1]
    derivative = sp.diff(poly, x)

    question_latex = sp.latex(poly)
    answer_expr = derivative
    answer_latex = sp.latex(answer_expr)

    # 构造一些干扰选项
    options = [answer_latex]
    wrong1 = sp.latex(sp.diff(poly, x) + random.randint(1, 3))
    wrong2 = sp.latex(sp.diff(poly, x) - random.randint(1, 3))
    wrong3 = sp.latex(sp.integrate(poly, x))
    options.extend([wrong1, wrong2, wrong3])
    random.shuffle(options)

    correct_index = options.index(answer_latex)
    answer_label = ["A", "B", "C", "D"][correct_index]

    # 简单解题过程说明
    solution_steps = (
        r"利用幂函数求导法则 $\frac{d}{dx}(x^n) = nx^{n-1}$，"
        r"对多项式 $f(x) = " + question_latex + r"$ 中的每一项分别求导："
        r"\\[6pt]"
        r"f'(x) = " + answer_latex
    )

    return {
        "id": "backend-temp",  # 前端暂时不依赖具体 ID，可后续扩展为真正流水号
        "topic": "导数基础",
        "difficulty": "基础",
        "question": r"求函数 $f(x) = " + question_latex + r"$ 的导数。",
        "options": [f"${opt}$" for opt in options],
        "answer": answer_label,
        "solution": solution_steps,
        "tags": ["导数", "多项式", "后端生成"],
    }


def generate_problem(topic: str, difficulty: str) -> Dict:
    """
    简单路由：当前仅支持“导数基础-基础”，其他组合先复用这一题型。
    """
    # 未来可以根据 topic/difficulty 分发到不同的生成函数
    return generate_derivative_basic()



