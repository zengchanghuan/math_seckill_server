"""
题型模板库
定义各类题目的生成模板，确保生成的题目符合真题风格
"""
from dataclasses import dataclass
from typing import List, Dict, Callable, Any
from enum import Enum


class TemplateCategory(str, Enum):
    """模板类别"""
    TRIGONOMETRY = "trigonometry"  # 三角函数
    ALGEBRA = "algebra"            # 代数
    CALCULUS = "calculus"          # 微积分
    GEOMETRY = "geometry"          # 几何
    COMBINATORICS = "combinatorics" # 排列组合
    COMPLEX = "complex"            # 复数


@dataclass
class ProblemTemplate:
    """题目模板"""
    templateId: str
    category: TemplateCategory
    name: str
    description: str

    # 知识点和能力标签
    knowledgePoints: List[str]
    abilityTags: List[str]

    # 适用难度
    difficulties: List[str]  # ["L1", "L2", "L3"]

    # 适用题型
    questionTypes: List[str]  # ["choice", "fill", "solution"]

    # 生成函数（接受难度和题型，返回题目数据）
    generator: Callable[[str, str], Dict[str, Any]]

    # 模板示例
    examples: List[str] = None


# ========== 三角函数模板 ==========

def generate_trig_domain_range(difficulty: str, qtype: str) -> Dict[str, Any]:
    """
    模板：三角函数的定义域和值域
    真题原型：考察基本三角函数的性质
    """
    import sympy as sp
    import random

    x = sp.Symbol('x')

    if difficulty == "L1":
        # 基础：单一三角函数
        funcs = {
            "sin": (sp.sin(x), "所有实数", "[-1, 1]"),
            "cos": (sp.cos(x), "所有实数", "[-1, 1]"),
            "tan": (sp.tan(x), r"$x \neq \frac{\pi}{2} + k\pi (k \in \mathbb{Z})$", "所有实数"),
        }

        func_name, (func, domain, range_val) = random.choice(list(funcs.items()))

        if qtype == "choice":
            question = f"函数 $f(x) = {sp.latex(func)}$ 的定义域是？"

            # 正确答案
            correct = domain

            # 干扰项
            options = [
                r"$x > 0$",
                "所有实数",
                r"$x \neq k\pi (k \in \mathbb{Z})$",
                correct
            ]
            random.shuffle(options)
            correct_index = chr(65 + options.index(correct))  # A, B, C, D

            return {
                "question": question,
                "options": options,
                "answer": correct_index,
                "solution": f"根据三角函数的基本性质，答案是 {correct}",
                "knowledgePoints": ["三角函数", "定义域"],
                "abilityTags": ["memory", "understand"]
            }

    # 更多难度和题型的生成逻辑...
    return {}


def generate_trig_identity(difficulty: str, qtype: str) -> Dict[str, Any]:
    """
    模板：三角恒等式化简
    真题原型：两角和差公式、倍角公式
    """
    import sympy as sp
    import random

    x = sp.Symbol('x')

    if difficulty == "L2":
        # 中档：两角和差公式
        formulas = [
            (sp.sin(x + sp.pi/4), sp.simplify(sp.sin(x + sp.pi/4)), "sin(x + π/4)"),
            (sp.cos(2*x), sp.cos(x)**2 - sp.sin(x)**2, "cos(2x)"),
        ]

        original, simplified, name = random.choice(formulas)

        if qtype == "fill":
            question = f"化简 ${sp.latex(original)}$ ="
            answer_expr = sp.latex(simplified)

            return {
                "question": question,
                "answer": answer_expr,
                "answerType": "expr",
                "answerExpr": str(simplified),
                "solution": f"利用{name}的展开公式，得到 ${answer_expr}$",
                "knowledgePoints": ["三角恒等式", "化简"],
                "abilityTags": ["apply", "analyze"]
            }

    return {}


# ========== 代数模板 ==========

def generate_quadratic_discriminant(difficulty: str, qtype: str) -> Dict[str, Any]:
    """
    模板：一元二次方程的判别式
    真题原型：判断根的个数
    """
    import sympy as sp
    import random

    x = sp.Symbol('x')

    if difficulty == "L1":
        # 基础：给定系数，判断根的个数
        a, b, c = random.randint(1, 5), random.randint(-10, 10), random.randint(-10, 10)

        equation = a*x**2 + b*x + c
        discriminant = b**2 - 4*a*c

        if discriminant > 0:
            root_count = 2
            desc = "两个不相等的实根"
        elif discriminant == 0:
            root_count = 1
            desc = "两个相等的实根"
        else:
            root_count = 0
            desc = "无实根"

        if qtype == "choice":
            question = f"方程 ${sp.latex(equation)} = 0$ 的实根个数是？"

            options = ["0个", "1个", "2个", "无穷多个"]
            correct = f"{root_count}个" if root_count <= 2 else "无穷多个"
            correct_index = chr(65 + options.index(correct))

            return {
                "question": question,
                "options": options,
                "answer": correct_index,
                "solution": f"判别式 Δ = {b}² - 4×{a}×{c} = {discriminant}，因此{desc}",
                "knowledgePoints": ["一元二次方程", "判别式"],
                "abilityTags": ["apply"]
            }

    return {}


# ========== 模板注册表 ==========

TEMPLATE_REGISTRY = {
    # 三角函数
    "trig_domain_range": ProblemTemplate(
        templateId="trig_domain_range",
        category=TemplateCategory.TRIGONOMETRY,
        name="三角函数的定义域和值域",
        description="考察基本三角函数的定义域和值域",
        knowledgePoints=["三角函数", "定义域", "值域"],
        abilityTags=["memory", "understand"],
        difficulties=["L1"],
        questionTypes=["choice"],
        generator=generate_trig_domain_range,
        examples=[
            "函数 f(x) = tan(x) 的定义域是？",
            "函数 f(x) = sin(x) 的值域是？"
        ]
    ),

    "trig_identity": ProblemTemplate(
        templateId="trig_identity",
        category=TemplateCategory.TRIGONOMETRY,
        name="三角恒等式化简",
        description="利用两角和差公式、倍角公式化简三角表达式",
        knowledgePoints=["三角恒等式", "化简"],
        abilityTags=["apply", "analyze"],
        difficulties=["L2"],
        questionTypes=["fill"],
        generator=generate_trig_identity
    ),

    # 代数
    "quadratic_discriminant": ProblemTemplate(
        templateId="quadratic_discriminant",
        category=TemplateCategory.ALGEBRA,
        name="一元二次方程判别式",
        description="利用判别式判断根的个数和性质",
        knowledgePoints=["一元二次方程", "判别式"],
        abilityTags=["apply"],
        difficulties=["L1", "L2"],
        questionTypes=["choice", "fill"],
        generator=generate_quadratic_discriminant
    ),
}


def get_template(template_id: str) -> ProblemTemplate:
    """获取模板"""
    return TEMPLATE_REGISTRY.get(template_id)


def list_templates(
    category: TemplateCategory = None,
    difficulty: str = None,
    question_type: str = None
) -> List[ProblemTemplate]:
    """列出符合条件的模板"""
    templates = list(TEMPLATE_REGISTRY.values())

    if category:
        templates = [t for t in templates if t.category == category]

    if difficulty:
        templates = [t for t in templates if difficulty in t.difficulties]

    if question_type:
        templates = [t for t in templates if question_type in t.questionTypes]

    return templates


def generate_from_template(
    template_id: str,
    difficulty: str,
    question_type: str
) -> Dict[str, Any]:
    """
    从模板生成题目

    Args:
        template_id: 模板ID
        difficulty: 难度 (L1/L2/L3)
        question_type: 题型 (choice/fill/solution)

    Returns:
        题目数据字典
    """
    template = get_template(template_id)
    if not template:
        raise ValueError(f"模板 {template_id} 不存在")

    if difficulty not in template.difficulties:
        raise ValueError(f"模板 {template_id} 不支持难度 {difficulty}")

    if question_type not in template.questionTypes:
        raise ValueError(f"模板 {template_id} 不支持题型 {question_type}")

    # 调用生成函数
    problem_data = template.generator(difficulty, question_type)

    # 添加模板元信息
    problem_data["templateId"] = template_id
    problem_data.setdefault("knowledgePoints", template.knowledgePoints)
    problem_data.setdefault("abilityTags", template.abilityTags)

    return problem_data







