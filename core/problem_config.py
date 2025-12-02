"""
Configuration for problem generation.
Defines difficulty-type ratios and chapter-difficulty ratios.
"""

from typing import Dict

# 难度与题型配比
DIFFICULTY_TYPE_RATIO: Dict[str, Dict[str, float]] = {
    "L1": {
        "choice": 0.6,   # 选择题 60%
        "fill": 0.3,     # 填空题 30%
        "solution": 0.1  # 解答题 10%
    },
    "L2": {
        "choice": 0.3,   # 选择题 30%
        "fill": 0.4,     # 填空题 40%
        "solution": 0.3  # 解答题 30%
    },
    "L3": {
        "choice": 0.1,   # 选择题 10%
        "fill": 0.3,     # 填空题 30%
        "solution": 0.6  # 解答题 60%
    }
}

# 章节与难度配比
CHAPTER_DIFFICULTY_RATIO: Dict[str, Dict[str, float]] = {
    "第1章 三角函数": {
        "L1": 0.55,
        "L2": 0.35,
        "L3": 0.10
    },
    "第2章 代数与方程": {
        "L1": 0.50,
        "L2": 0.35,
        "L3": 0.15
    },
    "第3章 平面几何": {
        "L1": 0.45,
        "L2": 0.35,
        "L3": 0.20
    },
    "第4章 反三角函数": {
        "L1": 0.50,
        "L2": 0.35,
        "L3": 0.15
    },
    "第5章 排列与组合": {
        "L1": 0.50,
        "L2": 0.35,
        "L3": 0.15
    },
    "第6章 复数": {
        "L1": 0.50,
        "L2": 0.35,
        "L3": 0.15
    },
    "第7章 参数方程与极坐标方程": {
        "L1": 0.45,
        "L2": 0.35,
        "L3": 0.20
    }
}


def get_problem_type_for_difficulty(difficulty: str) -> str:
    """
    根据难度随机选择题型（按配比）

    Args:
        difficulty: 难度等级 ("L1", "L2", "L3")

    Returns:
        题型 ("choice", "fill", "solution")
    """
    import random

    if difficulty not in DIFFICULTY_TYPE_RATIO:
        difficulty = "L1"

    ratios = DIFFICULTY_TYPE_RATIO[difficulty]
    types = list(ratios.keys())
    weights = list(ratios.values())

    return random.choices(types, weights=weights)[0]

