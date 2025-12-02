import random
from typing import Dict

import sympy as sp
from core.problem_config import get_problem_type_for_difficulty


def generate_derivative_basic() -> Dict:
    """
    生成一题简单的"导数基础-基础"题目，返回结构与 Flutter 端 Problem 模型对齐。
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
        "difficulty": "L1",  # 更新为新难度体系
        "type": "choice",  # 选择题
        "question": r"求函数 $f(x) = " + question_latex + r"$ 的导数。",
        "options": [f"${opt}$" for opt in options],
        "answer": answer_label,
        "solution": solution_steps,
        "tags": ["导数", "多项式", "后端生成"],
        "answerType": None,  # 选择题不需要
        "answerExpr": None,  # 选择题不需要
    }


def generate_trig_choice_l1() -> Dict:
    """
    生成第1章三角函数的L1选择题：定义域、值域、周期判断
    """
    functions = [
        ("\\sin(x)", "所有实数", "[-1, 1]", "2\\pi"),
        ("\\cos(x)", "所有实数", "[-1, 1]", "2\\pi"),
        ("\\tan(x)", "x \\neq \\frac{\\pi}{2} + k\\pi (k \\in \\mathbb{Z})", "所有实数", "\\pi"),
    ]
    
    func_latex, domain, range_str, period = random.choice(functions)
    
    question_types = ["domain", "range", "period"]
    q_type = random.choice(question_types)
    
    if q_type == "domain":
        question = f"函数 $f(x) = {func_latex}$ 的定义域是？"
        correct = domain
        if func_latex == "\\sin(x)" or func_latex == "\\cos(x)":
            options = [domain, "x \\neq 0", "x > 0", "x \\neq k\\pi (k \\in \\mathbb{Z})"]
        else:
            options = [domain, "所有实数", "x \\neq k\\pi (k \\in \\mathbb{Z})", "x > 0"]
    elif q_type == "range":
        question = f"函数 $f(x) = {func_latex}$ 的值域是？"
        correct = range_str
        options = [range_str, "[0, 1]", "[-2, 2]", "所有实数"]
    else:  # period
        question = f"函数 $f(x) = {func_latex}$ 的最小正周期是？"
        correct = period
        options = [period, "\\pi", "4\\pi", "\\frac{\\pi}{2}"]
    
    random.shuffle(options)
    correct_index = options.index(correct)
    answer_label = ["A", "B", "C", "D"][correct_index]
    
    return {
        "id": "backend-temp",
        "topic": "三角函数",
        "difficulty": "L1",
        "type": "choice",
        "question": question,
        "options": [f"${opt}$" for opt in options],
        "answer": answer_label,
        "solution": f"根据三角函数的基本性质，答案是 ${correct}$",
        "tags": ["三角函数", "基础概念"],
        "answerType": None,
        "answerExpr": None,
    }


def generate_trig_fill_l1() -> Dict:
    """
    生成第1章三角函数的L1填空题：简单三角值计算
    """
    angles_degrees = [0, 30, 45, 60, 90, 120, 135, 150, 180]
    angle_deg = random.choice(angles_degrees)
    angle_rad = sp.rad(angle_deg)
    
    func_type = random.choice(["sin", "cos", "tan"])
    
    if func_type == "sin":
        result = sp.sin(angle_rad)
        func_name = "\\sin"
    elif func_type == "cos":
        result = sp.cos(angle_rad)
        func_name = "\\cos"
    else:  # tan
        if angle_deg in [90, 270]:
            # tan(90°)不存在，跳过
            return generate_trig_fill_l1()
        result = sp.tan(angle_rad)
        func_name = "\\tan"
    
    result_simplified = sp.simplify(result)
    result_latex = sp.latex(result_simplified)
    result_float = float(result_simplified.evalf())
    
    question = f"计算：${func_name}({angle_deg}^\\circ) = ?$"
    
    return {
        "id": "backend-temp",
        "topic": "三角函数",
        "difficulty": "L1",
        "type": "fill",
        "question": question,
        "options": [],
        "answer": str(result_float),
        "solution": f"${func_name}({angle_deg}^\\circ) = {result_latex} \\approx {result_float:.4f}$",
        "tags": ["三角函数", "基础计算"],
        "answerType": "float",
        "answerExpr": result_latex,
    }


def generate_algebra_choice_l1() -> Dict:
    """
    生成第2章代数方程的L1选择题：判别式、根的个数
    """
    # 生成一元二次方程 ax^2 + bx + c = 0
    a = random.randint(1, 5)
    b = random.randint(-10, 10)
    c = random.randint(-10, 10)
    
    # 计算判别式
    delta = b**2 - 4*a*c
    
    if delta > 0:
        root_count = "两个不相等的实根"
    elif delta == 0:
        root_count = "两个相等的实根"
    else:
        root_count = "没有实根"
    
    question = f"方程 ${a}x^2 {b:+d}x {c:+d} = 0$ 有多少个实根？"
    
    options = ["两个不相等的实根", "两个相等的实根", "没有实根", "一个实根"]
    random.shuffle(options)
    correct_index = options.index(root_count)
    answer_label = ["A", "B", "C", "D"][correct_index]
    
    return {
        "id": "backend-temp",
        "topic": "代数与方程",
        "difficulty": "L1",
        "type": "choice",
        "question": question,
        "options": options,
        "answer": answer_label,
        "solution": f"判别式 $\\Delta = b^2 - 4ac = {b}^2 - 4 \\times {a} \\times {c} = {delta}$。因为 $\\Delta {'>' if delta > 0 else '=' if delta == 0 else '<'} 0$，所以方程有{root_count}。",
        "tags": ["代数", "一元二次方程", "判别式"],
        "answerType": None,
        "answerExpr": None,
    }


def generate_algebra_fill_l1() -> Dict:
    """
    生成第2章代数方程的L1填空题：方程求解
    """
    x = sp.symbols('x')
    
    # 生成简单的一元二次方程，确保有整数解
    root1 = random.randint(-5, 5)
    root2 = random.randint(-5, 5)
    
    # 构造方程 (x - root1)(x - root2) = 0
    eq = sp.expand((x - root1) * (x - root2))
    
    question = f"解方程：${sp.latex(eq)} = 0$，较小的根是？"
    
    smaller_root = min(root1, root2)
    
    return {
        "id": "backend-temp",
        "topic": "代数与方程",
        "difficulty": "L1",
        "type": "fill",
        "question": question,
        "options": [],
        "answer": str(smaller_root),
        "solution": f"方程可以因式分解为 $(x - {root1})(x - {root2}) = 0$，所以 $x = {root1}$ 或 $x = {root2}$。较小的根是 ${smaller_root}$。",
        "tags": ["代数", "一元二次方程", "求解"],
        "answerType": "integer",
        "answerExpr": str(smaller_root),
    }


def generate_problem(
    topic: str, 
    difficulty: str, 
    chapter: str | None = None,
    section: str | None = None,
    problem_type: str | None = None
) -> Dict:
    """
    根据主题、难度、章节生成题目
    
    Args:
        topic: 主题
        difficulty: 难度 (L1/L2/L3)
        chapter: 章节
        section: 节
        problem_type: 题型 (choice/fill/solution)，如果为None则根据难度自动选择
        
    Returns:
        题目字典
    """
    # 兼容旧难度体系
    if difficulty in ["基础", "进阶"]:
        difficulty = "L1" if difficulty == "基础" else "L2"
    
    # 如果没有指定题型，根据难度自动选择
    if problem_type is None:
        problem_type = get_problem_type_for_difficulty(difficulty)
    
    # 根据主题和难度选择生成器
    if topic == "三角函数" or (chapter and "三角函数" in chapter):
        if difficulty == "L1":
            if problem_type == "choice":
                result = generate_trig_choice_l1()
            elif problem_type == "fill":
                result = generate_trig_fill_l1()
            else:  # solution
                # 暂时用选择题代替
                result = generate_trig_choice_l1()
        else:
            # 其他难度暂时用L1代替
            result = generate_trig_choice_l1()
    elif topic == "代数与方程" or (chapter and "代数" in chapter):
        if difficulty == "L1":
            if problem_type == "choice":
                result = generate_algebra_choice_l1()
            elif problem_type == "fill":
                result = generate_algebra_fill_l1()
            else:  # solution
                result = generate_algebra_fill_l1()
        else:
            result = generate_algebra_choice_l1()
    else:
        # 默认使用导数题目
        result = generate_derivative_basic()
    
    # 添加章节和节信息
    if chapter:
        result["chapter"] = chapter
    if section:
        result["section"] = section
    
    return result



