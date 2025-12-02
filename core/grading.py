"""
SymPy-based grading logic for math problems.
Supports three problem types: choice, fill, solution
"""

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from typing import Tuple


def grade_choice(user_answer: str, correct_answer: str) -> Tuple[bool, str]:
    """
    判分选择题
    
    Args:
        user_answer: 用户选择的选项 (如 "A", "B", "C", "D")
        correct_answer: 正确选项
        
    Returns:
        (是否正确, 解释说明)
    """
    is_correct = user_answer.strip().upper() == correct_answer.strip().upper()
    
    if is_correct:
        explanation = f"正确！答案是 {correct_answer}"
    else:
        explanation = f"错误。正确答案是 {correct_answer}，您选择了 {user_answer}"
    
    return is_correct, explanation


def grade_fill_integer(user_answer: str, correct_answer: str) -> Tuple[bool, str]:
    """
    判分填空题（整数类型）
    
    Args:
        user_answer: 用户输入的答案
        correct_answer: 正确答案
        
    Returns:
        (是否正确, 解释说明)
    """
    try:
        user_int = int(user_answer.strip())
        correct_int = int(correct_answer.strip())
        is_correct = user_int == correct_int
        
        if is_correct:
            explanation = f"正确！答案是 {correct_int}"
        else:
            explanation = f"错误。正确答案是 {correct_int}，您的答案是 {user_int}"
        
        return is_correct, explanation
    except ValueError:
        return False, f"输入格式错误，请输入整数。正确答案是 {correct_answer}"


def grade_fill_float(user_answer: str, correct_answer: str, tolerance: float = 1e-6) -> Tuple[bool, str]:
    """
    判分填空题（浮点数类型）
    
    Args:
        user_answer: 用户输入的答案
        correct_answer: 正确答案
        tolerance: 允许的误差范围
        
    Returns:
        (是否正确, 解释说明)
    """
    try:
        user_float = float(user_answer.strip())
        correct_float = float(correct_answer.strip())
        is_correct = abs(user_float - correct_float) < tolerance
        
        if is_correct:
            explanation = f"正确！答案是 {correct_float}"
        else:
            explanation = f"错误。正确答案是 {correct_float}，您的答案是 {user_float}"
        
        return is_correct, explanation
    except ValueError:
        return False, f"输入格式错误，请输入数值。正确答案是 {correct_answer}"


def grade_fill_expr(user_answer: str, correct_answer_expr: str) -> Tuple[bool, str]:
    """
    判分填空题（表达式类型）
    
    使用 SymPy 检查两个表达式是否等价
    
    Args:
        user_answer: 用户输入的表达式字符串
        correct_answer_expr: 正确答案的表达式字符串
        
    Returns:
        (是否正确, 解释说明)
    """
    try:
        # 解析用户输入的表达式
        transformations = standard_transformations + (implicit_multiplication_application,)
        user_expr = parse_expr(user_answer.strip(), transformations=transformations)
        correct_expr = parse_expr(correct_answer_expr.strip(), transformations=transformations)
        
        # 检查表达式是否等价
        # 方法1：简化差值
        diff = sp.simplify(user_expr - correct_expr)
        is_correct = diff == 0
        
        if is_correct:
            explanation = f"正确！您的答案 {user_answer} 与标准答案等价"
        else:
            explanation = f"错误。您的答案与标准答案不等价。标准答案：{correct_answer_expr}"
        
        return is_correct, explanation
        
    except Exception as e:
        return False, f"表达式解析错误：{str(e)}。请检查输入格式。"


def grade_fill(
    user_answer: str, 
    correct_answer: str, 
    answer_type: str,
    correct_answer_expr: str | None = None
) -> Tuple[bool, str]:
    """
    填空题判分统一入口
    
    Args:
        user_answer: 用户答案
        correct_answer: 正确答案
        answer_type: 答案类型 ("integer", "float", "expr")
        correct_answer_expr: 正确答案的SymPy表达式（仅expr类型使用）
        
    Returns:
        (是否正确, 解释说明)
    """
    if answer_type == "integer":
        return grade_fill_integer(user_answer, correct_answer)
    elif answer_type == "float":
        return grade_fill_float(user_answer, correct_answer)
    elif answer_type == "expr":
        if correct_answer_expr is None:
            return False, "系统错误：缺少正确答案表达式"
        return grade_fill_expr(user_answer, correct_answer_expr)
    else:
        return False, f"未知的答案类型：{answer_type}"


def grade_solution(
    user_answer: str,
    correct_answer: str,
    answer_type: str,
    correct_answer_expr: str | None = None
) -> Tuple[bool, str]:
    """
    解答题判分（只判最终答案）
    
    解答题的判分逻辑与填空题相同，只检验最终答案
    
    Args:
        user_answer: 用户的最终答案
        correct_answer: 正确答案
        answer_type: 答案类型 ("integer", "float", "expr")
        correct_answer_expr: 正确答案的SymPy表达式（仅expr类型使用）
        
    Returns:
        (是否正确, 解释说明)
    """
    return grade_fill(user_answer, correct_answer, answer_type, correct_answer_expr)


def grade_problem(
    problem_type: str,
    user_answer: str,
    correct_answer: str,
    answer_type: str | None = None,
    correct_answer_expr: str | None = None
) -> Tuple[bool, str]:
    """
    通用判分函数
    
    Args:
        problem_type: 题型 ("choice", "fill", "solution")
        user_answer: 用户答案
        correct_answer: 正确答案
        answer_type: 答案类型（填空题和解答题使用）
        correct_answer_expr: 正确答案表达式（expr类型使用）
        
    Returns:
        (是否正确, 解释说明)
    """
    if problem_type == "choice":
        return grade_choice(user_answer, correct_answer)
    elif problem_type == "fill":
        if answer_type is None:
            return False, "系统错误：填空题缺少答案类型"
        return grade_fill(user_answer, correct_answer, answer_type, correct_answer_expr)
    elif problem_type == "solution":
        if answer_type is None:
            return False, "系统错误：解答题缺少答案类型"
        return grade_solution(user_answer, correct_answer, answer_type, correct_answer_expr)
    else:
        return False, f"未知的题型：{problem_type}"

