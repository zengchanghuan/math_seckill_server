"""
答案检查器 - 支持符号表达式的答案比对
"""
import sympy as sp
from typing import Union


def normalize_answer(answer_str: str) -> Union[sp.Expr, str, float]:
    """
    规范化答案字符串
    支持多种等价形式：1, 1.0, 1/1 都应该被识别为相同答案
    """
    try:
        # 移除LaTeX格式符号和空格
        cleaned = answer_str.strip().replace('$', '').replace('\\\\', '\\').replace(' ', '')

        # 处理常见的等价形式
        # 1. 先尝试作为数值处理
        try:
            val = float(cleaned)
            # 如果是整数，转为整数形式
            if val.is_integer():
                return int(val)
            # 尝试转为有理数
            rational = sp.Rational(val).limit_denominator(1000)
            if abs(float(rational) - val) < 1e-10:
                return rational
            return val
        except ValueError:
            pass

        # 2. 尝试解析为SymPy表达式
        expr = sp.sympify(cleaned, rational=True)
        # 化简表达式
        simplified = sp.simplify(expr)
        return simplified
    except:
        # 如果都失败，返回清理后的字符串（用于选择题A/B/C/D）
        return answer_str.strip().upper()


def check_answer(student_answer: str, correct_answer: str, tolerance: float = 1e-10) -> bool:
    """
    检查学生答案是否正确

    支持：
    1. 符号表达式比对（如 sqrt(3)/2 vs 0.866）
    2. 字符串比对（如 A vs A）
    3. 数值比对（带容差）

    Args:
        student_answer: 学生答案
        correct_answer: 标准答案
        tolerance: 数值比对时的容差

    Returns:
        是否正确
    """
    # 规范化答案
    student_expr = normalize_answer(student_answer)
    correct_expr = normalize_answer(correct_answer)

    # 0. 如果都是整数或浮点数，直接数值比对
    if isinstance(student_expr, (int, float)) and isinstance(correct_expr, (int, float)):
        return abs(float(student_expr) - float(correct_expr)) < tolerance

    # 1. 如果都是SymPy表达式，进行符号比对
    if isinstance(student_expr, sp.Expr) and isinstance(correct_expr, sp.Expr):
        try:
            # 化简差值，如果为0则相等
            diff = sp.simplify(student_expr - correct_expr)
            if diff == 0:
                return True

            # 数值比对（如果都能数值化）
            try:
                student_val = float(student_expr.evalf())
                correct_val = float(correct_expr.evalf())
                return abs(student_val - correct_val) < tolerance
            except:
                pass
        except:
            pass

    # 2. 如果有一个是SymPy表达式，另一个是数值/字符串
    if isinstance(student_expr, sp.Expr):
        try:
            student_val = float(student_expr.evalf())
            if isinstance(correct_expr, str):
                try:
                    correct_val = float(correct_expr)
                    return abs(student_val - correct_val) < tolerance
                except:
                    pass
        except:
            pass

    if isinstance(correct_expr, sp.Expr):
        try:
            correct_val = float(correct_expr.evalf())
            if isinstance(student_expr, str):
                try:
                    student_val = float(student_expr)
                    return abs(student_val - correct_val) < tolerance
                except:
                    pass
        except:
            pass

    # 3. 字符串比对（选择题的A/B/C/D）
    if isinstance(student_expr, str) and isinstance(correct_expr, str):
        return student_expr == correct_expr

    return False


def latex_to_sympy(latex_str: str) -> Union[sp.Expr, None]:
    """
    将LaTeX字符串转换为SymPy表达式
    """
    try:
        from sympy.parsing.latex import parse_latex
        return parse_latex(latex_str)
    except:
        return None


def format_answer_latex(expr: Union[sp.Expr, float, int, str]) -> str:
    """
    将答案格式化为LaTeX字符串

    优先使用符号形式，避免浮点数
    """
    if isinstance(expr, (sp.Expr, sp.Rational, sp.Integer)):
        return sp.latex(expr)
    elif isinstance(expr, float):
        # 尝试转换为有理数
        try:
            rational = sp.Rational(expr).limit_denominator(1000)
            if abs(float(rational) - expr) < 1e-6:
                return sp.latex(rational)
        except:
            pass
        return str(expr)
    else:
        return str(expr)

