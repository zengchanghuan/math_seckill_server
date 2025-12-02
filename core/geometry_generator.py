"""
几何题目生成器（坐标化）

将平面几何问题转换为解析几何/坐标系中的问题，使用SymPy计算。
"""

import random
from typing import Dict
import sympy as sp
from sympy.geometry import Point, Triangle, Circle, Line, Segment


def generate_triangle_basic_l1() -> Dict:
    """
    生成L1三角形基础题：给定坐标，求边长、面积等
    """
    # 随机生成三角形的三个顶点（保证不共线）
    while True:
        x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
        x2, y2 = random.randint(-5, 5), random.randint(-5, 5)
        x3, y3 = random.randint(-5, 5), random.randint(-5, 5)

        # 检查是否共线
        det = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
        if det != 0:  # 不共线
            break

    A = Point(x1, y1)
    B = Point(x2, y2)
    C = Point(x3, y3)

    triangle = Triangle(A, B, C)

    # 随机选择题目类型
    question_type = random.choice(['side_length', 'perimeter', 'area'])

    if question_type == 'side_length':
        # 求某条边的长度
        side = random.choice(['AB', 'BC', 'AC'])
        if side == 'AB':
            length = float(A.distance(B).evalf())
            question = f"在坐标系中，三角形ABC的顶点坐标为 A({x1}, {y1})、B({x2}, {y2})、C({x3}, {y3})。求边AB的长度。"
        elif side == 'BC':
            length = float(B.distance(C).evalf())
            question = f"在坐标系中，三角形ABC的顶点坐标为 A({x1}, {y1})、B({x2}, {y2})、C({x3}, {y3})。求边BC的长度。"
        else:  # AC
            length = float(A.distance(C).evalf())
            question = f"在坐标系中，三角形ABC的顶点坐标为 A({x1}, {y1})、B({x2}, {y2})、C({x3}, {y3})。求边AC的长度。"

        solution = f"使用两点间距离公式 $d = \\sqrt{{(x_2 - x_1)^2 + (y_2 - y_1)^2}}$，计算得到长度为 ${length:.2f}$"

        return {
            "id": "backend-temp",
            "topic": "平面几何",
            "difficulty": "L1",
            "type": "fill",
            "question": question,
            "options": [],
            "answer": f"{length:.2f}",
            "solution": solution,
            "tags": ["平面几何", "三角形", "距离公式"],
            "answerType": "float",
            "answerExpr": str(length),
        }

    elif question_type == 'perimeter':
        # 求周长
        perimeter = float(triangle.perimeter.evalf())
        question = f"在坐标系中，三角形ABC的顶点坐标为 A({x1}, {y1})、B({x2}, {y2})、C({x3}, {y3})。求三角形的周长。"
        solution = f"分别计算三边长度后相加，周长为 ${perimeter:.2f}$"

        return {
            "id": "backend-temp",
            "topic": "平面几何",
            "difficulty": "L1",
            "type": "fill",
            "question": question,
            "options": [],
            "answer": f"{perimeter:.2f}",
            "solution": solution,
            "tags": ["平面几何", "三角形", "周长"],
            "answerType": "float",
            "answerExpr": str(perimeter),
        }

    else:  # area
        # 求面积
        area = float(triangle.area.evalf())
        question = f"在坐标系中，三角形ABC的顶点坐标为 A({x1}, {y1})、B({x2}, {y2})、C({x3}, {y3})。求三角形的面积。"
        solution = f"使用坐标法计算面积：$S = \\frac{{1}}{{2}}|x_1(y_2 - y_3) + x_2(y_3 - y_1) + x_3(y_1 - y_2)|$，面积为 ${area:.2f}$"

        return {
            "id": "backend-temp",
            "topic": "平面几何",
            "difficulty": "L1",
            "type": "fill",
            "question": question,
            "options": [],
            "answer": f"{area:.2f}",
            "solution": solution,
            "tags": ["平面几何", "三角形", "面积"],
            "answerType": "float",
            "answerExpr": str(area),
        }


def generate_circle_basic_l1() -> Dict:
    """
    生成L1圆的基础题：给定圆心和半径，判断点是否在圆上/内/外，或求圆的方程
    """
    # 随机生成圆心和半径
    h = random.randint(-5, 5)
    k = random.randint(-5, 5)
    r = random.randint(1, 5)

    center = Point(h, k)
    circle = Circle(center, r)

    question_type = random.choice(['point_on_circle', 'circle_equation'])

    if question_type == 'point_on_circle':
        # 生成一个在圆上的点
        angle = random.uniform(0, 2 * sp.pi)
        x = h + r * sp.cos(angle)
        y = k + r * sp.sin(angle)
        px = float(x.evalf())
        py = float(y.evalf())

        # 计算距离
        dist = sp.sqrt((px - h)**2 + (py - k)**2)
        dist_value = float(dist.evalf())

        question = f"圆心为 ({h}, {k})，半径为 {r} 的圆，点 ({px:.2f}, {py:.2f}) 到圆心的距离是多少？"
        solution = f"使用距离公式：$d = \\sqrt{{({px:.2f} - {h})^2 + ({py:.2f} - {k})^2}} = {dist_value:.2f}$"

        return {
            "id": "backend-temp",
            "topic": "平面几何",
            "difficulty": "L1",
            "type": "fill",
            "question": question,
            "options": [],
            "answer": f"{dist_value:.2f}",
            "solution": solution,
            "tags": ["平面几何", "圆", "距离"],
            "answerType": "float",
            "answerExpr": str(dist_value),
        }

    else:  # circle_equation
        # 求圆的标准方程的某个参数
        question = f"圆心为 ({h}, {k})，半径为 {r} 的圆，其标准方程为 $(x - a)^2 + (y - b)^2 = r^2$。请问 $a$ 的值是多少？"
        solution = f"圆的标准方程为 $(x - {h})^2 + (y - {k})^2 = {r}^2$，所以 $a = {h}$"

        return {
            "id": "backend-temp",
            "topic": "平面几何",
            "difficulty": "L1",
            "type": "fill",
            "question": question,
            "options": [],
            "answer": str(h),
            "solution": solution,
            "tags": ["平面几何", "圆", "标准方程"],
            "answerType": "integer",
            "answerExpr": str(h),
        }


def generate_line_basic_l1() -> Dict:
    """
    生成L1直线基础题：两点确定直线，求斜率或截距
    """
    # 随机生成两个点
    x1, y1 = random.randint(-5, 5), random.randint(-5, 5)
    x2, y2 = random.randint(-5, 5), random.randint(-5, 5)

    # 确保不是垂直线
    while x2 == x1:
        x2 = random.randint(-5, 5)

    A = Point(x1, y1)
    B = Point(x2, y2)
    line = Line(A, B)

    # 计算斜率
    slope = float(line.slope.evalf())

    question = f"经过点 A({x1}, {y1}) 和点 B({x2}, {y2}) 的直线，其斜率是多少？"
    solution = f"斜率公式：$k = \\frac{{y_2 - y_1}}{{x_2 - x_1}} = \\frac{{{y2} - {y1}}}{{{x2} - {x1}}} = {slope:.2f}$"

    return {
        "id": "backend-temp",
        "topic": "平面几何",
        "difficulty": "L1",
        "type": "fill",
        "question": question,
        "options": [],
        "answer": f"{slope:.2f}",
        "solution": solution,
        "tags": ["平面几何", "直线", "斜率"],
        "answerType": "float",
        "answerExpr": str(slope),
    }


def generate_geometry_problem(difficulty: str = "L1") -> Dict:
    """
    生成几何题目的统一入口

    Args:
        difficulty: 难度 (L1/L2/L3)

    Returns:
        题目字典
    """
    if difficulty == "L1":
        # L1: 三角形、圆、直线的基础题
        problem_type = random.choice(['triangle', 'circle', 'line'])

        if problem_type == 'triangle':
            return generate_triangle_basic_l1()
        elif problem_type == 'circle':
            return generate_circle_basic_l1()
        else:  # line
            return generate_line_basic_l1()
    else:
        # 其他难度暂时使用L1
        return generate_triangle_basic_l1()

