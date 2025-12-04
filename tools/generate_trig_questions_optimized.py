"""
三角函数题目生成器 - 优化版
严格使用特殊角度值，全部符号表示，无浮点数
"""
import json
import random
import hashlib

# ========== 特殊角度三角函数值表（符号形式）==========

SPECIAL_ANGLES = {
    # 角度: (弧度, sin值, cos值, tan值)
    0: {
        'degree': '0',
        'radian': '0',
        'sin': '0',
        'cos': '1',
        'tan': '0'
    },
    30: {
        'degree': '30',
        'radian': '\\frac{\\pi}{6}',
        'sin': '\\frac{1}{2}',
        'cos': '\\frac{\\sqrt{3}}{2}',
        'tan': '\\frac{\\sqrt{3}}{3}'
    },
    45: {
        'degree': '45',
        'radian': '\\frac{\\pi}{4}',
        'sin': '\\frac{\\sqrt{2}}{2}',
        'cos': '\\frac{\\sqrt{2}}{2}',
        'tan': '1'
    },
    60: {
        'degree': '60',
        'radian': '\\frac{\\pi}{3}',
        'sin': '\\frac{\\sqrt{3}}{2}',
        'cos': '\\frac{1}{2}',
        'tan': '\\sqrt{3}'
    },
    90: {
        'degree': '90',
        'radian': '\\frac{\\pi}{2}',
        'sin': '1',
        'cos': '0',
        'tan': None  # 不存在
    },
    120: {
        'degree': '120',
        'radian': '\\frac{2\\pi}{3}',
        'sin': '\\frac{\\sqrt{3}}{2}',
        'cos': '-\\frac{1}{2}',
        'tan': '-\\sqrt{3}'
    },
    135: {
        'degree': '135',
        'radian': '\\frac{3\\pi}{4}',
        'sin': '\\frac{\\sqrt{2}}{2}',
        'cos': '-\\frac{\\sqrt{2}}{2}',
        'tan': '-1'
    },
    150: {
        'degree': '150',
        'radian': '\\frac{5\\pi}{6}',
        'sin': '\\frac{1}{2}',
        'cos': '-\\frac{\\sqrt{3}}{2}',
        'tan': '-\\frac{\\sqrt{3}}{3}'
    },
    180: {
        'degree': '180',
        'radian': '\\pi',
        'sin': '0',
        'cos': '-1',
        'tan': '0'
    },
    210: {
        'degree': '210',
        'radian': '\\frac{7\\pi}{6}',
        'sin': '-\\frac{1}{2}',
        'cos': '-\\frac{\\sqrt{3}}{2}',
        'tan': '\\frac{\\sqrt{3}}{3}'
    },
    225: {
        'degree': '225',
        'radian': '\\frac{5\\pi}{4}',
        'sin': '-\\frac{\\sqrt{2}}{2}',
        'cos': '-\\frac{\\sqrt{2}}{2}',
        'tan': '1'
    },
    240: {
        'degree': '240',
        'radian': '\\frac{4\\pi}{3}',
        'sin': '-\\frac{\\sqrt{3}}{2}',
        'cos': '-\\frac{1}{2}',
        'tan': '\\sqrt{3}'
    },
    270: {
        'degree': '270',
        'radian': '\\frac{3\\pi}{2}',
        'sin': '-1',
        'cos': '0',
        'tan': None  # 不存在
    },
    300: {
        'degree': '300',
        'radian': '\\frac{5\\pi}{3}',
        'sin': '-\\frac{\\sqrt{3}}{2}',
        'cos': '\\frac{1}{2}',
        'tan': '-\\sqrt{3}'
    },
    315: {
        'degree': '315',
        'radian': '\\frac{7\\pi}{4}',
        'sin': '-\\frac{\\sqrt{2}}{2}',
        'cos': '\\frac{\\sqrt{2}}{2}',
        'tan': '-1'
    },
    330: {
        'degree': '330',
        'radian': '\\frac{11\\pi}{6}',
        'sin': '-\\frac{1}{2}',
        'cos': '\\frac{\\sqrt{3}}{2}',
        'tan': '-\\frac{\\sqrt{3}}{3}'
    },
    360: {
        'degree': '360',
        'radian': '2\\pi',
        'sin': '0',
        'cos': '1',
        'tan': '0'
    }
}

# 三角函数值池（用于生成干扰项）
TRIG_VALUE_POOL = [
    '0',
    '\\frac{1}{2}',
    '\\frac{\\sqrt{2}}{2}',
    '\\frac{\\sqrt{3}}{2}',
    '1',
    '-\\frac{1}{2}',
    '-\\frac{\\sqrt{2}}{2}',
    '-\\frac{\\sqrt{3}}{2}',
    '-1',
    '\\frac{\\sqrt{3}}{3}',
    '\\sqrt{3}',
    '-\\frac{\\sqrt{3}}{3}',
    '-\\sqrt{3}',
]

# 周期值
PERIOD_VALUES = {
    'sin': '2\\pi',
    'cos': '2\\pi',
    'tan': '\\pi',
}

_used_ids = set()

def generate_unique_id(content: str) -> str:
    """生成唯一ID"""
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    unique_id = f"trig_{content_hash}"
    counter = 0
    while unique_id in _used_ids:
        counter += 1
        unique_id = f"trig_{content_hash}_{counter}"
    _used_ids.add(unique_id)
    return unique_id

def generate_distinct_options(correct_answer, pool, n=4):
    """生成不重复的选项"""
    options = [correct_answer]
    available = [opt for opt in pool if opt != correct_answer]

    # 随机选择干扰项
    selected = random.sample(available, min(n-1, len(available)))
    options.extend(selected)

    # 确保恰好n个且不重复
    options = list(dict.fromkeys(options))
    while len(options) < n:
        # 添加更多干扰项
        extra = random.choice([opt for opt in pool if opt not in options])
        options.append(extra)

    options = options[:n]
    random.shuffle(options)

    return options

def generate_trig_value_question(use_radian=False):
    """生成三角函数求值题"""
    # 随机选择角度（排除90和270度的tan）
    angle_key = random.choice(list(SPECIAL_ANGLES.keys()))
    func = random.choice(['sin', 'cos', 'tan'])

    angle_data = SPECIAL_ANGLES[angle_key]
    answer = angle_data[func]

    # 如果tan不存在，重新生成
    if answer is None:
        return generate_trig_value_question(use_radian)

    # 选择角度表示（度或弧度）
    angle_str = angle_data['radian'] if use_radian else f"{angle_data['degree']}^\\circ"

    question = f"计算: ${func}({angle_str}) = ?$"

    # 生成选项
    options = generate_distinct_options(answer, TRIG_VALUE_POOL, 4)
    answer_letter = ['A', 'B', 'C', 'D'][options.index(answer)]

    solution = f"${func}({angle_str}) = {answer}$"

    return {
        'questionId': generate_unique_id(question),
        'topic': '三角函数',
        'difficulty': 'L1',
        'type': 'choice',
        'question': question,
        'answer': answer_letter,
        'options': options,
        'solution': solution,
        'tags': ['三角函数', '特殊值'],
        'knowledgePoints': ['三角函数特殊值'],
        'abilityTags': ['计算'],
    }

def generate_trig_equation_question():
    """生成三角方程题"""
    # 简单的三角方程: sin(x) = k 或 cos(x) = k
    func = random.choice(['sin', 'cos'])
    target_value = random.choice(['\\frac{1}{2}', '\\frac{\\sqrt{2}}{2}', '\\frac{\\sqrt{3}}{2}', '1', '0'])

    # 找到满足条件的角度
    matching_angles = []
    for angle_key, data in SPECIAL_ANGLES.items():
        if data[func] == target_value and 0 <= angle_key <= 360:
            matching_angles.append(data['degree'])

    if not matching_angles:
        return generate_trig_equation_question()

    correct_angle = matching_angles[0]

    question = f"若 ${func}(x) = {target_value}$，且 $0 \\leq x \\leq 360^\\circ$，则 $x$ 可能等于？"

    # 生成角度选项
    angle_pool = [f"{data['degree']}^\\circ" for data in SPECIAL_ANGLES.values() if data['degree'] not in ['', '0']]
    options = generate_distinct_options(f"{correct_angle}^\\circ", angle_pool, 4)
    answer_letter = ['A', 'B', 'C', 'D'][options.index(f"{correct_angle}^\\circ")]

    solution = f"根据三角函数定义，${func}({correct_angle}^\\circ) = {target_value}$"

    return {
        'questionId': generate_unique_id(question),
        'topic': '三角函数',
        'difficulty': 'L2',
        'type': 'choice',
        'question': question,
        'answer': answer_letter,
        'options': options,
        'solution': solution,
        'tags': ['三角函数', '三角方程'],
        'knowledgePoints': ['三角方程'],
        'abilityTags': ['分析', '计算'],
    }

def generate_trig_period_question():
    """生成三角函数周期题"""
    func = random.choice(['sin', 'cos', 'tan'])
    coeff = random.choice([1, 2, 3, 4])

    period = PERIOD_VALUES[func]

    if coeff == 1:
        question = f"函数 $f(x) = \\{func}(x)$ 的最小正周期是？"
        answer = period
    else:
        question = f"函数 $f(x) = \\{func}({coeff}x)$ 的最小正周期是？"
        # T' = T / |coeff|
        if period == '2\\pi':
            if coeff == 2:
                answer = '\\pi'
            elif coeff == 3:
                answer = '\\frac{2\\pi}{3}'
            elif coeff == 4:
                answer = '\\frac{\\pi}{2}'
        else:  # period == '\\pi'
            if coeff == 2:
                answer = '\\frac{\\pi}{2}'
            elif coeff == 3:
                answer = '\\frac{\\pi}{3}'
            elif coeff == 4:
                answer = '\\frac{\\pi}{4}'

    # 周期选项池
    period_pool = ['\\pi', '2\\pi', '\\frac{\\pi}{2}', '\\frac{\\pi}{3}', '\\frac{\\pi}{4}', '\\frac{2\\pi}{3}', '4\\pi']
    options = generate_distinct_options(answer, period_pool, 4)
    answer_letter = ['A', 'B', 'C', 'D'][options.index(answer)]

    solution = f"三角函数 $\\{func}(x)$ 的周期为 ${period}$，因此 $\\{func}({coeff}x)$ 的周期为 $\\frac{{{period}}}{{{coeff}}} = {answer}$"

    return {
        'questionId': generate_unique_id(question),
        'topic': '三角函数',
        'difficulty': 'L2',
        'type': 'choice',
        'question': question,
        'answer': answer_letter,
        'options': options,
        'solution': solution,
        'tags': ['三角函数', '周期'],
        'knowledgePoints': ['三角函数周期'],
        'abilityTags': ['分析'],
    }

def main():
    """生成三角函数题目"""
    questions = []

    print('开始生成三角函数题目...\n')

    # 生成50道求值题（度数制）
    print('1. 生成求值题（度数制）...')
    for _ in range(30):
        q = generate_trig_value_question(use_radian=False)
        questions.append(q)

    # 生成20道求值题（弧度制）
    print('2. 生成求值题（弧度制）...')
    for _ in range(20):
        q = generate_trig_value_question(use_radian=True)
        questions.append(q)

    # 生成30道三角方程题
    print('3. 生成三角方程题...')
    for _ in range(30):
        q = generate_trig_equation_question()
        questions.append(q)

    # 生成20道周期题
    print('4. 生成周期题...')
    for _ in range(20):
        q = generate_trig_period_question()
        questions.append(q)

    print(f'\n✅ 共生成 {len(questions)} 道三角函数题目')

    # 保存
    with open('../data/trig_questions_optimized.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    print('✅ 已保存到 trig_questions_optimized.json')

    # 统计
    print('\n📊 题目统计：')
    print(f'  - 求值题：50道')
    print(f'  - 三角方程：30道')
    print(f'  - 周期题：20道')
    print(f'  - 全部使用特殊角度值')
    print(f'  - 全部使用符号表示')
    print(f'  - 无浮点数')

if __name__ == '__main__':
    main()

